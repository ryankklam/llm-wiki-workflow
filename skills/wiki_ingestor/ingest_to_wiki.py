"""
Wiki Ingestion Skill - 将字幕内容集成到LLM Wiki
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from github import Github
from github.GithubException import GithubException

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Ingestion结果数据类"""
    updated_files: List[str] = field(default_factory=list)
    summary: str = ""
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)


class WikiIngestor:
    """Wiki内容Ingestor"""
    
    def __init__(self, config: Dict = None):
        """
        初始化Ingestor
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.wiki_config = self.config.get('wiki', {})
        self.github_config = self.config.get('github', {})
        
        # 加载Skill配置
        self.skill_config = self._load_skill_config()
        
        # GitHub客户端
        self.github = None
        self.repo = None
        
    def _load_skill_config(self) -> Dict:
        """加载Skill配置文件"""
        skill_path = Path(__file__).parent / "skill.yaml"
        if skill_path.exists():
            with open(skill_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _init_github(self):
        """初始化GitHub连接"""
        if self.github is not None:
            return
        
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            raise RuntimeError("未设置GITHUB_TOKEN环境变量")
        
        repo_owner = self.github_config.get('repo_owner')
        repo_name = self.github_config.get('repo_name')
        
        if not repo_owner or not repo_name:
            raise RuntimeError("GitHub配置不完整")
        
        self.github = Github(token)
        self.repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
        logger.info(f"Wiki Ingestor已连接到: {repo_owner}/{repo_name}")
    
    def ingest(self,
               subtitle_content: str,
               video_info: Dict,
               github_url: str) -> IngestionResult:
        """
        执行Ingestion流程
        
        Args:
            subtitle_content: 校正后的字幕内容
            video_info: 视频信息
            github_url: GitHub文件URL
            
        Returns:
            IngestionResult对象
        """
        self._init_github()
        
        result = IngestionResult()
        
        logger.info(f"开始Ingest内容: {video_info.get('title', 'Unknown')}")
        
        # 1. 提取关键词
        if self.skill_config.get('parameters', {}).get('extract_keywords', {}).get('default', True):
            result.keywords = self._extract_keywords(subtitle_content)
            logger.info(f"提取关键词: {result.keywords}")
        
        # 2. 确定分类
        result.categories = self._categorize_content(subtitle_content, video_info)
        logger.info(f"内容分类: {result.categories}")
        
        # 3. 更新索引文件
        if self._update_main_index(video_info, github_url, result.categories):
            result.updated_files.append('index.md')
        
        # 4. 更新分类索引
        for category in result.categories:
            if self._update_category_index(category, video_info, github_url):
                result.updated_files.append(f"categories/{category}.md")
        
        # 5. 更新标签云
        if result.keywords:
            if self._update_tag_cloud(result.keywords, video_info, github_url):
                result.updated_files.append('tags.md')
        
        # 6. 更新时间线
        if self._update_timeline(video_info, github_url):
            result.updated_files.append('timeline.md')
        
        # 生成摘要
        result.summary = self._generate_summary(video_info, result)
        
        logger.info(f"Ingestion完成，更新了 {len(result.updated_files)} 个文件")
        return result
    
    def _extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """
        从内容中提取关键词
        
        Args:
            content: 内容文本
            max_keywords: 最大关键词数量
            
        Returns:
            关键词列表
        """
        # 简单的关键词提取逻辑
        # 实际应用中可以使用NLP库如jieba、spaCy等
        
        keywords = []
        
        # 提取加粗的文字作为关键词
        bold_pattern = r'\*\*(.*?)\*\*'
        bold_words = re.findall(bold_pattern, content)
        keywords.extend([w.strip() for w in bold_words if len(w.strip()) > 1])
        
        # 提取代码标记的内容
        code_pattern = r'`([^`]+)`'
        code_words = re.findall(code_pattern, content)
        keywords.extend([w.strip() for w in code_words if len(w.strip()) > 1])
        
        # 去重并限制数量
        keywords = list(dict.fromkeys(keywords))[:max_keywords]
        
        return keywords
    
    def _categorize_content(self, content: str, video_info: Dict) -> List[str]:
        """
        对内容进行分类
        
        Args:
            content: 内容文本
            video_info: 视频信息
            
        Returns:
            分类列表
        """
        categories = []
        content_lower = content.lower()
        title_lower = video_info.get('title', '').lower()
        
        # 定义分类关键词
        category_keywords = {
            '技术': ['代码', '编程', '开发', 'python', 'javascript', 'ai', '算法', 
                   '技术', '工程', '软件', '系统', '架构', '数据库'],
            'AI': ['人工智能', '机器学习', '深度学习', '神经网络', '大模型', 
                   'llm', 'gpt', 'ai', 'machine learning', '神经网络'],
            '生活': ['生活', '日常', 'vlog', '美食', '旅行', '家居', '健康'],
            '学习': ['学习', '教程', '课程', '知识', '读书', '笔记', '方法'],
            '职场': ['职场', '工作', '面试', '简历', '职业发展', '管理'],
            '创业': ['创业', '商业', '产品', '运营', '市场', '投资'],
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in content_lower or kw in title_lower for kw in keywords):
                categories.append(category)
        
        # 如果没有匹配到分类，使用默认分类
        if not categories:
            categories.append('其他')
        
        return categories
    
    def _update_main_index(self, 
                          video_info: Dict, 
                          github_url: str,
                          categories: List[str]) -> bool:
        """
        更新主索引文件
        
        Args:
            video_info: 视频信息
            github_url: GitHub URL
            categories: 分类列表
            
        Returns:
            是否成功更新
        """
        try:
            index_file = 'index.md'
            branch = self.github_config.get('branch', 'main')
            
            # 尝试获取现有内容
            try:
                file_content = self.repo.get_contents(index_file, ref=branch)
                content = file_content.decoded_content.decode('utf-8')
                sha = file_content.sha
            except GithubException as e:
                if e.status == 404:
                    # 创建新索引文件
                    content = self._create_default_index()
                    sha = None
                else:
                    raise
            
            # 添加新条目
            new_entry = self._format_index_entry(video_info, github_url, categories)
            
            # 找到最新内容位置并插入
            if '## 最新内容' in content:
                # 在最新内容部分插入
                parts = content.split('## 最新内容', 1)
                content = parts[0] + '## 最新内容\n\n' + new_entry + '\n' + parts[1].split('\n\n', 1)[1] if '\n\n' in parts[1] else parts[1]
            else:
                content += f"\n## 最新内容\n\n{new_entry}\n"
            
            # 提交更新
            commit_msg = f"Add to index: {video_info.get('title', 'New content')}"
            
            if sha:
                self.repo.update_file(index_file, commit_msg, content, sha, branch=branch)
            else:
                self.repo.create_file(index_file, commit_msg, content, branch=branch)
            
            logger.info(f"主索引已更新: {index_file}")
            return True
            
        except Exception as e:
            logger.warning(f"更新主索引失败: {e}")
            return False
    
    def _update_category_index(self, 
                               category: str,
                               video_info: Dict,
                               github_url: str) -> bool:
        """
        更新分类索引
        
        Args:
            category: 分类名称
            video_info: 视频信息
            github_url: GitHub URL
            
        Returns:
            是否成功更新
        """
        try:
            category_file = f"categories/{category}.md"
            branch = self.github_config.get('branch', 'main')
            
            # 尝试获取现有内容
            try:
                file_content = self.repo.get_contents(category_file, ref=branch)
                content = file_content.decoded_content.decode('utf-8')
                sha = file_content.sha
            except GithubException as e:
                if e.status == 404:
                    # 创建新分类文件
                    content = f"# {category} 分类\n\n本分类下的所有内容。\n\n"
                    sha = None
                else:
                    raise
            
            # 添加新条目
            new_entry = self._format_index_entry(video_info, github_url, [])
            content += new_entry + '\n'
            
            # 提交更新
            commit_msg = f"Add to {category}: {video_info.get('title', 'New content')}"
            
            if sha:
                self.repo.update_file(category_file, commit_msg, content, sha, branch=branch)
            else:
                self.repo.create_file(category_file, commit_msg, content, branch=branch)
            
            logger.info(f"分类索引已更新: {category_file}")
            return True
            
        except Exception as e:
            logger.warning(f"更新分类索引失败: {e}")
            return False
    
    def _update_tag_cloud(self, 
                         keywords: List[str],
                         video_info: Dict,
                         github_url: str) -> bool:
        """
        更新标签云
        
        Args:
            keywords: 关键词列表
            video_info: 视频信息
            github_url: GitHub URL
            
        Returns:
            是否成功更新
        """
        try:
            tags_file = 'tags.md'
            branch = self.github_config.get('branch', 'main')
            
            # 尝试获取现有内容
            try:
                file_content = self.repo.get_contents(tags_file, ref=branch)
                content = file_content.decoded_content.decode('utf-8')
                sha = file_content.sha
            except GithubException as e:
                if e.status == 404:
                    content = "# 标签云\n\n"
                    sha = None
                else:
                    raise
            
            # 为每个关键词添加引用
            for keyword in keywords:
                tag_section = f"## {keyword}"
                entry = f"- [{video_info.get('title', 'Content')}]({github_url})"
                
                if tag_section in content:
                    # 在现有标签下添加
                    content = content.replace(
                        tag_section,
                        f"{tag_section}\n{entry}"
                    )
                else:
                    # 创建新标签
                    content += f"\n{tag_section}\n\n{entry}\n"
            
            # 提交更新
            commit_msg = f"Update tags for: {video_info.get('title', 'New content')}"
            
            if sha:
                self.repo.update_file(tags_file, commit_msg, content, sha, branch=branch)
            else:
                self.repo.create_file(tags_file, commit_msg, content, branch=branch)
            
            logger.info(f"标签云已更新: {tags_file}")
            return True
            
        except Exception as e:
            logger.warning(f"更新标签云失败: {e}")
            return False
    
    def _update_timeline(self, 
                        video_info: Dict,
                        github_url: str) -> bool:
        """
        更新时间线
        
        Args:
            video_info: 视频信息
            github_url: GitHub URL
            
        Returns:
            是否成功更新
        """
        try:
            timeline_file = 'timeline.md'
            branch = self.github_config.get('branch', 'main')
            date_str = datetime.now().strftime('%Y-%m-%d')
            
            # 尝试获取现有内容
            try:
                file_content = self.repo.get_contents(timeline_file, ref=branch)
                content = file_content.decoded_content.decode('utf-8')
                sha = file_content.sha
            except GithubException as e:
                if e.status == 404:
                    content = "# 内容时间线\n\n按时间顺序排列的所有内容。\n\n"
                    sha = None
                else:
                    raise
            
            # 添加新条目
            date_section = f"## {date_str}"
            entry = f"- [{video_info.get('title', 'Content')}]({github_url})"
            
            if date_section in content:
                # 在现有日期下添加
                content = content.replace(
                    date_section,
                    f"{date_section}\n{entry}"
                )
            else:
                # 创建新日期（插入到最前面）
                content = f"# 内容时间线\n\n按时间顺序排列的所有内容。\n\n{date_section}\n\n{entry}\n\n" + content.split('\n\n', 2)[2] if '\n\n' in content else content + f"\n{date_section}\n\n{entry}\n"
            
            # 提交更新
            commit_msg = f"Update timeline: {video_info.get('title', 'New content')}"
            
            if sha:
                self.repo.update_file(timeline_file, commit_msg, content, sha, branch=branch)
            else:
                self.repo.create_file(timeline_file, commit_msg, content, branch=branch)
            
            logger.info(f"时间线已更新: {timeline_file}")
            return True
            
        except Exception as e:
            logger.warning(f"更新时间线失败: {e}")
            return False
    
    def _format_index_entry(self, 
                           video_info: Dict, 
                           github_url: str,
                           categories: List[str]) -> str:
        """
        格式化索引条目
        
        Args:
            video_info: 视频信息
            github_url: GitHub URL
            categories: 分类列表
            
        Returns:
            格式化后的条目
        """
        title = video_info.get('title', 'Unknown')
        author = video_info.get('uploader', 'Unknown')
        date = datetime.now().strftime('%Y-%m-%d')
        
        category_str = f" [{', '.join(categories)}]" if categories else ""
        
        return f"- **{date}**{category_str} [{title}]({github_url}) - by {author}"
    
    def _create_default_index(self) -> str:
        """
        创建默认索引文件内容
        
        Returns:
            默认索引内容
        """
        return """# LLM Wiki 索引

