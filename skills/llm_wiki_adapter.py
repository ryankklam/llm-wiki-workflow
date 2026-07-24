"""
LLM Wiki Adapter - 将视频字幕转换为 llm-wiki 格式

按照 llm-wiki SKILL 规范生成：
- raw/rednote/video/      - 原始视频文件
- raw/rednote/subtitle/   - 校正后的字幕Markdown
- wiki/sources/           - 来源摘要页
- wiki/index.md           - 索引更新
- wiki/overview.md        - 概览更新
- wiki/log.md             - 日志追加

文件命名规则：{日期}-{视频标题}_{小红书链接ID}
  例如：2026-05-10-skill实战_从0到1写一个你自己的skill_4iELqFXf4C0.md

支持两种模式：
- 本地模式：直接写入本地 wiki_root 目录
- 远程仓库模式：clone GitHub 仓库，更新后 commit & push
"""

import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# 导入仓库管理器
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.github_repo_manager import GitHubRepoManager

logger = logging.getLogger(__name__)


@dataclass
class LLMWikiIngestResult:
    """llm-wiki ingest 结果"""
    success: bool
    wiki_root: str
    video_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    source_page: Optional[str] = None
    created_pages: List[str] = field(default_factory=list)
    updated_pages: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    error: Optional[str] = None


