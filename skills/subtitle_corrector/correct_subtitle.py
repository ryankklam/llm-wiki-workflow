"""
字幕校正Skill - 使用LLM对字幕进行校正和优化

支持两种模式：
- EXTERNAL: 调用OpenAI兼容API（需要配置OPENAI_API_KEY）
- INTERNAL: 使用SOLO内置LLM能力（无需API Key，由SOLO自身完成校正）
"""

import os
import re
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Callable
from dataclasses import dataclass

# 尝试导入OpenAI
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


@dataclass
class CorrectionResult:
    """校正结果数据类"""
    corrected_text: str
    changes_summary: str
    tokens_used: int
    model: str


class SubtitleCorrector:
    """字幕校正器"""
    
    # 校正模式常量
    MODE_EXTERNAL = "EXTERNAL"  # 使用OpenAI API
    MODE_INTERNAL = "INTERNAL"  # 使用SOLO内置LLM
    
    def __init__(self, config: Dict = None, internal_corrector: Callable = None):
        """
        初始化校正器
        
        Args:
            config: 配置字典
            internal_corrector: INTERNAL模式的校正回调函数。
                签名: (subtitle_text: str, video_title: str, video_description: str) -> str
                返回校正后的文本。
                如果不提供，INTERNAL模式下将抛出NotImplementedError。
        """
        self.config = config or {}
        self.correction_config = self.config.get('correction', {})
        
        # 校正模式
        self.mode = self.correction_config.get('mode', 'EXTERNAL').upper()
        if self.mode not in (self.MODE_EXTERNAL, self.MODE_INTERNAL):
            raise ValueError(
                f"无效的correction.mode: '{self.mode}'，"
                f"必须是 '{self.MODE_EXTERNAL}' 或 '{self.MODE_INTERNAL}'"
            )
        
        # INTERNAL模式的回调
        self._internal_corrector = internal_corrector
        
        # 加载Skill配置
        self.skill_config = self._load_skill_config()
        
        # 模型配置（EXTERNAL模式使用）
        self.model = self.correction_config.get('model') or self.skill_config.get('parameters', {}).get('model', {}).get('default', 'gpt-4o')
        self.temperature = self.correction_config.get('temperature') or self.skill_config.get('parameters', {}).get('temperature', {}).get('default', 0.3)
        self.max_tokens = self.correction_config.get('max_tokens') or self.skill_config.get('parameters', {}).get('max_tokens', {}).get('default', 4000)
        
        # 加载prompt模板
        self.prompt_template = self._load_prompt_template()
        
        # EXTERNAL模式：初始化OpenAI客户端
        self.client = None
        if self.mode == self.MODE_EXTERNAL:
            self.client = self._init_openai_client()
        
        logger.info(f"字幕校正器初始化完成，模式: {self.mode}")
    
    def _load_skill_config(self) -> Dict:
        """加载Skill配置文件"""
        skill_path = Path(__file__).parent / "skill.yaml"
        if skill_path.exists():
            with open(skill_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _init_openai_client(self) -> Optional[OpenAI]:
        """初始化OpenAI客户端"""
        if OpenAI is None:
            raise RuntimeError("EXTERNAL模式需要openai库，请运行: pip install openai")
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError(
                "EXTERNAL模式需要设置OPENAI_API_KEY环境变量。"
                "如需使用内置LLM校正，请将correction.mode设为'INTERNAL'。"
            )
        
        base_url = os.getenv('OPENAI_BASE_URL')
        
        client_kwargs = {'api_key': api_key}
        if base_url:
            client_kwargs['base_url'] = base_url
        
        return OpenAI(**client_kwargs)
    
    def _load_prompt_template(self) -> str:
        """加载prompt模板"""
        # 首先尝试从配置文件加载
        template = self.correction_config.get('prompt_template')
        if template:
            return template
        
        # 从skill配置加载
        skill_template = self.skill_config.get('prompt_template')
        if skill_template:
            return skill_template
        
        # 默认模板
        return """你是一位专业的字幕编辑和文案优化专家。请对以下从视频中提取的字幕进行校正和优化：

视频标题：{video_title}

原始字幕：
{subtitle_text}

请完成以下任务：
1. 修正语音识别错误（同音字、专有名词等）
2. 将口语化表达转为流畅的书面语
3. 优化标点符号使用
4. 重组段落结构，使其更易阅读
5. 保留关键的时间戳信息

输出格式要求：
- 使用Markdown格式
- 保留重要时间戳（格式：[MM:SS]）
- 添加适当的标题层级
- 关键概念用**粗体**标注

请直接输出校正后的内容："""
    
    def correct(self, 
                subtitle_text: str,
                video_title: str = "",
                video_description: str = "") -> CorrectionResult:
        """
        校正字幕（根据配置自动选择模式）
        
        Args:
            subtitle_text: 原始字幕文本
            video_title: 视频标题
            video_description: 视频描述
            
        Returns:
            CorrectionResult对象
        """
        if self.mode == self.MODE_INTERNAL:
            return self._correct_internal(subtitle_text, video_title, video_description)
        else:
            return self._correct_external(subtitle_text, video_title, video_description)
    
    def _correct_external(self,
                          subtitle_text: str,
                          video_title: str,
                          video_description: str) -> CorrectionResult:
        """
        EXTERNAL模式：调用OpenAI API校正字幕
        
        Args:
            subtitle_text: 原始字幕文本
            video_title: 视频标题
            video_description: 视频描述
            
        Returns:
            CorrectionResult对象
        """
        if self.client is None:
            raise RuntimeError("OpenAI客户端未初始化，请检查API密钥")
        
        logger.info(f"[EXTERNAL] 开始校正字幕，使用模型: {self.model}")
        
        # 构建prompt
        prompt = self.prompt_template.format(
            subtitle_text=subtitle_text,
            video_title=video_title or "未提供",
            video_description=video_description or "未提供"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的字幕编辑和内容优化专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            corrected_text = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # 生成修改摘要
            changes_summary = self._generate_changes_summary(subtitle_text, corrected_text)
            
            logger.info(f"[EXTERNAL] 字幕校正完成，使用token: {tokens_used}")
            
            return CorrectionResult(
                corrected_text=corrected_text,
                changes_summary=changes_summary,
                tokens_used=tokens_used,
                model=self.model
            )
            
        except Exception as e:
            logger.error(f"[EXTERNAL] 字幕校正失败: {e}")
            raise RuntimeError(f"字幕校正失败(EXTERNAL): {e}")
    
    def _correct_internal(self,
                          subtitle_text: str,
                          video_title: str,
                          video_description: str) -> CorrectionResult:
        """
        INTERNAL模式：使用SOLO内置LLM能力校正字幕
        
        Args:
            subtitle_text: 原始字幕文本
            video_title: 视频标题
            video_description: 视频描述
            
        Returns:
            CorrectionResult对象
        """
        logger.info("[INTERNAL] 开始使用内置LLM校正字幕")
        
        if self._internal_corrector is None:
            raise NotImplementedError(
                "INTERNAL模式需要提供 internal_corrector 回调函数。"
                "请在创建SubtitleCorrector时传入 internal_corrector 参数，"
                "或通过 set_internal_corrector() 方法设置。"
            )
        
        try:
            # 调用内置LLM校正
            corrected_text = self._internal_corrector(
                subtitle_text, video_title, video_description
            )
            
            if not corrected_text or not corrected_text.strip():
                raise RuntimeError("内置LLM返回了空结果")
            
            # 估算token数（中文约1.5字/token）
            tokens_used = int(len(subtitle_text) / 1.5) + int(len(corrected_text) / 1.5)
            
            # 生成修改摘要
            changes_summary = self._generate_changes_summary(subtitle_text, corrected_text)
            
            logger.info(f"[INTERNAL] 字幕校正完成")
            
            return CorrectionResult(
                corrected_text=corrected_text,
                changes_summary=changes_summary,
                tokens_used=tokens_used,
                model="SOLO-internal"
            )
            
        except Exception as e:
            logger.error(f"[INTERNAL] 字幕校正失败: {e}")
            raise RuntimeError(f"字幕校正失败(INTERNAL): {e}")
    
    def set_internal_corrector(self, callback: Callable):
        """
        设置INTERNAL模式的校正回调函数
        
        Args:
            callback: 回调函数，签名:
                (subtitle_text: str, video_title: str, video_description: str) -> str
        """
        self._internal_corrector = callback
        logger.info("已设置INTERNAL模式校正回调函数")
    
    def _generate_changes_summary(self, original: str, corrected: str) -> str:
        """
        生成修改摘要
        
        Args:
            original: 原始文本
            corrected: 校正后文本
            
        Returns:
            修改摘要
        """
        original_lines = len(original.split('\n'))
        corrected_lines = len(corrected.split('\n'))
        original_chars = len(original)
        corrected_chars = len(corrected)
        
        summary = f"""校正摘要：
- 校正模式：{self.mode}
- 原始文本：{original_lines} 行，{original_chars} 字符
- 校正后：{corrected_lines} 行，{corrected_chars} 字符
- 字符变化：{corrected_chars - original_chars:+d}
- 主要改进：修正语音识别错误、优化口语表达、规范标点符号、重组内容结构
"""
        return summary
    
    def correct_segments(self, 
                         segments: list,
                         video_info: Dict = None) -> CorrectionResult:
        """
        校正字幕片段列表
        
        Args:
            segments: 字幕片段列表（SubtitleSegment对象）
            video_info: 视频信息字典
            
        Returns:
            CorrectionResult对象
        """
        # 将片段合并为文本
        text_parts = []
        for segment in segments:
            timestamp = segment.start_formatted
            text_parts.append(f"[{timestamp}] {segment.text}")
        
        subtitle_text = '\n'.join(text_parts)
        
        video_title = video_info.get('title', '') if video_info else ''
        video_description = video_info.get('description', '') if video_info else ''
        
        return self.correct(subtitle_text, video_title, video_description)
    
    def save_corrected_markdown(self, 
                                result: CorrectionResult,
                                video_info: Dict,
                                output_path: str):
        """
        保存校正后的Markdown文件
        
        Args:
            result: 校正结果
            video_info: 视频信息
            output_path: 输出文件路径
        """
        # 构建完整的Markdown内容
        lines = []
        
        # YAML前置元数据
        lines.append("---")
        lines.append(f"title: {video_info.get('title', 'Unknown')}")
        lines.append(f"author: {video_info.get('uploader', 'Unknown')}")
        lines.append(f"source: {video_info.get('original_url', '')}")
        lines.append(f"date: {video_info.get('upload_date', '')}")
        lines.append("type: corrected-subtitle")
        lines.append("status: corrected")
        lines.append(f"correction_model: {result.model}")
        lines.append(f"correction_mode: {self.mode}")
        lines.append(f"tokens_used: {result.tokens_used}")
        lines.append("---")
        lines.append("")
        
        # 添加校正摘要
        lines.append("## 校正信息")
        lines.append("")
        lines.append(f"```")
        lines.append(result.changes_summary)
        lines.append(f"```")
        lines.append("")
        
        # 添加校正后的内容
        lines.append(result.corrected_text)
        
        # 保存文件
        content = '\n'.join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"校正后的Markdown已保存: {output_path}")


# 便捷函数
def correct_subtitle_text(subtitle_text: str, 
                          video_title: str = "",
                          video_description: str = "",
                          config: Dict = None,
                          internal_corrector: Callable = None) -> CorrectionResult:
    """
    便捷函数：校正字幕文本
    
    Args:
        subtitle_text: 原始字幕文本
        video_title: 视频标题
        video_description: 视频描述
        config: 配置字典
        internal_corrector: INTERNAL模式的回调函数
        
    Returns:
        CorrectionResult对象
    """
    corrector = SubtitleCorrector(config, internal_corrector=internal_corrector)
    return corrector.correct(subtitle_text, video_title, video_description)
