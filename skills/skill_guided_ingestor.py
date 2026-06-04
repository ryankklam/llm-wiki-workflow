"""
Skill-Guided Ingestor - 准备数据后由LLM按SKILL.md执行ingest

职责分工：
- 本模块：clone仓库、保存视频/字幕文件、commit & push
- LLM自身：阅读内容、提取实体/概念、创建wiki页面、更新交叉引用

工作流程：
1. Clone远程仓库（或使用本地目录）
2. 根据平台保存视频到 raw/{platform}/video/
3. 根据平台保存校正后的字幕到 raw/{platform}/subtitle/
4. 返回准备好的数据，交由LLM执行SKILL.md的ingest流程
5. LLM完成后，调用commit_and_push提交更改

支持平台：小红书(xiaohongshu)、抖音(douyin)
"""

import os
import re
import time
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, field

# 导入仓库管理器
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.github_repo_manager import GitHubRepoManager

logger = logging.getLogger(__name__)


@dataclass
class SkillGuidedResult:
    """Skill-Guided ingest 结果"""
    success: bool
    wiki_root: str
    video_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    corrected_content: Optional[str] = None
    video_info: Optional[Dict] = None
    pushed: bool = False
    error: Optional[str] = None


class SkillGuidedIngestor:
    """
    Skill-Guided Ingestor
    
    准备数据后由LLM按SKILL.md规范执行ingest。
    本类只负责文件操作（clone、保存、commit、push），
    不负责内容理解（由LLM完成）。
    """
    
    def __init__(self, config: Dict):
        """
        初始化
        
        Args:
            config: 配置字典，包含 ingestion.skill_guided 配置
        """
        self.config = config
        self.sg_config = config.get('ingestion', {}).get('skill_guided', {})
        
        # 路径配置
        self.wiki_root = Path(self.sg_config.get('wiki_root', '~/llm-wiki')).expanduser()
        self.video_subdir = self.sg_config.get('video_subdir', 'raw/rednote/video')
        self.subtitle_subdir = self.sg_config.get('subtitle_subdir', 'raw/rednote/subtitle')
        self.skill_md_path = self.sg_config.get('skill_md_path', '.agents/skills/llm-wiki/SKILL.md')
        
        # 远程仓库
        remote_config = self.sg_config.get('remote_repo', {})
        self.use_remote_repo = remote_config.get('enabled', False)
        self.repo_manager: Optional[GitHubRepoManager] = None
        
        if self.use_remote_repo:
            self.repo_manager = GitHubRepoManager(self.sg_config)
        
        logger.info(f"SkillGuidedIngestor 初始化完成")
        if self.use_remote_repo:
            logger.info(f"  远程仓库: {remote_config.get('github_owner')}/{remote_config.get('github_repo')}@{remote_config.get('branch')}")
        else:
            logger.info(f"  本地目录: {self.wiki_root}")
    
    def prepare(self, video_path: str, corrected_content: str, video_info: Dict) -> SkillGuidedResult:
        """
        步骤A：准备数据（clone + 保存文件）
        
        Args:
            video_path: 视频文件路径
            corrected_content: 校正后的字幕内容
            video_info: 视频信息
            
        Returns:
            SkillGuidedResult，包含wiki_root路径供LLM操作
        """
        result = SkillGuidedResult(success=False, wiki_root=str(self.wiki_root))
        
        # 记录 prepare 时间戳，用于后续完整性校验
        self._prepare_timestamp = time.time()
        
        try:
            # 1. Clone远程仓库（如果启用）
            if self.use_remote_repo and self.repo_manager:
                logger.info("[准备] Clone远程仓库...")
                local_repo_path = self.repo_manager.clone()
                self.wiki_root = local_repo_path
                result.wiki_root = str(local_repo_path)
            
            # 2. 检测平台并选择目录
            platform = self._detect_platform(video_info.get('original_url', ''))
            video_subdir = f"raw/{platform}/video"
            subtitle_subdir = f"raw/{platform}/subtitle"
            logger.info(f"[准备] 检测到平台: {platform}")
            
            # 3. 生成文件名
            short_id = self._extract_short_id(video_info.get('original_url', ''), platform)
            date_str = datetime.now().strftime('%Y-%m-%d')
            safe_title = self._sanitize_filename(video_info.get('title', 'unknown'))[:40]
            base_filename = f"{date_str}-{safe_title}_{short_id}"
            
            # 4. 确保目录结构
            (self.wiki_root / video_subdir).mkdir(parents=True, exist_ok=True)
            (self.wiki_root / subtitle_subdir).mkdir(parents=True, exist_ok=True)
            
            # 5. 保存视频
            video_filename = f"{base_filename}.mp4"
            video_target = self.wiki_root / video_subdir / video_filename
            shutil.copy2(video_path, video_target)
            result.video_path = str(video_target)
            logger.info(f"[准备] 视频已保存: {video_subdir}/{video_filename}")
            
            # 6. 保存字幕
            subtitle_filename = f"{base_filename}.md"
            subtitle_target = self.wiki_root / subtitle_subdir / subtitle_filename
            with open(subtitle_target, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            result.subtitle_path = str(subtitle_target)
            logger.info(f"[准备] 字幕已保存: {subtitle_subdir}/{subtitle_filename}")
            
            result.corrected_content = corrected_content
            result.video_info = video_info
            result.success = True
            
            logger.info(f"[准备] 数据准备完成，wiki_root: {self.wiki_root}")
            
        except Exception as e:
            logger.error(f"[准备] 失败: {e}")
            result.error = str(e)
        
        return result
    
    def prepare_image_note(
        self,
        markdown_path: str,
        image_paths: List[str],
        note_info: Dict
    ) -> SkillGuidedResult:
        """
        步骤A2：准备图文笔记数据（clone + 保存图片和MD）

        Args:
            markdown_path: 生成的Markdown文件路径
            image_paths: 下载的图片文件路径列表
            note_info: 笔记信息字典，包含：
                - title: 标题
                - author: 作者
                - note_id: 笔记ID
                - original_url: 原始链接
                - note_type: 笔记类型

        Returns:
            SkillGuidedResult，包含wiki_root路径供LLM操作
        """
        result = SkillGuidedResult(success=False, wiki_root=str(self.wiki_root))

        # 记录 prepare 时间戳
        self._prepare_timestamp = time.time()

        try:
            # 1. Clone远程仓库
            if self.use_remote_repo and self.repo_manager:
                logger.info("[准备-图文] Clone远程仓库...")
                local_repo_path = self.repo_manager.clone()
                self.wiki_root = local_repo_path
                result.wiki_root = str(local_repo_path)

            # 2. 检测平台
            platform = self._detect_platform(note_info.get('original_url', ''))
            image_subdir = f"raw/{platform}/images"
            content_subdir = f"raw/{platform}/content"
            logger.info(f"[准备-图文] 检测到平台: {platform}")

            # 3. 生成文件名
            short_id = self._extract_short_id(note_info.get('original_url', ''), platform)
            date_str = datetime.now().strftime('%Y-%m-%d')
            safe_title = self._sanitize_filename(note_info.get('title', 'unknown'))[:40]
            base_filename = f"{date_str}-{safe_title}_{short_id}"

            # 4. 确保目录结构
            (self.wiki_root / image_subdir).mkdir(parents=True, exist_ok=True)
            (self.wiki_root / content_subdir).mkdir(parents=True, exist_ok=True)

            # 5. 保存图片
            saved_images = []
            for i, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    ext = Path(img_path).suffix
                    img_filename = f"{base_filename}_image_{i+1:02d}{ext}"
                    img_target = self.wiki_root / image_subdir / img_filename
                    shutil.copy2(img_path, img_target)
                    saved_images.append(str(img_target))
                    logger.info(f"[准备-图文] 图片已保存: {image_subdir}/{img_filename}")

            # 6. 保存Markdown内容
            content_filename = f"{base_filename}.md"
            content_target = self.wiki_root / content_subdir / content_filename

            # 读取原始MD，替换图片路径为仓库内相对路径
            with open(markdown_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 替换图片路径为 raw/{platform}/images/ 下的相对路径
            for i, (orig_path, saved_path) in enumerate(zip(image_paths, saved_images)):
                if os.path.exists(orig_path):
                    rel_path = f"../images/{base_filename}_image_{i+1:02d}{Path(orig_path).suffix}"
                    # 替换各种可能的路径引用
                    md_content = md_content.replace(orig_path, rel_path)

            with open(content_target, 'w', encoding='utf-8') as f:
                f.write(md_content)

            result.corrected_content = md_content
            result.video_info = note_info
            result.video_path = str(content_target)
            result.success = True

            logger.info(
                f"[准备-图文] 数据准备完成，"
                f"图片: {len(saved_images)}张, "
                f"MD: {content_subdir}/{content_filename}"
            )

        except Exception as e:
            logger.error(f"[准备-图文] 失败: {e}")
            result.error = str(e)

        return result
    
    def commit_and_push(self, message: str) -> bool:
        """
        步骤C：提交并推送更改（LLM完成ingest后调用）
        
        提交前会自动校验以下文件是否已更新：
        - wiki/index.md
        - wiki/overview.md
        - wiki/log.md
        如果检测到遗漏，会打印警告但不阻止提交。
        
        Args:
            message: Commit消息
            
        Returns:
            是否成功
        """
        if not self.use_remote_repo or not self.repo_manager:
            logger.info("[提交] 远程仓库未启用，跳过commit & push")
            return False
        
        # ---- Ingest 完整性预检 ----
        self._validate_ingest_completeness()
        
        logger.info(f"[提交] 正在 commit & push...")
        success = self.repo_manager.commit_and_push(message)
        
        if success:
            logger.info(f"[提交] 推送成功")
        else:
            logger.warning(f"[提交] 推送失败")
        
        return success
    
    def _validate_ingest_completeness(self):
        """
        校验 ingest 流程的完整性
        
        检查 wiki/index.md、wiki/overview.md、wiki/log.md 是否在本次 ingest 中被更新。
        通过对比文件的修改时间与 prepare() 的调用时间来判断。
        """
        import time
        
        required_files = {
            'wiki/index.md': '内容目录',
            'wiki/overview.md': '整体概览',
            'wiki/log.md': '操作日志',
        }
        
        warnings = []
        for rel_path, desc in required_files.items():
            file_path = self.wiki_root / rel_path
            if not file_path.exists():
                warnings.append(f"  ⚠️ {rel_path} ({desc}) 不存在")
            elif hasattr(self, '_prepare_timestamp'):
                mtime = file_path.stat().st_mtime
                if mtime < self._prepare_timestamp:
                    warnings.append(f"  ⚠️ {rel_path} ({desc}) 未更新 (修改时间早于 prepare)")
        
        if warnings:
            logger.warning("[完整性检查] 以下索引文件可能未更新：")
            for w in warnings:
                logger.warning(w)
            logger.warning("[完整性检查] 请确认是否已更新 index.md、overview.md、log.md")
        else:
            logger.info("[完整性检查] ✅ index.md、overview.md、log.md 均已更新")
    
    def read_wiki_file(self, relative_path: str) -> Optional[str]:
        """
        读取wiki仓库中的文件（供LLM查询已有内容）
        
        Args:
            relative_path: 相对于wiki_root的路径
            
        Returns:
            文件内容，不存在返回None
        """
        target = self.wiki_root / relative_path
        if not target.exists():
            return None
        with open(target, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_wiki_files(self, subdir: str = "wiki") -> List[str]:
        """
        列出wiki目录下的文件（供LLM了解已有内容）
        
        Args:
            subdir: 子目录名
            
        Returns:
            文件路径列表
        """
        target_dir = self.wiki_root / subdir
        if not target_dir.exists():
            return []
        return [str(f.relative_to(self.wiki_root)) for f in target_dir.rglob("*.md")]
    
    def write_wiki_file(self, content: str, relative_path: str):
        """
        写入文件到wiki仓库（供LLM创建/更新页面）
        
        Args:
            content: 文件内容
            relative_path: 相对于wiki_root的路径
        """
        target = self.wiki_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"[写入] {relative_path}")
    
    def get_ingest_context(self) -> Dict:
        """
        获取ingest上下文信息（供LLM了解当前wiki状态）
        
        Returns:
            上下文字典
        """
        context = {
            'wiki_root': str(self.wiki_root),
            'existing_sources': self.list_wiki_files("wiki/sources"),
            'existing_concepts': self.list_wiki_files("wiki/concepts"),
            'existing_entities': self.list_wiki_files("wiki/entities"),
            'existing_topics': self.list_wiki_files("wiki/topics"),
            'existing_solutions': self.list_wiki_files("wiki/solutions"),
            'index_content': self.read_wiki_file("wiki/index.md"),
            'overview_content': self.read_wiki_file("wiki/overview.md"),
        }
        return context
    
    def _detect_platform(self, url: str) -> str:
        """
        检测视频链接的平台
        
        Args:
            url: 视频链接
            
        Returns:
            平台名称: 'xiaohongshu', 'douyin', 'unknown'
        """
        if not url:
            return 'unknown'
        url_lower = url.lower()
        if any(p in url_lower for p in ['xhslink.com', 'xiaohongshu.com', 'xhs.cn']):
            return 'xiaohongshu'
        if any(p in url_lower for p in ['douyin.com', 'v.douyin.com', 'iesdouyin.com']):
            return 'douyin'
        return 'unknown'
    
    def _extract_short_id(self, url: str, platform: str) -> str:
        """
        从链接提取短ID（用于文件命名）
        
        Args:
            url: 视频链接
            platform: 平台名称
            
        Returns:
            短ID字符串
        """
        if not url:
            return 'unknown'
        
        if platform == 'xiaohongshu':
            # 小红书：从 xhslink.com/o/xxxxx 或 xhslink.com/a/xxxxx 提取
            match = re.search(r'xhslink\.com/[oa]/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
            match = re.search(r'xiaohongshu\.com/(?:explore|discovery/item)/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
        
        elif platform == 'douyin':
            # 抖音：从 v.douyin.com/xxxxx 提取
            match = re.search(r'v\.douyin\.com/([a-zA-Z0-9]+)/?', url)
            if match:
                return match.group(1)
            # 从 douyin.com/video/xxxxx 提取
            match = re.search(r'douyin\.com/video/(\d+)', url)
            if match:
                return match.group(1)
            # 从 modal_id=xxxxx 提取
            match = re.search(r'modal_id=(\d+)', url)
            if match:
                return match.group(1)
        
        # 兜底：取URL最后一段有意义的部分
        parts = url.rstrip('/').split('/')
        for part in reversed(parts):
            if part and part not in ('o', 'a', 'video', 'item', 'explore', 'discovery'):
                return part[:20]
        return 'unknown'
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        return filename.strip(' .')[:50]
