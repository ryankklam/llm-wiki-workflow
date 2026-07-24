#!/usr/bin/env python3
"""
视频转LLM Wiki 工作流主程序
支持平台: 小红书、抖音、Bilibili

使用方法:
    python main.py "http://xhslink.com/o/4doVxyjRF2c"
    python main.py "https://www.bilibili.com/video/BV1xx411c7mD"
    python main.py --batch urls.txt
    python main.py --skip-download --audio-path ./audio.mp3
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules import (
    VideoDownloader,
    AudioExtractor,
    AudioTranscriber,
    GitHubUploader,
    load_config,
    setup_logging,
    WorkflowError,
)
from modules.transcriber import SubtitleSegment
from skills.subtitle_corrector.correct_subtitle import SubtitleCorrector
from skills.wiki_ingestor.ingest_to_wiki import WikiIngestor
from skills.llm_wiki_adapter import LLMWikiAdapter
from skills.skill_guided_ingestor import SkillGuidedIngestor

logger = logging.getLogger(__name__)


class VideoToLLMWikiWorkflow:
    """视频转LLM Wiki工作流（支持小红书、抖音、Bilibili）"""
    
    def __init__(self, config: dict = None, internal_corrector=None):
        """
        初始化工作流
        
        Args:
            config: 配置字典，如果为None则自动加载
            internal_corrector: INTERNAL模式的字幕校正回调函数。
                签名: (subtitle_text: str, video_title: str, video_description: str) -> str
                仅在 correction.mode 为 "INTERNAL" 时使用。
        """
        self.config = config or load_config()
        setup_logging(self.config)
        
        # 初始化各模块
        self.downloader = VideoDownloader(self.config)
        self.audio_extractor = AudioExtractor(self.config)
        self.transcriber = AudioTranscriber(self.config)
        self.corrector = SubtitleCorrector(
            self.config,
            internal_corrector=internal_corrector
        )
        self.uploader = GitHubUploader(self.config)
        
        # 根据 ingestion.mode 选择 Ingestor
        ingestion_mode = self.config.get('ingestion', {}).get('mode', 'SKILL_GUIDED')
        
        if ingestion_mode == 'SKILL_GUIDED':
            self.ingestor = SkillGuidedIngestor(self.config)
            self.ingestion_mode = 'SKILL_GUIDED'
            logger.info(f"Ingestion模式: SKILL_GUIDED (LLM按SKILL.md执行)")
        elif ingestion_mode == 'PROGRAMMATIC':
            # PROGRAMMATIC模式使用LLMWikiAdapter
            prog_config = self.config.get('ingestion', {}).get('programmatic', {})
            # 把programmatic配置映射到LLMWikiAdapter期望的格式
            merged_config = dict(self.config)
            merged_config['ingestion'] = {'custom_skill': prog_config}
            self.ingestor = LLMWikiAdapter(merged_config)
            self.ingestion_mode = 'PROGRAMMATIC'
            logger.info(f"Ingestion模式: PROGRAMMATIC (Python程序自动处理)")
        else:
            self.ingestor = WikiIngestor(self.config)
            self.ingestion_mode = 'BUILTIN'
            logger.info(f"Ingestion模式: BUILTIN (内置WikiIngestor)")
        
        correction_mode = self.config.get('correction', {}).get('mode', 'EXTERNAL')
        logger.info(f"工作流初始化完成，字幕校正: {correction_mode}, Ingestion: {ingestion_mode}")
    
    def process_video(self, 
                      url: str,
                      skip_download: bool = False,
                      video_path: str = None,
                      audio_path: str = None,
                      keep_temp: bool = False) -> dict:
        """
        处理单个视频
        
        Args:
            url: 视频链接
            skip_download: 是否跳过下载（使用本地文件）
            video_path: 本地视频文件路径（如果skip_download为True）
            audio_path: 本地音频文件路径（如果skip_download为True）
            keep_temp: 是否保留临时文件
            
        Returns:
            处理结果字典
        """
        result = {
            'url': url,
            'success': False,
            'video_info': None,
            'subtitle_segments': None,
            'corrected_result': None,
            'github_urls': None,
            'ingestion_result': None,
            'error': None
        }
        
        temp_files = []  # 跟踪临时文件以便清理
        
        try:
            # ========== 步骤1: 下载视频 ==========
            if skip_download and audio_path:
                logger.info(f"跳过下载，使用本地音频: {audio_path}")
                # 提取视频信息（如果可能）
                try:
                    result['video_info'] = self.downloader.extract_video_info(url)
                except:
                    result['video_info'] = {'title': 'Local Audio', 'original_url': url}
            elif skip_download and video_path:
                logger.info(f"跳过下载，使用本地视频: {video_path}")
                result['video_info'] = {'title': Path(video_path).stem, 'original_url': url}
            else:
                logger.info(f"步骤1/6: 下载视频 - {url}")
                video_file, video_info = self.downloader.download_video(url)
                result['video_info'] = video_info
                video_path = video_file
                temp_files.append(video_file)
            
            # ========== 步骤2: 提取音频 ==========
            if not audio_path:
                logger.info("步骤2/6: 提取音频")
                audio_path = self.audio_extractor.extract_audio(video_path)
                temp_files.append(audio_path)
            
            # ========== 步骤3: 转录音频 ==========
            logger.info("步骤3/6: 转录音频为字幕")
            segments, full_text = self.transcriber.transcribe(audio_path)
            result['subtitle_segments'] = segments
            
            # 保存原始字幕文件
            base_name = self._generate_base_name(result['video_info'])
            raw_files = self.transcriber.save_all_formats(
                segments, full_text, base_name, result['video_info']
            )
            
            # ========== 步骤4: LLM校正 ==========
            logger.info("步骤4/6: LLM校正字幕")
            correction_result = self.corrector.correct_segments(
                segments, result['video_info']
            )
            result['corrected_result'] = correction_result
            
            # 保存校正后的Markdown
            corrected_md_path = Path(self.config.get('paths', {}).get('output_dir', './storage/output')) / f"{base_name}_corrected.md"
            self.corrector.save_corrected_markdown(
                correction_result, result['video_info'], str(corrected_md_path)
            )
            
            # ========== 步骤5: 上传到GitHub ==========
            logger.info("步骤5/6: 上传到GitHub")
            github_urls = self.uploader.upload_subtitle_package(
                result['video_info'],
                str(corrected_md_path),
                raw_files
            )
            result['github_urls'] = github_urls
            
            # 更新索引
            self.uploader.update_index_file(
                result['video_info'],
                github_urls.get('corrected_md', ''),
                category=None  # 可以自动检测或手动指定
            )
            
            # ========== 步骤6: Ingest到Wiki ==========
            logger.info(f"步骤6/6: Ingest到LLM Wiki (模式: {self.ingestion_mode})")
            
            if self.ingestion_mode == 'SKILL_GUIDED':
                # SKILL_GUIDED模式：准备数据，返回上下文供LLM执行SKILL.md ingest
                prepare_result = self.ingestor.prepare(
                    video_path=video_path,
                    corrected_content=correction_result.corrected_text,
                    video_info=result['video_info']
                )
                if prepare_result.success:
                    # 获取当前wiki状态，供LLM参考
                    ingest_context = self.ingestor.get_ingest_context()
                    result['ingestion_result'] = {
                        'mode': 'SKILL_GUIDED',
                        'status': 'prepared',
                        'wiki_root': prepare_result.wiki_root,
                        'video_path': prepare_result.video_path,
                        'subtitle_path': prepare_result.subtitle_path,
                        'video_info': prepare_result.video_info,
                        'corrected_content': prepare_result.corrected_content,
                        'ingest_context': ingest_context,
                        'message': '数据已准备完成，等待LLM按SKILL.md执行ingest后调用commit_and_push()'
                    }
                    logger.info("[SKILL_GUIDED] 数据准备完成，等待LLM执行SKILL.md ingest")
                else:
                    raise WorkflowError(f"SKILL_GUIDED prepare失败: {prepare_result.error}")
            
            elif self.ingestion_mode == 'PROGRAMMATIC':
                # PROGRAMMATIC模式：Python程序自动处理
                ingestion_result = self.ingestor.ingest(
                    video_path=video_path,
                    subtitle_content=full_text,
                    video_info=result['video_info'],
                    corrected_content=correction_result.corrected_text
                )
                result['ingestion_result'] = ingestion_result
            
            else:
                # BUILTIN模式：内置WikiIngestor
                ingestion_result = self.ingestor.ingest(
                    correction_result.corrected_text,
                    result['video_info'],
                    github_urls.get('corrected_md', '')
                )
                result['ingestion_result'] = ingestion_result
            
            result['success'] = True
            logger.info("工作流执行成功！")
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}")
            result['error'] = str(e)
            result['success'] = False
        
        finally:
            # 清理临时文件
            if not keep_temp:
                self._cleanup_temp_files(temp_files)
        
        return result
    
    def process_batch(self, 
                      urls: List[str],
                      keep_temp: bool = False) -> List[dict]:
        """
        批量处理视频
        
        Args:
            urls: 视频链接列表
            keep_temp: 是否保留临时文件
            
        Returns:
            处理结果列表
        """
        results = []
        total = len(urls)
        
        for i, url in enumerate(urls, 1):
            logger.info(f"处理第 {i}/{total} 个视频: {url}")
            result = self.process_video(url, keep_temp=keep_temp)
            results.append(result)
            
            # 打印处理结果
            if result['success']:
                logger.info(f"✓ 视频 {i} 处理成功")
                if result.get('github_urls'):
                    logger.info(f"  GitHub链接: {result['github_urls'].get('corrected_md', 'N/A')}")
            else:
                logger.error(f"✗ 视频 {i} 处理失败: {result.get('error', 'Unknown error')}")
        
        # 打印汇总
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"批量处理完成: {success_count}/{total} 成功")
        
        return results
    
    def _generate_base_name(self, video_info: dict) -> str:
        """
        生成基础文件名
        
        Args:
            video_info: 视频信息
            
        Returns:
            基础文件名
        """
        from modules.utils import sanitize_filename
        from datetime import datetime
        
        title = video_info.get('title', 'unknown')
        video_id = video_info.get('id', '')[:8]
        date_str = datetime.now().strftime('%Y%m%d')
        
        safe_title = sanitize_filename(title)[:30]
        return f"{date_str}_{safe_title}_{video_id}"
    
    def _cleanup_temp_files(self, temp_files: List[str]):
        """
        清理临时文件
        
        Args:
            temp_files: 临时文件路径列表
        """
        for file_path in temp_files:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    logger.debug(f"已删除临时文件: {file_path}")
            except Exception as e:
                logger.warning(f"删除临时文件失败 {file_path}: {e}")


def read_urls_from_file(file_path: str) -> List[str]:
    """
    从文件读取URL列表
    
    Args:
        file_path: 文件路径
        
    Returns:
        URL列表
    """
    urls = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def print_result(result: dict):
    """
    打印处理结果
    
    Args:
        result: 处理结果字典
    """
    print("\n" + "="*60)
    if result['success']:
        print("✓ 处理成功！")
        print(f"  标题: {result['video_info'].get('title', 'N/A')}")
        print(f"  作者: {result['video_info'].get('uploader', 'N/A')}")
        
        if result.get('subtitle_segments'):
            print(f"  字幕片段: {len(result['subtitle_segments'])} 个")
        
        if result.get('corrected_result'):
            print(f"  校正模型: {result['corrected_result'].model}")
            print(f"  使用Token: {result['corrected_result'].tokens_used}")
        
        if result.get('github_urls'):
            print("\n  GitHub文件:")
            for file_type, url in result['github_urls'].items():
                print(f"    - {file_type}: {url}")
        
        if result.get('ingestion_result'):
            ir = result['ingestion_result']
            if isinstance(ir, dict) and ir.get('mode') == 'SKILL_GUIDED':
                print(f"\n  Wiki Ingest (SKILL_GUIDED):")
                print(f"    状态: {ir.get('status', 'N/A')}")
                print(f"    Wiki根目录: {ir.get('wiki_root', 'N/A')}")
                print(f"    字幕路径: {ir.get('subtitle_path', 'N/A')}")
                print(f"    {ir.get('message', '')}")
            elif hasattr(ir, 'updated_files'):
                print(f"\n  Wiki更新:")
                print(f"    更新文件: {', '.join(ir.updated_files)}")
                print(f"    关键词: {', '.join(ir.keywords[:5])}")
    else:
        print("✗ 处理失败")
        print(f"  错误: {result.get('error', 'Unknown error')}")
    print("="*60 + "\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='视频转LLM Wiki工作流（支持小红书、抖音、Bilibili）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py "http://xhslink.com/o/4doVxyjRF2c"
  python main.py "https://www.bilibili.com/video/BV1xx411c7mD"
  python main.py --batch urls.txt
  python main.py --skip-download --audio-path ./audio.mp3 "http://example.com"
        """
    )
    
    parser.add_argument('url', nargs='?', help='视频链接（支持小红书、抖音、Bilibili）')
    parser.add_argument('--batch', '-b', metavar='FILE', help='批量处理，从文件读取URL列表')
    parser.add_argument('--skip-download', action='store_true', help='跳过下载，使用本地文件')
    parser.add_argument('--video-path', help='本地视频文件路径（配合--skip-download使用）')
    parser.add_argument('--audio-path', help='本地音频文件路径（配合--skip-download使用）')
    parser.add_argument('--keep-temp', action='store_true', help='保留临时文件')
    parser.add_argument('--config', '-c', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.url and not args.batch:
        parser.error('必须提供URL或使用--batch指定文件')
    
    if args.skip_download and not (args.video_path or args.audio_path):
        parser.error('使用--skip-download时必须提供--video-path或--audio-path')
    
    # 加载配置
    config = load_config(args.config)
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 初始化工作流
    workflow = VideoToLLMWikiWorkflow(config)
    
    # 处理视频
    if args.batch:
        # 批量处理
        urls = read_urls_from_file(args.batch)
        print(f"从文件读取了 {len(urls)} 个URL")
        results = workflow.process_batch(urls, keep_temp=args.keep_temp)
        
        # 打印汇总
        success_count = sum(1 for r in results if r['success'])
        print(f"\n批量处理完成: {success_count}/{len(results)} 成功")
        
        # 打印失败的URL
        failed = [r for r in results if not r['success']]
        if failed:
            print("\n失败的URL:")
            for r in failed:
                print(f"  - {r['url']}: {r.get('error', 'Unknown')}")
    else:
        # 单个处理
        result = workflow.process_video(
            args.url,
            skip_download=args.skip_download,
            video_path=args.video_path,
            audio_path=args.audio_path,
            keep_temp=args.keep_temp
        )
        print_result(result)
        
        # 返回退出码
        return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
