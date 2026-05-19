"""
音频提取模块 - 从视频中提取音频
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional
import ffmpeg

from .utils import ensure_dir, WorkflowError

logger = logging.getLogger(__name__)


class AudioExtractor:
    """音频提取器类"""
    
    def __init__(self, config: Dict):
        """
        初始化音频提取器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.audio_config = config.get('audio', {})
        self.temp_dir = Path(config.get('paths', {}).get('temp_dir', './storage/temp'))
        ensure_dir(self.temp_dir)
        
        # 检查ffmpeg是否可用
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """检查ffmpeg是否已安装"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                logger.info(f"FFmpeg已安装: {version_line}")
            else:
                raise WorkflowError("FFmpeg检查失败")
        except FileNotFoundError:
            raise WorkflowError(
                "FFmpeg未安装！请安装FFmpeg:\n"
                "- macOS: brew install ffmpeg\n"
                "- Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "- Windows: 从 https://ffmpeg.org/download.html 下载"
            )
        except Exception as e:
            raise WorkflowError(f"检查FFmpeg时出错: {e}")
    
    def extract_audio(self, video_path: str, output_name: str = None) -> str:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            output_name: 输出音频文件名（不含扩展名）
            
        Returns:
            提取的音频文件路径
        """
        video_file = Path(video_path)
        if not video_file.exists():
            raise WorkflowError(f"视频文件不存在: {video_path}")
        
        # 确定输出文件名
        if output_name is None:
            output_name = video_file.stem
        
        audio_format = self.audio_config.get('format', 'mp3')
        output_path = self.temp_dir / f"{output_name}.{audio_format}"
        
        logger.info(f"开始提取音频: {video_path} -> {output_path}")
        
        try:
            # 构建ffmpeg命令
            stream = ffmpeg.input(str(video_path))
            
            # 音频参数
            audio_params = {
                'vn': None,  # 不包含视频
                'acodec': 'libmp3lame' if audio_format == 'mp3' else 'aac',
                'ar': self.audio_config.get('sample_rate', 16000),  # 采样率
                'ac': 1,  # 单声道（语音识别更优）
            }
            
            # 比特率
            bitrate = self.audio_config.get('bitrate', '32k')
            if bitrate:
                audio_params['audio_bitrate'] = bitrate
            
            stream = ffmpeg.output(stream, str(output_path), **audio_params)
            
            # 执行转换
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            if not output_path.exists():
                raise WorkflowError("音频提取失败：输出文件未生成")
            
            # 获取文件大小
            file_size = output_path.stat().st_size / 1024 / 1024  # MB
            logger.info(f"音频提取成功: {output_path} ({file_size:.2f} MB)")
            
            return str(output_path)
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            logger.error(f"FFmpeg错误: {error_msg}")
            raise WorkflowError(f"音频提取失败: {error_msg}")
        except Exception as e:
            logger.error(f"音频提取失败: {e}")
            raise WorkflowError(f"音频提取失败: {e}")
    
    def get_audio_info(self, audio_path: str) -> Dict:
        """
        获取音频文件信息
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            音频信息字典
        """
        try:
            probe = ffmpeg.probe(audio_path)
            audio_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
                None
            )
            
            if audio_stream is None:
                raise WorkflowError("无法找到音频流")
            
            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'bitrate': int(probe['format'].get('bit_rate', 0)) // 1000,  # kbps
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': audio_stream.get('channels', 0),
                'codec': audio_stream.get('codec_name', 'unknown'),
                'format': probe['format'].get('format_name', 'unknown'),
            }
            
            return info
            
        except Exception as e:
            logger.warning(f"获取音频信息失败: {e}")
            return {}
    
    def cleanup_audio(self, audio_path: str):
        """
        删除临时音频文件
        
        Args:
            audio_path: 音频文件路径
        """
        try:
            audio_file = Path(audio_path)
            if audio_file.exists():
                audio_file.unlink()
                logger.info(f"已删除临时音频文件: {audio_path}")
        except Exception as e:
            logger.warning(f"删除音频文件失败: {e}")


# 便捷函数
def extract_audio_from_video(video_path: str, config: Dict, output_name: str = None) -> str:
    """
    便捷函数：从视频提取音频
    
    Args:
        video_path: 视频文件路径
        config: 配置字典
        output_name: 输出音频文件名
        
    Returns:
        音频文件路径
    """
    extractor = AudioExtractor(config)
    return extractor.extract_audio(video_path, output_name)
