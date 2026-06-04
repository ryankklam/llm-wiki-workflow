"""
小红书图文笔记抓取模块

支持从小红书链接抓取图文笔记（非视频）的文字和图片。
通过解析页面的 __INITIAL_STATE__ JSON 获取完整笔记数据。

功能：
1. 判断笔记类型（视频 vs 图文）
2. 提取标题、正文、标签、作者等信息
3. 下载所有高清图片
4. 生成结构化的 Markdown 文档
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

import requests

logger = logging.getLogger(__name__)


@dataclass
class NoteInfo:
    """笔记信息数据类"""
    note_id: str = ""
    note_type: str = "unknown"  # 'video', 'normal', 'unknown'
    title: str = ""
    desc: str = ""
    tags: List[str] = field(default_factory=list)
    author: str = ""
    author_id: str = ""
    liked_count: str = "0"
    collected_count: str = "0"
    comment_count: str = "0"
    image_list: List[Dict] = field(default_factory=list)  # [{'url': str, 'width': int, 'height': int}]
    source_url: str = ""


@dataclass
class ScrapedNote:
    """抓取结果数据类"""
    info: NoteInfo = None
    image_paths: List[str] = field(default_factory=list)  # 下载的图片本地路径
    markdown_path: str = ""  # 生成的 Markdown 文件路径
    success: bool = False
    error: str = ""


class RedNoteScraper:
    """小红书图文笔记抓取器"""

    DEFAULT_HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.xiaohongshu.com/',
    }

    def __init__(self, config: dict = None):
        """
        初始化抓取器

        Args:
            config: 配置字典，可包含：
                - image_dir: 图片保存目录（默认 storage/temp/images/）
                - output_dir: Markdown输出目录（默认 storage/output/）
        """
        self.config = config or {}
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def is_rednote_url(self, url: str) -> bool:
        """判断是否为小红书链接"""
        patterns = [
            r'xhslink\.com',
            r'xiaohongshu\.com',
            r'xhs\.cn',
        ]
        return any(re.search(p, url.lower()) for p in patterns)

    def extract_note_id(self, url: str) -> Optional[str]:
        """
        从URL中提取笔记ID

        Args:
            url: 小红书链接（支持短链和长链）

        Returns:
            笔记ID，如无法提取返回None
        """
        # 短链格式: xhslink.com/o/XXXXXX -> 需要请求后从重定向URL提取
        if re.search(r'xhslink\.com', url):
            return None  # 短链需要先请求才能获取ID

        # 长链格式
        match = re.search(r'xiaohongshu\.com/(?:explore|discovery/item)/([\da-f]+)', url)
        if match:
            return match.group(1)

        return None

    def fetch_note_info(self, url: str) -> NoteInfo:
        """
        抓取笔记信息（不下载图片）

        Args:
            url: 小红书笔记链接

        Returns:
            NoteInfo 对象

        Raises:
            ValueError: 无法解析页面
            requests.RequestException: 网络请求失败
        """
        logger.info(f"[抓取] 正在访问: {url}")

        resp = self.session.get(url, allow_redirects=True, timeout=15)
        resp.raise_for_status()

        final_url = resp.url
        logger.info(f"[抓取] 重定向到: {final_url}")

        # 从重定向后的URL提取笔记ID
        id_match = re.search(
            r'xiaohongshu\.com/(?:explore|discovery/item)/([\da-f]+)',
            final_url
        )
        if not id_match:
            raise ValueError(f"无法从URL提取笔记ID: {final_url}")

        note_id = id_match.group(1)
        logger.info(f"[抓取] 笔记ID: {note_id}")

        # 解析 __INITIAL_STATE__
        state_match = re.search(
            r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*</script>',
            resp.text, re.DOTALL
        )
        if not state_match:
            raise ValueError(
                "无法找到 __INITIAL_STATE__ 数据，"
                "可能需要登录或页面结构已变化"
            )

        raw_json = state_match.group(1)
        # 将 JS 的 undefined 替换为 JSON 的 null
        raw_json = re.sub(r'\bundefined\b', 'null', raw_json)

        try:
            initial_state = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"__INITIAL_STATE__ JSON 解析失败: {e}")

        # 提取笔记数据
        note_data = (
            initial_state
            .get('note', {})
            .get('noteDetailMap', {})
            .get(note_id, {})
            .get('note', {})
        )

        if not note_data:
            raise ValueError(f"笔记数据为空，ID: {note_id}")

        note_type = note_data.get('type', 'unknown')
        logger.info(f"[抓取] 笔记类型: {note_type}")

        # 提取用户信息
        user_data = note_data.get('user', {})
        interact_info = note_data.get('interactInfo', {})

        info = NoteInfo(
            note_id=note_id,
            note_type=note_type,
            title=note_data.get('title', ''),
            desc=note_data.get('desc', ''),
            tags=[t.get('name', '') for t in note_data.get('tagList', [])],
            author=user_data.get('nickname', ''),
            author_id=user_data.get('userId', ''),
            liked_count=interact_info.get('likedCount', '0'),
            collected_count=interact_info.get('collectedCount', '0'),
            comment_count=interact_info.get('commentCount', '0'),
            source_url=final_url,
        )

        # 提取图片列表（图文笔记）
        if note_type == 'normal':
            for img in note_data.get('imageList', []):
                info_list = img.get('infoList', [])
                if info_list:
                    # 取第一个（最大尺寸）
                    image_url = info_list[0].get('url', '')
                    if image_url:
                        info.image_list.append({
                            'url': image_url,
                            'width': img.get('width', 0),
                            'height': img.get('height', 0),
                        })

        logger.info(
            f"[抓取] 标题: {info.title}, "
            f"作者: {info.author}, "
            f"图片数: {len(info.image_list)}"
        )

        return info

    def download_images(
        self,
        note_info: NoteInfo,
        output_dir: str = None
    ) -> List[str]:
        """
        下载笔记中的所有图片

        Args:
            note_info: 笔记信息
            output_dir: 图片保存目录

        Returns:
            下载成功的文件路径列表
        """
        if not note_info.image_list:
            logger.warning("[下载图片] 没有图片需要下载")
            return []

        if output_dir is None:
            output_dir = self.config.get(
                'image_dir',
                'storage/temp/images'
            )

        os.makedirs(output_dir, exist_ok=True)
        downloaded = []

        for i, img_info in enumerate(note_info.image_list):
            url = img_info['url']
            # 判断扩展名
            ext = '.jpg'
            if 'png' in url.lower():
                ext = '.png'
            elif 'webp' in url.lower():
                ext = '.webp'

            filepath = os.path.join(output_dir, f'image_{i+1:02d}{ext}')

            try:
                logger.info(f"[下载图片] {i+1}/{len(note_info.image_list)}: {url[:60]}...")
                resp = self.session.get(url, timeout=30)
                resp.raise_for_status()

                with open(filepath, 'wb') as f:
                    f.write(resp.content)

                downloaded.append(filepath)
                logger.info(f"[下载图片] ✅ 已保存: {filepath}")

            except requests.RequestException as e:
                logger.error(f"[下载图片] ❌ 下载失败: {e}")

        return downloaded

    def generate_markdown(
        self,
        note_info: NoteInfo,
        image_paths: List[str] = None,
        output_path: str = None
    ) -> str:
        """
        生成结构化的 Markdown 文档

        Args:
            note_info: 笔记信息
            image_paths: 图片本地路径列表
            output_path: 输出文件路径（如果为None则不保存到文件）

        Returns:
            Markdown 内容字符串
        """
        lines = []

        # 元数据
        lines.append("---")
        lines.append(f"type: source")
        lines.append(f"date: {self._get_today()}")
        lines.append(f"platform: xiaohongshu")
        lines.append(f"note_id: {note_info.note_id}")
        lines.append(f"author: {note_info.author}")
        lines.append(f"note_type: {note_info.note_type}")
        if note_info.tags:
            lines.append(f"tags: [{', '.join(note_info.tags)}]")
        lines.append(f"source_url: {note_info.source_url}")
        lines.append("---")
        lines.append("")

        # 标题
        lines.append(f"# {note_info.title}")
        lines.append("")

        # 作者和互动数据
        lines.append(f"**作者**：{note_info.author}")
        lines.append(f"**点赞**：{note_info.liked_count} | "
                     f"**收藏**：{note_info.collected_count} | "
                     f"**评论**：{note_info.comment_count}")
        lines.append("")

        # 正文
        if note_info.desc:
            lines.append("## 正文")
            lines.append("")
            # 按换行分段
            for paragraph in note_info.desc.split('\n'):
                paragraph = paragraph.strip()
                if paragraph:
                    lines.append(paragraph)
                    lines.append("")

        # 图片
        if image_paths:
            lines.append("## 图片")
            lines.append("")
            for i, img_path in enumerate(image_paths):
                # 使用相对路径
                rel_path = os.path.relpath(img_path, os.path.dirname(output_path) if output_path else '.')
                lines.append(f"![图片{i+1}]({rel_path})")
                lines.append("")

        # 标签
        if note_info.tags:
            lines.append("## 标签")
            lines.append("")
            for tag in note_info.tags:
                lines.append(f"- #{tag}")
            lines.append("")

        content = '\n'.join(lines)

        # 保存到文件
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"[生成MD] ✅ 已保存: {output_path}")

        return content

    def scrape(
        self,
        url: str,
        output_dir: str = None,
        download_images: bool = True
    ) -> ScrapedNote:
        """
        完整抓取流程：获取信息 -> 下载图片 -> 生成Markdown

        Args:
            url: 小红书笔记链接
            output_dir: 输出目录（图片和Markdown保存在此）
            download_images: 是否下载图片

        Returns:
            ScrapedNote 对象
        """
        result = ScrapedNote()

        try:
            # 1. 获取笔记信息
            note_info = self.fetch_note_info(url)
            result.info = note_info

            # 2. 判断类型
            if note_info.note_type == 'video':
                result.error = "这是视频笔记，请使用视频下载流程"
                logger.warning(f"[抓取] {result.error}")
                return result

            if note_info.note_type != 'normal':
                result.error = f"未知的笔记类型: {note_info.note_type}"
                logger.warning(f"[抓取] {result.error}")
                return result

            # 3. 设置输出目录
            if output_dir is None:
                output_dir = self.config.get('output_dir', 'storage/temp')
            note_dir = os.path.join(
                output_dir,
                f"note_{note_info.note_id}"
            )
            os.makedirs(note_dir, exist_ok=True)

            # 4. 下载图片
            if download_images:
                image_paths = self.download_images(note_info, note_dir)
                result.image_paths = image_paths
            else:
                result.image_paths = []

            # 5. 生成 Markdown
            md_path = os.path.join(note_dir, 'content.md')
            self.generate_markdown(note_info, result.image_paths, md_path)
            result.markdown_path = md_path

            result.success = True
            logger.info(
                f"[抓取] ✅ 完成！图片: {len(result.image_paths)}张, "
                f"MD: {md_path}"
            )

        except Exception as e:
            result.error = str(e)
            logger.error(f"[抓取] ❌ 失败: {e}")

        return result

    def _get_today(self) -> str:
        """获取今天的日期字符串"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
