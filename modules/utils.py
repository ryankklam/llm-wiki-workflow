"""
工具函数模块
"""

import os
import re
import yaml
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv


def load_config(config_path: str = "config/config.yaml") -> dict:
    """加载YAML配置文件"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    config_file = project_root / config_path
    
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 加载环境变量
    env_file = project_root / "config" / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    return config


def setup_logging(config: dict = None):
    """设置日志配置"""
    if config is None:
        config = load_config()
    
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('file')
    
    # 确保日志目录存在
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    # 限制长度
    if len(filename) > 200:
        filename = filename[:200]
    # 移除首尾空格和点
    filename = filename.strip(' .')
    return filename


def format_timestamp(seconds: float) -> str:
    """
    将秒数格式化为时间戳字符串 MM:SS
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化后的时间戳 (MM:SS)
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def ensure_dir(path: str) -> Path:
    """
    确保目录存在，不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_env_var(key: str, default=None) -> str:
    """
    获取环境变量
    
    Args:
        key: 环境变量名
        default: 默认值
        
    Returns:
        环境变量值或默认值
    """
    return os.getenv(key, default)


def generate_markdown_metadata(title: str, author: str, url: str, 
                                duration: str = "", tags: list = None) -> str:
    """
    生成Markdown文件的YAML前置元数据
    
    Args:
        title: 视频标题
        author: 作者
        url: 原始链接
        duration: 视频时长
        tags: 标签列表
        
    Returns:
        YAML元数据字符串
    """
    metadata = {
        'title': title,
        'author': author,
        'source': url,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'type': 'video-subtitle'
    }
    
    if duration:
        metadata['duration'] = duration
    if tags:
        metadata['tags'] = tags
    
    yaml_content = yaml.dump(metadata, allow_unicode=True, sort_keys=False)
    return f"---\n{yaml_content}---\n\n"


class WorkflowError(Exception):
    """工作流自定义异常"""
    pass


class DownloadError(WorkflowError):
    """下载错误"""
    pass


class TranscriptionError(WorkflowError):
    """转录错误"""
    pass


class CorrectionError(WorkflowError):
    """校正错误"""
    pass


class UploadError(WorkflowError):
    """上传错误"""
    pass
