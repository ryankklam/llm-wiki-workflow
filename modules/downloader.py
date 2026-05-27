"""
视频下载模块 - 使用yt-dlp下载视频（支持小红书、抖音等平台）
"""

import os
import re
import json
import logging
import requests
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
        
        # 抖音链接使用专用提取方法
        if self.is_douyin_url(url):
            return self._extract_douyin_info(url)
        
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
        
        # 抖音链接使用专用下载方法
        if self.is_douyin_url(url):
            return self._download_douyin(url, custom_filename)
        
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
    
    def is_douyin_url(self, url: str) -> bool:
        """
        检查是否为抖音链接
        
        Args:
            url: 待检查的URL
            
        Returns:
            是否为抖音链接
        """
        douyin_patterns = [
            r'douyin\.com',
            r'v\.douyin\.com',
            r'iesdouyin\.com',
        ]
        
        url_lower = url.lower()
        return any(re.search(pattern, url_lower) for pattern in douyin_patterns)
    
    def detect_platform(self, url: str) -> str:
        """
        检测视频链接的平台
        
        Args:
            url: 视频链接
            
        Returns:
            平台名称: 'xiaohongshu', 'douyin', 'unknown'
        """
        if self.is_xiaohongshu_url(url):
            return 'xiaohongshu'
        elif self.is_douyin_url(url):
            return 'douyin'
        return 'unknown'
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        从URL中提取视频ID
        
        Args:
            url: 视频链接
            
        Returns:
            视频ID，如果无法提取则返回None
        """
        # 小红书链接
        if self.is_xiaohongshu_url(url):
            # xhslink短链格式: http://xhslink.com/o/XXXXXX
            match = re.search(r'xhslink\.com/o/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
            # 长链格式: xiaohongshu.com/discovery/item/XXXXXX
            match = re.search(r'xiaohongshu\.com/.*?/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
        
        # 抖音链接
        if self.is_douyin_url(url):
            # 短链格式: v.douyin.com/XXXXXX
            match = re.search(r'v\.douyin\.com/([a-zA-Z0-9]+)/?', url)
            if match:
                return match.group(1)
            # 长链格式: douyin.com/video/XXXXXX
            match = re.search(r'douyin\.com/video/(\d+)', url)
            if match:
                return match.group(1)
        
        return None
    
    def check_duplicate(self, url: str, wiki_root: Path = None) -> Dict:
        """
        检查视频链接是否已经处理过
        
        Args:
            url: 视频链接
            wiki_root: Wiki仓库根目录，如果为None则使用默认路径
            
        Returns:
            {
                'is_duplicate': bool,  # 是否重复
                'video_id': str,       # 视频ID
                'platform': str,       # 平台
                'existing_files': [],  # 已存在的文件列表
                'message': str         # 提示信息
            }
        """
        result = {
            'is_duplicate': False,
            'video_id': None,
            'platform': 'unknown',
            'existing_files': [],
            'message': ''
        }
        
        # 检测平台
        platform = self.detect_platform(url)
        result['platform'] = platform
        
        # 提取视频ID
        video_id = self.extract_video_id(url)
        result['video_id'] = video_id
        
        if not video_id:
            result['message'] = f"无法从链接提取视频ID，跳过去重检查"
            return result
        
        # 确定检查目录
        if wiki_root is None:
            wiki_root = Path('/data/user/work/repos/llm-wiki-storage')
        
        if not wiki_root.exists():
            result['message'] = f"Wiki仓库不存在: {wiki_root}，跳过去重检查"
            return result
        
        # 平台目录映射
        platform_dir_map = {
            'xiaohongshu': 'rednote',
            'douyin': 'douyin',
        }
        platform_dir = platform_dir_map.get(platform, platform)
        
        # 检查字幕文件是否存在
        subtitle_dir = wiki_root / 'raw' / platform_dir / 'subtitle'
        video_dir = wiki_root / 'raw' / platform_dir / 'video'
        
        existing_files = []
        
        # 检查字幕文件（包含视频ID的.md文件）
        if subtitle_dir.exists():
            for f in subtitle_dir.glob(f'*{video_id}*.md'):
                existing_files.append(str(f.relative_to(wiki_root)))
        
        # 检查视频文件
        if video_dir.exists():
            for f in video_dir.glob(f'*{video_id}*.mp4'):
                existing_files.append(str(f.relative_to(wiki_root)))
        
        # 检查source页面
        sources_dir = wiki_root / 'wiki' / 'sources'
        if sources_dir.exists():
            for f in sources_dir.glob('*.md'):
                content = f.read_text(encoding='utf-8')
                if video_id in content:
                    existing_files.append(str(f.relative_to(wiki_root)))
        
        if existing_files:
            result['is_duplicate'] = True
            result['existing_files'] = existing_files
            result['message'] = f"⚠️ 该视频已处理过！视频ID: {video_id}，已存在 {len(existing_files)} 个文件"
        else:
            result['message'] = f"✅ 新视频，视频ID: {video_id}"
        
        return result
    
    def _extract_douyin_info(self, url: str) -> Dict:
        """
        抖音视频信息提取（不依赖yt-dlp）
        
        Args:
            url: 抖音视频链接
            
        Returns:
            视频信息字典
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Referer': 'https://www.douyin.com/',
        }
        
        try:
            resp = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            raise DownloadError(f"无法访问抖音链接: {e}")
        
        # 提取视频ID
        video_id = 'unknown'
        id_match = re.search(r'/video/(\d+)', resp.url)
        if id_match:
            video_id = id_match.group(1)
        
        # 提取标题
        title = 'Unknown'
        title_match = re.search(r'<title>([^<]+)</title>', resp.text)
        if title_match:
            title = title_match.group(1).split(' - ')[0].strip()
            title = re.sub(r'\s*#[^\s]+', '', title).strip()
        
        # 提取作者
        author = 'Unknown'
        author_match = re.search(r'"nickname":"([^"]+)"', resp.text)
        if author_match:
            author = author_match.group(1)
        
        # 提取描述
        desc_match = re.search(r'"desc":"([^"]*)"', resp.text)
        description = desc_match.group(1).replace('\\n', '\n') if desc_match else ''
        
        video_info = {
            'id': video_id,
            'title': title,
            'description': description,
            'uploader': author,
            'uploader_id': '',
            'duration': 0,
            'view_count': 0,
            'like_count': 0,
            'upload_date': '',
            'original_url': url,
            'webpage_url': resp.url,
            'thumbnail': '',
            'formats': 0,
            'platform': 'douyin',
        }
        
        logger.info(f"抖音视频信息提取成功: {title} (by {author})")
        return video_info
    
    def _download_douyin(self, url: str, custom_filename: Optional[str] = None) -> Tuple[str, Dict]:
        """
        抖音视频下载（不依赖yt-dlp，直接通过requests获取）
        
        Args:
            url: 抖音视频链接
            custom_filename: 自定义文件名
            
        Returns:
            (下载文件路径, 视频信息字典)
        """
        logger.info(f"[抖音] 开始下载: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Referer': 'https://www.douyin.com/',
        }
        
        try:
            resp = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            raise DownloadError(f"无法访问抖音链接: {e}")
        
        # 提取视频URL
        video_url = None
        patterns = [
            r'"videoUrl":"([^"]+)"',
            r'"playApi":"([^"]+)"',
            r'"play_addr":\{[^}]*"url_list":\["([^"]+)"',
        ]
        for p in patterns:
            match = re.search(p, resp.text)
            if match:
                video_url = match.group(1).replace('\\u002F', '/').replace('\\u0026', '&')
                break
        
        if not video_url:
            raise DownloadError("无法从抖音页面提取视频URL，可能需要登录或链接已失效")
        
        # 提取视频信息
        video_info = self._extract_douyin_info(url)
        
        # 确定文件名
        if custom_filename:
            base_name = sanitize_filename(custom_filename)
        else:
            base_name = sanitize_filename(video_info['title'])
            base_name = f"{base_name}_{video_info['id'][:12]}"
        
        output_path = self.temp_dir / f"{base_name}.mp4"
        
        # 下载视频
        logger.info(f"[抖音] 正在下载视频...")
        video_resp = requests.get(video_url, headers=headers, stream=True, timeout=120)
        video_resp.raise_for_status()
        
        total = int(video_resp.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_path, 'wb') as f:
            for chunk in video_resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        file_size_mb = downloaded / 1024 / 1024
        logger.info(f"[抖音] 视频下载成功: {output_path} ({file_size_mb:.2f} MB)")
        
        return str(output_path), video_info
    
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
