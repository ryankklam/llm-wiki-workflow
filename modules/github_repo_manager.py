"""
GitHub 仓库管理模块 - 用于 clone、commit、push 到远程仓库

支持：
- Clone 指定分支的仓库
- 添加/更新文件
- Commit 并 Push 回远程
"""

import os
import re
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RepoConfig:
    """仓库配置"""
    enabled: bool
    owner: str
    repo: str
    branch: str
    token: Optional[str] = None
    
    @property
    def repo_url(self) -> str:
        """获取仓库 URL"""
        if self.token:
            return f"https://{self.token}@github.com/{self.owner}/{self.repo}.git"
        return f"https://github.com/{self.owner}/{self.repo}.git"
    
    @property
    def repo_name(self) -> str:
        """仓库名称"""
        return f"{self.owner}_{self.repo}"


class GitHubRepoManager:
    """GitHub 仓库管理器"""
    
    def __init__(self, config: Dict):
        """
        初始化仓库管理器
        
        Args:
            config: 配置字典，包含 remote_repo 配置
        """
        remote_config = config.get('remote_repo', {})
        
        self.enabled = remote_config.get('enabled', False)
        self.owner = remote_config.get('github_owner', '')
        self.repo = remote_config.get('github_repo', '')
        self.branch = remote_config.get('branch', 'main')
        self.token = os.getenv('GITHUB_TOKEN')
        
        # 工作目录（用于 clone 仓库）
        self.work_dir = Path('/data/user/work/repos')
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 本地仓库路径
        self.local_repo_path: Optional[Path] = None
        
        if self.enabled:
            logger.info(f"GitHub Repo Manager 初始化: {self.owner}/{self.repo}@{self.branch}")
    
    def is_enabled(self) -> bool:
        """检查是否启用远程仓库"""
        return self.enabled and bool(self.owner) and bool(self.repo)
    
    def has_token(self) -> bool:
        """检查是否有 Token"""
        return bool(self.token)
    
    def clone(self) -> Path:
        """
        Clone 仓库到本地工作目录
        
        Returns:
            本地仓库路径
        """
        if not self.is_enabled():
            raise RuntimeError("远程仓库未启用或配置不完整")
        
        if not self.has_token():
            raise RuntimeError("未设置 GITHUB_TOKEN 环境变量")
        
        repo_url = f"https://{self.token}@github.com/{self.owner}/{self.repo}.git"
        target_path = self.work_dir / self.repo
        
        # 如果已存在，先删除
        if target_path.exists():
            logger.info(f"删除已存在的仓库目录: {target_path}")
            shutil.rmtree(target_path)
        
        logger.info(f"Cloning {self.owner}/{self.repo}@{self.branch}...")
        
        # Clone 仓库
        result = subprocess.run(
            ['git', 'clone', '-b', self.branch, '--single-branch', repo_url, str(target_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            logger.error(f"Clone 失败: {result.stderr}")
            raise RuntimeError(f"Clone 失败: {result.stderr}")
        
        # 配置 git 用户信息
        subprocess.run(['git', 'config', 'user.email', 'solo-ai@local'], cwd=target_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'SOLO AI'], cwd=target_path, capture_output=True)
        
        self.local_repo_path = target_path
        logger.info(f"Clone 成功: {target_path}")
        
        return target_path
    
    def add_file(self, local_file_path: str, repo_relative_path: str) -> bool:
        """
        添加文件到仓库
        
        Args:
            local_file_path: 本地文件路径
            repo_relative_path: 仓库内相对路径
            
        Returns:
            是否成功
        """
        if not self.local_repo_path:
            raise RuntimeError("请先调用 clone()")
        
        local_file = Path(local_file_path)
        if not local_file.exists():
            logger.error(f"本地文件不存在: {local_file_path}")
            return False
        
        # 目标路径
        target_path = self.local_repo_path / repo_relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        shutil.copy2(local_file, target_path)
        logger.info(f"文件已复制: {local_file_path} -> {repo_relative_path}")
        
        return True
    
    def write_file(self, content: str, repo_relative_path: str) -> bool:
        """
        直接写入内容到仓库
        
        Args:
            content: 文件内容
            repo_relative_path: 仓库内相对路径
            
        Returns:
            是否成功
        """
        if not self.local_repo_path:
            raise RuntimeError("请先调用 clone()")
        
        target_path = self.local_repo_path / repo_relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"文件已写入: {repo_relative_path}")
        return True
    
    def read_file(self, repo_relative_path: str) -> Optional[str]:
        """
        读取仓库中的文件
        
        Args:
            repo_relative_path: 仓库内相对路径
            
        Returns:
            文件内容，不存在返回 None
        """
        if not self.local_repo_path:
            raise RuntimeError("请先调用 clone()")
        
        target_path = self.local_repo_path / repo_relative_path
        
        if not target_path.exists():
            return None
        
        with open(target_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def file_exists(self, repo_relative_path: str) -> bool:
        """检查文件是否存在"""
        if not self.local_repo_path:
            return False
        return (self.local_repo_path / repo_relative_path).exists()
    
    def commit_and_push(self, message: str) -> bool:
        """
        Commit 并 Push 更改
        
        Args:
            message: Commit 消息
            
        Returns:
            是否成功
        """
        if not self.local_repo_path:
            raise RuntimeError("请先调用 clone()")
        
        # git add .
        result = subprocess.run(
            ['git', 'add', '.'],
            cwd=self.local_repo_path,
            capture_output=True,
            text=True
        )
        
        # 检查是否有更改
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=self.local_repo_path,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            logger.info("没有更改需要提交")
            return True
        
        # git commit
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=self.local_repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Commit 失败: {result.stderr}")
            return False
        
        logger.info(f"Commit 成功: {message}")
        
        # git push
        result = subprocess.run(
            ['git', 'push', 'origin', self.branch],
            cwd=self.local_repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            logger.error(f"Push 失败: {result.stderr}")
            return False
        
        logger.info(f"Push 成功: {self.owner}/{self.repo}@{self.branch}")
        
        return True
    
    def cleanup(self):
        """清理本地仓库"""
        if self.local_repo_path and self.local_repo_path.exists():
            shutil.rmtree(self.local_repo_path)
            logger.info(f"已清理本地仓库: {self.local_repo_path}")
            self.local_repo_path = None
    
    def get_full_path(self, repo_relative_path: str) -> Path:
        """获取仓库内文件的完整本地路径"""
        if not self.local_repo_path:
            raise RuntimeError("请先调用 clone()")
        return self.local_repo_path / repo_relative_path


# 便捷函数
def create_repo_manager(config: Dict) -> GitHubRepoManager:
    """创建仓库管理器"""
    return GitHubRepoManager(config)