欢迎来到LLM Wiki！这里收集了从各种视频中提取和校正的知识内容。

## 分类浏览

- [技术](categories/技术.md)
- [AI](categories/AI.md)
- [生活](categories/生活.md)
- [学习](categories/学习.md)
- [职场](categories/职场.md)
- [创业](categories/创业.md)
- [其他](categories/其他.md)

## 标签云

查看 [标签云](tags.md) 按主题浏览内容。

## 时间线

查看 [时间线](timeline.md) 按时间顺序浏览内容。

## 最新内容

"""
    
    def _generate_summary(self, video_info: Dict, result: IngestionResult) -> str:
        """
        生成处理摘要
        
        Args:
            video_info: 视频信息
            result: Ingestion结果
            
        Returns:
            摘要文本
        """
        return f"""Ingestion摘要：
- 内容标题: {video_info.get('title', 'Unknown')}
- 更新文件数: {len(result.updated_files)}
- 提取关键词: {', '.join(result.keywords)}
- 内容分类: {', '.join(result.categories)}
- 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


# 便捷函数
def ingest_to_wiki(subtitle_content: str,
                   video_info: Dict,
                   github_url: str,
                   config: Dict = None) -> IngestionResult:
    """
    便捷函数：将内容Ingest到Wiki
    
    Args:
        subtitle_content: 字幕内容
        video_info: 视频信息
        github_url: GitHub URL
        config: 配置字典
        
    Returns:
        IngestionResult对象
    """
    ingestor = WikiIngestor(config)
    return ingestor.ingest(subtitle_content, video_info, github_url)
