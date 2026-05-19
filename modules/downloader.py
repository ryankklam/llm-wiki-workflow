"""
视频下载模块 - 使用yt-dlp下载小红书视频
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import yt_dlp

from .utils import sanitize_filename, ensure_dir, DownloadError

logger = logging.getLogger(__name__)


class VideoDownloader:
    """视频下载器类"""
    
    def __init__(self, config: Dict):
        """
        初始化下载器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.download_config = config.get('download', {})
        self.temp_dir = Path(config.get('paths', {}).get('temp_dir', './storage/temp'))
        ensure_dir(self.temp_dir)
        
    def _get_ydl_opts(self, output_path: str) -> Dict:
        """
        获取yt-dlp配置选项
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            yt-dlp配置字典
        """
        return {
            'format': self.download_config.get('format', 'best'),
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'socket_timeout': self.download_config.get('timeout', 300),
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            # 添加请求头模拟浏览器
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            },
            # 进度回调
            'progress_hooks': [self._progress_hook],
        }
    
    def _progress_hook(self, d):
        """下载进度回调"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            logger.info(f"下载进度: {percent} | 速度: {speed} | 剩余时间: {eta}")
        elif d['status'] == 'finished':
            logger.info(f"下载完成: {d['filename']}")
    
    def extract_video_info(self, url: str) -> Dict:
        """
        提取视频信息（不下载）
        
        Args:
            url: 视频链接
            
        Returns:
            视频信息字典
        """
        logger.info(f"正在提取视频信息: {url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # 提取关键信息
                video_info = {
                    'id': info.get('id', ''),
                    'title': info.get('title', 'Unknown Title'),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'uploader_id': info.get('uploader_id', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'original_url': url,
                    'webpage_url': info.get('webpage_url', url),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': len(info.get('formats', [])),
                }
                
                logger.info(f"视频信息提取成功: {video_info['title']}")
                return video_info
                
        except Exception as e:
            logger.error(f"提取视频信息失败: {e}")
            raise DownloadError(f"无法提取视频信息: {e}")
    
    def download_video(self, url: str, custom_filename: Optional[str] = None) -> Tuple[str, Dict]:
        """
        下载视频
        
        Args:
            url: 视频链接
            custom_filename: 自定义文件名（不含扩展名）
            
        Returns:
            (下载文件路径, 视频信息字典)
        """
        logger.info(f"开始下载视频: {url}")
        
        # 首先提取视频信息
        video_info = self.extract_video_info(url)
        
        # 确定输出文件名
        if custom_filename:
            base_name = sanitize_filename(custom_filename)
        else:
            # 使用视频标题作为文件名
            base_name = sanitize_filename(video_info['title'])
            # 添加视频ID避免重复
            base_name = f"{base_name}_{video_info['id'][:8]}"
        
        output_path = str(self.temp_dir / f"{base_name}.%(ext)s")
        
        # 配置yt-dlp
        ydl_opts = self._get_ydl_opts(output_path)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 下载视频
                ydl.download([url])
                
                # 找到实际下载的文件
                downloaded_files = list(self.temp_dir.glob(f"{base_name}.*"))
                video_files = [f for f in downloaded_files if f.suffix in ['.mp4', '.webm', '.mkv', '.mov']]
                
                if not video_files:
                    raise DownloadError(f"下载后未找到视频文件: {base_name}")
                
                downloaded_file = str(video_files[0])
                logger.info(f"视频下载成功: {downloaded_file}")
                
                return downloaded_file, video_info
                
        except Exception as e:
            logger.error(f"视频下载失败: {e}")
            raise DownloadError(f"视频下载失败: {e}")
    
    def is_xiaohongshu_url(self, url: str) -> bool:
        """
        检查是否为小红书链接
        
        Args:
            url: 待检查的URL
            
        Returns:
            是否为小红书链接
        """
        xiaohongshu_patterns = [
            r'xhslink\.com',
            r'xiaohongshu\.com',
            r'xhs\.cn',
        ]
        
        url_lower = url.lower()
        return any(re.search(pattern, url_lower) for pattern in xiaohongshu_patterns)
    
    def cleanup_temp_files(self, video_path: str = None, keep_video: bool = False):
        """
        清理临时文件
        
        Args:
            video_path: 视频文件路径（如果提供则删除）
            keep_video: 是否保留视频文件
        """
        if video_path and not keep_video:
            try:
                video_file = Path(video_path)
                if video_file.exists():
                    video_file.unlink()
                    logger.info(f"已删除临时视频文件: {video_path}")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {e}")


# 便捷函数
def download_xiaohongshu_video(url: str, config: Dict, custom_filename: str = None) -> Tuple[str, Dict]:
    """
    便捷函数：下载小红书视频
    
    Args:
        url: 小红书视频链接
        config: 配置字典
        custom_filename: 自定义文件名
        
    Returns:
        (下载文件路径, 视频信息字典)
    """
    downloader = VideoDownloader(config)
    return downloader.download_video(url, custom_filename)
