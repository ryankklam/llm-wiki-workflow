"""
GitHub上传模块 - 自动提交字幕文件到GitHub仓库
"""

import os
import base64
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

from github import Github
from github.GithubException import GithubException

from .utils import UploadError, get_env_var

logger = logging.getLogger(__name__)


class GitHubUploader:
    """GitHub文件上传器"""
    
    def __init__(self, config: Dict):
        """
        初始化上传器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.github_config = config.get('github', {})
        
        # GitHub配置
        self.repo_owner = self.github_config.get('repo_owner')
        self.repo_name = self.github_config.get('repo_name')
        self.branch = self.github_config.get('branch', 'main')
        self.content_path = self.github_config.get('content_path', 'content/videos')
        
        # GitHub客户端
        self.github = None
        self.repo = None
        
        # 验证配置
        self._validate_config()
    
    def _validate_config(self):
        """验证GitHub配置"""
        if not self.repo_owner or not self.repo_name:
            raise UploadError("GitHub配置错误：缺少repo_owner或repo_name")
        
        # 检查token
        token = get_env_var('GITHUB_TOKEN')
        if not token:
            raise UploadError("未设置GITHUB_TOKEN环境变量")
    
    def connect(self):
        """连接到GitHub"""
        if self.github is not None:
            return
        
        token = get_env_var('GITHUB_TOKEN')
        
        try:
            self.github = Github(token)
            self.repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            logger.info(f"成功连接到GitHub仓库: {self.repo_owner}/{self.repo_name}")
        except GithubException as e:
            raise UploadError(f"GitHub连接失败: {e}")
        except Exception as e:
            raise UploadError(f"GitHub连接失败: {e}")
    
    def upload_file(self, 
                    local_path: str, 
                    remote_path: str = None,
                    commit_message: str = None) -> str:
        """
        上传单个文件到GitHub
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径（相对于仓库根目录）
            commit_message: 提交信息
            
        Returns:
            文件的GitHub URL
        """
        self.connect()
        
        local_file = Path(local_path)
        if not local_file.exists():
            raise UploadError(f"本地文件不存在: {local_path}")
        
        # 确定远程路径
        if remote_path is None:
            remote_path = f"{self.content_path}/{local_file.name}"
        
        # 确保路径不以/开头
        remote_path = remote_path.lstrip('/')
        
        # 读取文件内容
        with open(local_file, 'rb') as f:
            content = f.read()
        
        # 生成提交信息
        if commit_message is None:
            commit_message = self.github_config.get(
                'commit_message_template', 
                'Add file: {filename}'
            ).format(filename=local_file.name)
        
        try:
            # 检查文件是否已存在
            try:
                existing_file = self.repo.get_contents(remote_path, ref=self.branch)
                # 文件存在，更新
                result = self.repo.update_file(
                    path=remote_path,
                    message=f"{commit_message} (update)",
                    content=content,
                    sha=existing_file.sha,
                    branch=self.branch
                )
                logger.info(f"文件已更新: {remote_path}")
            except GithubException as e:
                if e.status == 404:
                    # 文件不存在，创建新文件
                    result = self.repo.create_file(
                        path=remote_path,
                        message=commit_message,
                        content=content,
                        branch=self.branch
                    )
                    logger.info(f"文件已创建: {remote_path}")
                else:
                    raise
            
            # 返回文件URL
            file_url = f"https://github.com/{self.repo_owner}/{self.repo_name}/blob/{self.branch}/{remote_path}"
            return file_url
            
        except GithubException as e:
            raise UploadError(f"文件上传失败: {e}")
        except Exception as e:
            raise UploadError(f"文件上传失败: {e}")
    
    def upload_subtitle_package(self,
                                 video_info: Dict,
                                 corrected_md_path: str,
                                 raw_files: Dict[str, str] = None) -> Dict[str, str]:
        """
        上传完整的字幕包（校正后的Markdown + 原始文件）
        
        Args:
            video_info: 视频信息字典
            corrected_md_path: 校正后的Markdown文件路径
            raw_files: 原始文件路径字典 {'srt': path, 'txt': path, ...}
            
        Returns:
            上传文件URL字典
        """
        self.connect()
        
        uploaded_urls = {}
        
        # 生成基础路径
        video_title = video_info.get('title', 'unknown')
        safe_title = self._sanitize_path(video_title)
        date_str = datetime.now().strftime('%Y-%m-%d')
        base_path = f"{self.content_path}/{date_str}_{safe_title}"
        
        # 上传校正后的Markdown
        if corrected_md_path and Path(corrected_md_path).exists():
            md_filename = Path(corrected_md_path).name
            remote_md_path = f"{base_path}/{md_filename}"
            
            commit_msg = f"Add corrected subtitle: {video_title}"
            url = self.upload_file(corrected_md_path, remote_md_path, commit_msg)
            uploaded_urls['corrected_md'] = url
        
        # 上传原始文件到raw子目录
        if raw_files:
            for file_type, file_path in raw_files.items():
                if file_path and Path(file_path).exists():
                    filename = Path(file_path).name
                    remote_path = f"{base_path}/raw/{filename}"
                    
                    commit_msg = f"Add {file_type} subtitle: {video_title}"
                    url = self.upload_file(file_path, remote_path, commit_msg)
                    uploaded_urls[file_type] = url
        
        logger.info(f"字幕包上传完成，共 {len(uploaded_urls)} 个文件")
        return uploaded_urls
    
    def update_index_file(self, 
                          video_info: Dict,
                          subtitle_url: str,
                          category: str = None):
        """
        更新Wiki索引文件
        
        Args:
            video_info: 视频信息
            subtitle_url: 字幕文件URL
            category: 分类
        """
        self.connect()
        
        wiki_config = self.config.get('wiki', {})
        index_file = wiki_config.get('index_file', 'index.md')
        
        try:
            # 尝试获取现有索引文件
            try:
                file_content = self.repo.get_contents(index_file, ref=self.branch)
                current_content = base64.b64decode(file_content.content).decode('utf-8')
                sha = file_content.sha
            except GithubException as e:
                if e.status == 404:
                    # 索引文件不存在，创建新文件
                    current_content = "# LLM Wiki Index\n\n"
                    sha = None
                else:
                    raise
            
            # 添加新条目
            new_entry = self._create_index_entry(video_info, subtitle_url, category)
            updated_content = current_content + new_entry
            
            # 提交更新
            commit_msg = f"Update index: Add {video_info.get('title', 'new video')}"
            
            if sha:
                self.repo.update_file(
                    path=index_file,
                    message=commit_msg,
                    content=updated_content,
                    sha=sha,
                    branch=self.branch
                )
            else:
                self.repo.create_file(
                    path=index_file,
                    message=commit_msg,
                    content=updated_content,
                    branch=self.branch
                )
            
            logger.info(f"索引文件已更新: {index_file}")
            
        except Exception as e:
            logger.warning(f"更新索引文件失败: {e}")
            # 不抛出异常，因为这不是关键操作
    
    def _create_index_entry(self, 
                           video_info: Dict, 
                           subtitle_url: str,
                           category: str = None) -> str:
        """
        创建索引条目
        
        Args:
            video_info: 视频信息
            subtitle_url: 字幕URL
            category: 分类
            
        Returns:
            索引条目Markdown文本
        """
        title = video_info.get('title', 'Unknown')
        author = video_info.get('uploader', 'Unknown')
        date = datetime.now().strftime('%Y-%m-%d')
        
        category_tag = f" [{category}]" if category else ""
        
        entry = f"\n- [{date}]{category_tag} [{title}]({subtitle_url}) - by {author}\n"
        return entry
    
    def _sanitize_path(self, path: str) -> str:
        """
        清理路径字符串
        
        Args:
            path: 原始路径
            
        Returns:
            清理后的路径
        """
        # 替换非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            path = path.replace(char, '_')
        
        # 限制长度
        if len(path) > 50:
            path = path[:50]
        
        # 移除首尾空格和点
        path = path.strip(' .')
        
        return path
    
    def get_repo_info(self) -> Dict:
        """
        获取仓库信息
        
        Returns:
            仓库信息字典
        """
        self.connect()
        
        return {
            'name': self.repo.name,
            'full_name': self.repo.full_name,
            'url': self.repo.html_url,
            'default_branch': self.repo.default_branch,
            'stars': self.repo.stargazers_count,
            'forks': self.repo.forks_count,
        }


# 便捷函数
def upload_to_github(local_path: str, 
                     config: Dict,
                     remote_path: str = None,
                     commit_message: str = None) -> str:
    """
    便捷函数：上传文件到GitHub
    
    Args:
        local_path: 本地文件路径
        config: 配置字典
        remote_path: 远程文件路径
        commit_message: 提交信息
        
    Returns:
        文件URL
    """
    uploader = GitHubUploader(config)
    return uploader.upload_file(local_path, remote_path, commit_message)
