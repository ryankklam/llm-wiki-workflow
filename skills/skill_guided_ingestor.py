"""
Skill-Guided Ingestor - 准备数据后由LLM按SKILL.md执行ingest

职责分工：
- 本模块：clone仓库、保存视频/字幕文件、commit & push
- LLM自身：阅读内容、提取实体/概念、创建wiki页面、更新交叉引用

工作流程：
1. Clone远程仓库（或使用本地目录）
2. 保存视频到 raw/rednote/video/
3. 保存校正后的字幕到 raw/rednote/subtitle/
4. 返回准备好的数据，交由LLM执行SKILL.md的ingest流程
5. LLM完成后，调用commit_and_push提交更改
"""

import os
import re
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
        
        try:
            # 1. Clone远程仓库（如果启用）
            if self.use_remote_repo and self.repo_manager:
                logger.info("[准备] Clone远程仓库...")
                local_repo_path = self.repo_manager.clone()
                self.wiki_root = local_repo_path
                result.wiki_root = str(local_repo_path)
            
            # 2. 生成文件名
            rednote_id = self._extract_rednote_id(video_info.get('original_url', ''))
            date_str = datetime.now().strftime('%Y-%m-%d')
            safe_title = self._sanitize_filename(video_info.get('title', 'unknown'))[:40]
            base_filename = f"{date_str}-{safe_title}_{rednote_id}"
            
            # 3. 确保目录结构
            (self.wiki_root / self.video_subdir).mkdir(parents=True, exist_ok=True)
            (self.wiki_root / self.subtitle_subdir).mkdir(parents=True, exist_ok=True)
            
            # 4. 保存视频
            video_filename = f"{base_filename}.mp4"
            video_target = self.wiki_root / self.video_subdir / video_filename
            shutil.copy2(video_path, video_target)
            result.video_path = str(video_target)
            logger.info(f"[准备] 视频已保存: {self.video_subdir}/{video_filename}")
            
            # 5. 保存字幕
            subtitle_filename = f"{base_filename}.md"
            subtitle_target = self.wiki_root / self.subtitle_subdir / subtitle_filename
            with open(subtitle_target, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            result.subtitle_path = str(subtitle_target)
            logger.info(f"[准备] 字幕已保存: {self.subtitle_subdir}/{subtitle_filename}")
            
            result.corrected_content = corrected_content
            result.video_info = video_info
            result.success = True
            
            logger.info(f"[准备] 数据准备完成，wiki_root: {self.wiki_root}")
            
        except Exception as e:
            logger.error(f"[准备] 失败: {e}")
            result.error = str(e)
        
        return result
    
    def commit_and_push(self, message: str) -> bool:
        """
        步骤C：提交并推送更改（LLM完成ingest后调用）
        
        Args:
            message: Commit消息
            
        Returns:
            是否成功
        """
        if not self.use_remote_repo or not self.repo_manager:
            logger.info("[提交] 远程仓库未启用，跳过commit & push")
            return False
        
        logger.info(f"[提交] 正在 commit & push...")
        success = self.repo_manager.commit_and_push(message)
        
        if success:
            logger.info(f"[提交] 推送成功")
        else:
            logger.warning(f"[提交] 推送失败")
        
        return success
    
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
    
    def _extract_rednote_id(self, url: str) -> str:
        """从小红书链接提取ID"""
        if not url:
            return 'unknown'
        match = re.search(r'xhslink\.com/[oa]/([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
        match = re.search(r'xiaohongshu\.com/(?:explore|discovery/item)/([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
        parts = url.rstrip('/').split('/')
        for part in reversed(parts):
            if part and part not in ('o', 'a'):
                return part
        return 'unknown'
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        return filename.strip(' .')[:50]