class LLMWikiAdapter:
    """
    llm-wiki 适配器
    
    将视频字幕内容转换为 llm-wiki 格式的知识库结构
    """
    
    def __init__(self, config: Dict):
        """
        初始化适配器
        
        Args:
            config: 配置字典，需要包含 ingestion.custom_skill 配置
        """
        self.config = config
        self.ingestion_config = config.get('ingestion', {}).get('custom_skill', {})
        
        # 远程仓库配置
        remote_config = self.ingestion_config.get('remote_repo', {})
        self.use_remote_repo = remote_config.get('enabled', False)
        self.repo_manager: Optional[GitHubRepoManager] = None
        
        # 本地路径配置
        self.wiki_root = Path(self.ingestion_config.get('wiki_root', '~/llm-wiki')).expanduser()
        self.video_subdir = self.ingestion_config.get('video_subdir', 'raw/rednote/video')
        self.subtitle_subdir = self.ingestion_config.get('subtitle_subdir', 'raw/rednote/subtitle')
        self.sources_subdir = self.ingestion_config.get('sources_subdir', 'wiki/sources')
        self.create_entities = self.ingestion_config.get('create_entities', True)
        self.create_concepts = self.ingestion_config.get('create_concepts', True)
        self.update_overview = self.ingestion_config.get('update_overview', True)
        self.append_log = self.ingestion_config.get('append_log', True)
        
        if self.use_remote_repo:
            self.repo_manager = GitHubRepoManager(self.ingestion_config)
            logger.info(f"LLM Wiki Adapter 初始化完成，模式: 远程仓库 ({remote_config.get('github_owner')}/{remote_config.get('github_repo')}@{remote_config.get('branch')})")
        else:
            logger.info(f"LLM Wiki Adapter 初始化完成，模式: 本地目录 ({self.wiki_root})")
    
    def ingest(self,
               video_path: str,
               subtitle_content: str,
               video_info: Dict,
               corrected_content: Optional[str] = None) -> LLMWikiIngestResult:
        """
        执行 llm-wiki 格式的 ingest
        
        Args:
            video_path: 原始视频文件路径
            subtitle_content: 原始字幕内容
            video_info: 视频信息字典（需包含 original_url 用于提取ID）
            corrected_content: 校正后的内容（可选）
            
        Returns:
            LLMWikiIngestResult 对象
        """
        result = LLMWikiIngestResult(success=False, wiki_root=str(self.wiki_root))
        
        try:
            # 远程仓库模式：clone 仓库
            if self.use_remote_repo and self.repo_manager:
                logger.info("[远程仓库模式] 正在 clone 仓库...")
                local_repo_path = self.repo_manager.clone()
                self.wiki_root = local_repo_path  # 更新 wiki_root 为 clone 的路径
                result.wiki_root = str(local_repo_path)
            
            # 从链接提取ID
            video_id = self._extract_video_id(video_info.get('original_url', ''))
            platform = self._detect_platform(video_info.get('original_url', ''))

            # 生成统一文件名: {日期}-{标题}_{ID}
            date_str = datetime.now().strftime('%Y-%m-%d')
            safe_title = self._sanitize_filename(video_info.get('title', 'unknown'))[:40]
            base_filename = f"{date_str}-{safe_title}_{video_id}"

            # 确保目录结构存在
            self._ensure_directory_structure()

            # Step 1: 保存原始视频
            saved_video_path = self._save_video(video_path, base_filename)
            result.video_path = saved_video_path
            logger.info(f"[Step 1] 视频已保存: {saved_video_path}")

            # Step 2: 保存校正后的字幕
            saved_subtitle_path = self._save_subtitle(corrected_content, base_filename, video_info)
            result.subtitle_path = saved_subtitle_path
            result.created_pages.append(saved_subtitle_path)
            logger.info(f"[Step 2] 字幕已保存: {saved_subtitle_path}")

            # Step 3: 创建来源摘要页
            source_page_path = self._create_source_page(
                video_info, subtitle_content, corrected_content,
                saved_video_path, saved_subtitle_path
            )
            result.source_page = source_page_path
            result.created_pages.append(source_page_path)
            logger.info(f"[Step 3] 来源摘要页已创建: {source_page_path}")

            # Step 4: 提取实体和概念
            entities, concepts = self._extract_entities_and_concepts(
                corrected_content or subtitle_content, video_info
            )
            result.entities = entities
            result.concepts = concepts
            logger.info(f"[Step 4] 提取实体: {entities}, 概念: {concepts}")

            # Step 5: 创建/更新实体页和概念页
            if self.create_entities:
                for entity in entities:
                    entity_path = self._create_or_update_entity(entity, video_info, source_page_path)
                    if entity_path:
                        result.created_pages.append(entity_path)

            if self.create_concepts:
                for concept in concepts:
                    concept_path = self._create_or_update_concept(concept, video_info, source_page_path)
                    if concept_path:
                        result.created_pages.append(concept_path)

            logger.info(f"[Step 5] 实体/概念页已更新")

            # Step 6: 更新 index.md
            self._update_index(video_info, source_page_path, entities, concepts)
            result.updated_pages.append(str(self.wiki_root / 'wiki' / 'index.md'))
            logger.info(f"[Step 6] index.md 已更新")

            # Step 7: 更新 overview.md
            if self.update_overview:
                self._update_overview(len(result.created_pages))
                result.updated_pages.append(str(self.wiki_root / 'wiki' / 'overview.md'))
                logger.info(f"[Step 7] overview.md 已更新")

            # Step 8: 追加 log.md
            if self.append_log:
                self._append_log(video_info, result.created_pages, result.updated_pages)
                result.updated_pages.append(str(self.wiki_root / 'wiki' / 'log.md'))
                logger.info(f"[Step 8] log.md 已追加")

            # Step 9: 远程仓库模式 - Commit & Push
            if self.use_remote_repo and self.repo_manager:
                commit_message = f"Add: {video_info.get('title', 'new video')} [{video_id}]"
                logger.info(f"[Step 9] 正在 commit & push...")
                if self.repo_manager.commit_and_push(commit_message):
                    logger.info(f"[Step 9] 已推送到远程仓库")
                else:
                    logger.warning(f"[Step 9] Push 失败，请检查网络或权限")
            
            result.success = True
            logger.info("llm-wiki ingest 完成")
            
        except Exception as e:
            logger.error(f"llm-wiki ingest 失败: {e}")
            result.error = str(e)
        
        return result
    
    def _ensure_directory_structure(self):
        """确保 llm-wiki 目录结构存在"""
        dirs = [
            self.wiki_root / self.video_subdir,
            self.wiki_root / self.subtitle_subdir,
            self.wiki_root / 'wiki' / 'sources',
            self.wiki_root / 'wiki' / 'entities',
            self.wiki_root / 'wiki' / 'concepts',
            self.wiki_root / 'wiki' / 'topics',
            self.wiki_root / 'wiki' / 'solutions',
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            logger.debug(f"确保目录存在: {d}")

    def _detect_platform(self, url: str) -> str:
        """
        检测视频链接的平台
        """
        if not url:
            return 'unknown'
        url_lower = url.lower()
        if any(p in url_lower for p in ['xhslink.com', 'xiaohongshu.com', 'xhs.cn']):
            return 'xiaohongshu'
        if any(p in url_lower for p in ['douyin.com', 'v.douyin.com', 'iesdouyin.com']):
            return 'douyin'
        if any(p in url_lower for p in ['bilibili.com', 'b23.tv', 'bilibili.tv']):
            return 'bilibili'
        return 'unknown'

    def _extract_video_id(self, url: str) -> str:
        """
        从链接中提取视频ID（支持多平台）
        
        支持格式:
        - 小红书: http://xhslink.com/o/4iELqFXf4C0
        - Bilibili: https://www.bilibili.com/video/BV1xx411c7mD
        - Bilibili短链: https://b23.tv/xxxxx
        
        Returns:
            提取的ID字符串
        """
        if not url:
            return 'unknown'

        platform = self._detect_platform(url)

        if platform == 'xiaohongshu':
            # xhslink.com/o/ID 格式
            match = re.search(r'xhslink\.com/[oa]/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)
            # xiaohongshu.com/explore/ID 或 /discovery/item/ID
            match = re.search(r'xiaohongshu\.com/(?:explore|discovery/item)/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)

        elif platform == 'bilibili':
            # BV号
            match = re.search(r'/BV([a-zA-Z0-9]+)', url)
            if match:
                return f"BV{match.group(1)}"
            # AV号
            match = re.search(r'/av(\d+)', url)
            if match:
                return f"av{match.group(1)}"
            # b23.tv短链
            match = re.search(r'b23\.tv/([a-zA-Z0-9]+)', url)
            if match:
                return match.group(1)

        elif platform == 'douyin':
            match = re.search(r'v\.douyin\.com/([a-zA-Z0-9]+)/?', url)
            if match:
                return match.group(1)
            match = re.search(r'douyin\.com/video/(\d+)', url)
            if match:
                return match.group(1)

        # 通用：取URL最后一段非空路径
        parts = url.rstrip('/').split('/')
        for part in reversed(parts):
            if part and part not in ('o', 'a', 'video', 'item', 'explore', 'discovery'):
                return part

        return 'unknown'
    
    def _save_video(self, video_path: str, base_filename: str) -> str:
        """
        保存视频到 raw/rednote/video/
        
        Args:
            video_path: 原始视频路径
            base_filename: 基础文件名（不含扩展名）
            
        Returns:
            保存后的相对路径
        """
        filename = f"{base_filename}.mp4"
        target_dir = self.wiki_root / self.video_subdir
        target_path = target_dir / filename
        
        import shutil
        shutil.copy2(video_path, target_path)
        
        return f"{self.video_subdir}/{filename}"
    
    def _save_subtitle(self, corrected_content: Optional[str], base_filename: str, video_info: Dict) -> str:
        """
        保存校正后的字幕到 raw/rednote/subtitle/
        
        Args:
            corrected_content: 校正后的Markdown内容
            base_filename: 基础文件名（不含扩展名）
            video_info: 视频信息
            
        Returns:
            保存后的绝对路径
        """
        if not corrected_content:
            logger.warning("校正内容为空，跳过字幕保存")
            return ""
        
        filename = f"{base_filename}.md"
        target_dir = self.wiki_root / self.subtitle_subdir
        target_path = target_dir / filename
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        
        return str(target_path)
    
    def _create_source_page(self,
                           video_info: Dict,
                           subtitle_content: str,
                           corrected_content: Optional[str],
                           video_relative_path: str,
                           subtitle_relative_path: str = "") -> str:
        """
        创建来源摘要页 wiki/sources/YYYY-MM-DD-视频标题.md
        
        Returns:
            创建的页面路径
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        safe_title = self._sanitize_filename(video_info.get('title', 'unknown'))[:40]
        
        filename = f"{date_str}-{safe_title}.md"
        source_path = self.wiki_root / self.sources_subdir / filename
        
        # 提取关键概念（从校正后的内容中提取加粗文字）
        key_concepts = self._extract_bold_text(corrected_content or subtitle_content)[:10]
        
        # 生成内容摘要（前500字）
        content_summary = self._generate_summary(corrected_content or subtitle_content, 500)
        
        # 构建页面内容
        platform = self._detect_platform(video_info.get('original_url', ''))
        page_content = f"""---
type: source
date: {date_str}
source: {video_relative_path}
subtitle: {subtitle_relative_path}
platform: {platform}
video_id: {video_info.get('id', '')}
author: {video_info.get('uploader', 'Unknown')}
tags: [{', '.join(key_concepts)}]
---

# 来源：{video_info.get('title', 'Unknown')}

## 视频信息
- **作者**：{video_info.get('uploader', 'Unknown')}
- **发布时间**：{date_str}
- **视频链接**：{video_info.get('original_url', '')}
- **时长**：{self._format_duration(video_info.get('duration', 0))}

## 文件位置
- **视频文件**：`{video_relative_path}`
- **字幕文件**：`{subtitle_relative_path}`

## 核心要点
{self._extract_key_points(corrected_content or subtitle_content)}

## 视频内容摘要
{content_summary}

## 关键概念
{self._format_concepts_list(key_concepts)}

## 衍生概念
{self._format_derived_concepts(key_concepts)}
"""
        
        with open(source_path, 'w', encoding='utf-8') as f:
            f.write(page_content)
        
        return str(source_path)
    
    def _extract_entities_and_concepts(self, content: str, video_info: Dict) -> Tuple[List[str], List[str]]:
        """
        从内容中提取实体和概念
        
        Returns:
            (entities列表, concepts列表)
        """
        # 提取加粗的文字作为概念
        concepts = self._extract_bold_text(content)
        
        # 提取可能的人名、公司名、产品名作为实体（简单启发式）
        entities = []
        
        # 从标题和描述中提取可能的实体
        title = video_info.get('title', '')
        
        # 常见技术实体关键词
        entity_keywords = [
            'OpenAI', 'Google', 'Anthropic', 'Meta', 'Microsoft', '阿里', '腾讯', '字节',
            'Karpathy', 'Andrej', 'Elon Musk', 'Sam Altman',
            'ChatGPT', 'GPT-4', 'Claude', 'Llama', 'Gemini',
        ]
        
        for keyword in entity_keywords:
            if keyword in content or keyword in title:
                entities.append(keyword)
        
        # 去重
        entities = list(dict.fromkeys(entities))
        concepts = list(dict.fromkeys(concepts))
        
        return entities, concepts
    
    def _create_or_update_entity(self, entity: str, video_info: Dict, source_page: str) -> Optional[str]:
        """创建或更新实体页"""
        safe_name = self._sanitize_filename(entity)
        entity_path = self.wiki_root / 'wiki' / 'entities' / f"{safe_name}.md"
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        source_name = Path(source_page).stem
        
        if entity_path.exists():
            # 更新现有页面
            with open(entity_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 追加新信息
            if source_name not in content:
                content += f"\n## 新信息（{date_str}）\n\n"
                content += f"来自 [[{source_name}]]：{video_info.get('title', '')}\n"
                
                with open(entity_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return str(entity_path)
        else:
            # 创建新页面
            page_content = f"""---
type: entity
created: {date_str}
updated: {date_str}
sources: [{source_name}]
---

# {entity}

## 定义
关于 {entity} 的简要描述。

## 关键信息
- 相关信息（来源：[[{source_name}]]）

## 关联
- 相关概念：

## 开放问题
- 
"""
            with open(entity_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            return str(entity_path)
        
        return None
    
    def _create_or_update_concept(self, concept: str, video_info: Dict, source_page: str) -> Optional[str]:
        """创建或更新概念页"""
        safe_name = self._sanitize_filename(concept)
        concept_path = self.wiki_root / 'wiki' / 'concepts' / f"{safe_name}.md"
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        source_name = Path(source_page).stem
        
        if concept_path.exists():
            # 更新现有页面
            with open(concept_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 追加新信息
            if source_name not in content:
                content += f"\n## 补充说明（{date_str}）\n\n"
                content += f"来自 [[{source_name}]]：关于 {concept} 的新视角。\n"
                
                # 更新 updated 字段
                content = re.sub(
                    r'updated: \d{4}-\d{2}-\d{2}',
                    f'updated: {date_str}',
                    content
                )
                
                with open(concept_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return str(concept_path)
        else:
            # 创建新页面
            page_content = f"""---
type: concept
created: {date_str}
updated: {date_str}
sources: [{source_name}]
---

# {concept}

## 定义
{concept} 的定义和解释。

## 关键信息
- 核心要点（来源：[[{source_name}]]）

## 关联
- 相关概念：
- 相关实体：

## 开放问题
- 
"""
            with open(concept_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
            
            return str(concept_path)
        
        return None
    
    def _update_index(self, video_info: Dict, source_page: str, entities: List[str], concepts: List[str]):
        """更新 wiki/index.md"""
        index_path = self.wiki_root / 'wiki' / 'index.md'
        date_str = datetime.now().strftime('%Y-%m-%d')
        source_name = Path(source_page).stem
        title = video_info.get('title', 'Unknown')
        
        # 构建新条目
        new_entry = f"- **{date_str}** [{title}]([[{source_name}]])\n"
        
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在"来源"部分插入新条目
            if '## 来源' in content:
                # 在 ## 来源 后面插入
                content = content.replace(
                    '## 来源',
                    f'## 来源\n\n{new_entry}'
                )
            else:
                content += f"\n## 来源\n\n{new_entry}\n"
        else:
            # 创建新的 index.md
            content = f"""# Wiki Index

## 概览
- [[overview]] - 整体综述

## 来源
{new_entry}

## 实体
<!-- 人物、组织、产品等 -->

## 概念
<!-- 理论、方法、术语等 -->

## 主题
<!-- 综合分析、比较等 -->

## 经验
<!-- 解决问题的经验 -->
"""
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _update_overview(self, new_pages_count: int):
        """更新 wiki/overview.md"""
        overview_path = self.wiki_root / 'wiki' / 'overview.md'
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        if overview_path.exists():
            with open(overview_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新统计信息
            # 来源数量 +1
            content = re.sub(
                r'来源数量：(\d+)',
                lambda m: f'来源数量：{int(m.group(1)) + 1}',
                content
            )
            
            # 总页面数
            content = re.sub(
                r'总页面数：(\d+)',
                lambda m: f'总页面数：{int(m.group(1)) + new_pages_count}',
                content
            )
            
            # 最近更新
            content = re.sub(
                r'最近更新：.+',
                f'最近更新：{date_str}',
                content
            )
        else:
            # 创建新的 overview.md
            content = f"""---
type: overview
created: {date_str}
---

# 知识库概览

> 本 Wiki 由 LLM 自动维护。

## 当前状态
- 来源数量：1
- 总页面数：{1 + new_pages_count}
- 最近更新：{date_str}

## 核心发现
<!-- 随着知识积累，这里将总结最重要的发现 -->
"""
        
        with open(overview_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _append_log(self, video_info: Dict, created_pages: List[str], updated_pages: List[str]):
        """追加 wiki/log.md"""
        log_path = self.wiki_root / 'wiki' / 'log.md'
        date_str = datetime.now().strftime('%Y-%m-%d')
        title = video_info.get('title', 'Unknown')
        
        # 构建相对路径
        created_names = [Path(p).stem for p in created_pages]
        updated_names = [Path(p).stem for p in updated_pages]
        
        log_entry = f"""## [{date_str}] ingest | {title}

- **来源**：{video_info.get('original_url', '')}
- **新增页面**：{', '.join(created_names)}
- **更新页面**：{', '.join(updated_names)}
- **影响范围**：{len(created_pages) + len(updated_pages)} 个页面

"""
        
        if log_path.exists():
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            content += log_entry
        else:
            content = f"# Wiki Log\n\n{log_entry}"
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # ============ 工具方法 ============
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名"""
        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        filename = filename.strip(' .')
        return filename[:50]
    
    def _format_duration(self, seconds: float) -> str:
        """格式化时长"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}分{secs}秒"
    
    def _extract_bold_text(self, content: str) -> List[str]:
        """提取加粗的文字，过滤掉非概念性内容"""
        pattern = r'\*\*(.*?)\*\*'
        matches = re.findall(pattern, content)
        
        # 过滤规则
        filtered = []
        noise_patterns = [
            r'^[\u4e00-\u9fff]{1,2}$',           # 单个或两个汉字（太短）
            r'^[\u4e00-\u9fff]{1,3}[。，！？]$',   # 带标点的短句
            r'^[""「」].*[""「」]$',               # 纯引号内容
            r'[？?！!。,，]',                       # 包含句末标点（说明是句子不是概念）
            r'^.{1,2}$',                            # 任意1-2字符
        ]
        
        for m in matches:
            m = m.strip()
            # 长度检查
            if len(m) < 2 or len(m) > 30:
                continue
            # 噪音过滤
            is_noise = any(re.search(p, m) for p in noise_patterns)
            if not is_noise:
                filtered.append(m)
        
        # 去重
        seen = set()
        unique = []
        for item in filtered:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        
        return unique[:15]
    
    def _strip_frontmatter(self, content: str) -> str:
        """剥离YAML frontmatter"""
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                return content[end + 3:].strip()
        return content
    
    def _generate_summary(self, content: str, max_length: int = 500) -> str:
        """生成内容摘要"""
        # 先剥离frontmatter
        content = self._strip_frontmatter(content)
        
        # 移除Markdown标记
        text = re.sub(r'\[.*?\]', '', content)  # 移除链接
        text = re.sub(r'[#*`_]', '', text)  # 移除格式标记
        text = re.sub(r'\n+', ' ', text)  # 合并换行
        text = text.strip()
        
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    def _extract_key_points(self, content: str) -> str:
        """提取关键要点"""
        lines = content.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            # 寻找列表项或标题
            if line.startswith('- ') or line.startswith('## ') or line.startswith('### '):
                clean = re.sub(r'^[-#\s]+', '', line)
                if clean and len(clean) > 10:
                    key_points.append(f"- {clean[:100]}")
            if len(key_points) >= 5:
                break
        
        return '\n'.join(key_points) if key_points else "- 详见视频内容"
    
    def _format_concepts_list(self, concepts: List[str]) -> str:
        """格式化概念列表"""
        if not concepts:
            return "- 待补充"
        return '\n'.join([f"- [[{c}]]" for c in concepts[:10]])
    
    def _format_derived_concepts(self, concepts: List[str]) -> str:
        """格式化衍生概念"""
        if not concepts:
            return "- 待创建"
        return '\n'.join([f"- [[{c}]]" for c in concepts[:5]])


# 便捷函数
def ingest_to_llm_wiki(video_path: str,
                       subtitle_content: str,
                       video_info: Dict,
                       config: Dict,
                       corrected_content: Optional[str] = None) -> LLMWikiIngestResult:
    """
    便捷函数：将视频内容 ingest 到 llm-wiki
    
    Args:
        video_path: 视频文件路径
        subtitle_content: 原始字幕内容
        video_info: 视频信息
        config: 配置字典
        corrected_content: 校正后的内容（可选）
        
    Returns:
        LLMWikiIngestResult 对象
    """
    adapter = LLMWikiAdapter(config)
    return adapter.ingest(video_path, subtitle_content, video_info, corrected_content)
