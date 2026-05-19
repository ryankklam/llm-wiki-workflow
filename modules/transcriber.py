"""
音频转字幕模块 - 使用Whisper将音频转为字幕
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .utils import ensure_dir, format_timestamp, TranscriptionError

logger = logging.getLogger(__name__)


@dataclass
class SubtitleSegment:
    """字幕片段数据类"""
    start: float
    end: float
    text: str
    
    @property
    def start_formatted(self) -> str:
        return format_timestamp(self.start)
    
    @property
    def end_formatted(self) -> str:
        return format_timestamp(self.end)
    
    def to_srt(self, index: int) -> str:
        """转换为SRT格式"""
        return f"{index}\n{self._format_srt_time(self.start)} --> {self._format_srt_time(self.end)}\n{self.text}\n"
    
    def to_vtt(self) -> str:
        """转换为VTT格式"""
        return f"{self._format_vtt_time(self.start)} --> {self._format_vtt_time(self.end)}\n{self.text}\n"
    
    def to_markdown(self, include_timestamp: bool = True) -> str:
        """转换为Markdown格式"""
        if include_timestamp:
            return f"[{self.start_formatted}] {self.text}"
        return self.text
    
    def _format_srt_time(self, seconds: float) -> str:
        """格式化为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_vtt_time(self, seconds: float) -> str:
        """格式化为VTT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


class AudioTranscriber:
    """音频转录器类"""
    
    def __init__(self, config: Dict):
        """
        初始化转录器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.transcription_config = config.get('transcription', {})
        self.output_dir = Path(config.get('paths', {}).get('output_dir', './storage/output'))
        ensure_dir(self.output_dir)
        
        # Whisper配置
        self.model_name = self.transcription_config.get('model', 'base')
        self.language = self.transcription_config.get('language', 'zh')
        self.device = self.transcription_config.get('device', 'cpu')
        self.compute_type = self.transcription_config.get('compute_type', 'int8')
        
        self.model = None
        
    def _load_model(self):
        """加载Whisper模型（延迟加载）"""
        if self.model is not None:
            return
        
        logger.info(f"正在加载Whisper模型: {self.model_name}")
        
        try:
            # 尝试使用faster-whisper（更快，支持GPU加速）
            from faster_whisper import WhisperModel
            
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type
            )
            self.using_faster = True
            logger.info("使用 faster-whisper 进行转录")
            
        except ImportError:
            # 回退到openai-whisper
            import whisper
            
            self.model = whisper.load_model(self.model_name)
            self.using_faster = False
            logger.info("使用 openai-whisper 进行转录")
    
    def transcribe(self, audio_path: str) -> Tuple[List[SubtitleSegment], str]:
        """
        转录音频为字幕
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            (字幕片段列表, 完整文本)
        """
        if not Path(audio_path).exists():
            raise TranscriptionError(f"音频文件不存在: {audio_path}")
        
        self._load_model()
        
        logger.info(f"开始转录音频: {audio_path}")
        
        try:
            if self.using_faster:
                segments, info = self.model.transcribe(
                    audio_path,
                    language=self.language,
                    task="transcribe",
                    beam_size=5,
                    best_of=5,
                    condition_on_previous_text=True,
                )
                
                logger.info(f"检测到语言: {info.language}, 概率: {info.language_probability:.2f}")
                
                # 转换为SubtitleSegment列表
                subtitle_segments = []
                full_text_parts = []
                
                for segment in segments:
                    sub_segment = SubtitleSegment(
                        start=segment.start,
                        end=segment.end,
                        text=segment.text.strip()
                    )
                    subtitle_segments.append(sub_segment)
                    full_text_parts.append(segment.text.strip())
                
                full_text = ' '.join(full_text_parts)
                
            else:
                # 使用openai-whisper
                result = self.model.transcribe(
                    audio_path,
                    language=self.language,
                    task="transcribe",
                    verbose=False
                )
                
                # 转换为SubtitleSegment列表
                subtitle_segments = []
                full_text_parts = []
                
                for seg in result.get('segments', []):
                    sub_segment = SubtitleSegment(
                        start=seg['start'],
                        end=seg['end'],
                        text=seg['text'].strip()
                    )
                    subtitle_segments.append(sub_segment)
                    full_text_parts.append(seg['text'].strip())
                
                full_text = result.get('text', '').strip()
            
            logger.info(f"转录完成: {len(subtitle_segments)} 个片段")
            return subtitle_segments, full_text
            
        except Exception as e:
            logger.error(f"转录失败: {e}")
            raise TranscriptionError(f"音频转录失败: {e}")
    
    def save_srt(self, segments: List[SubtitleSegment], output_path: str):
        """
        保存为SRT格式文件
        
        Args:
            segments: 字幕片段列表
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                f.write(segment.to_srt(i))
                f.write('\n')
        logger.info(f"SRT字幕已保存: {output_path}")
    
    def save_vtt(self, segments: List[SubtitleSegment], output_path: str):
        """
        保存为VTT格式文件
        
        Args:
            segments: 字幕片段列表
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in segments:
                f.write(segment.to_vtt())
                f.write('\n')
        logger.info(f"VTT字幕已保存: {output_path}")
    
    def save_text(self, text: str, output_path: str):
        """
        保存纯文本文件
        
        Args:
            text: 文本内容
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"文本已保存: {output_path}")
    
    def generate_raw_markdown(self, segments: List[SubtitleSegment], 
                              video_info: Dict, 
                              include_timestamps: bool = True) -> str:
        """
        生成原始字幕的Markdown格式
        
        Args:
            segments: 字幕片段列表
            video_info: 视频信息字典
            include_timestamps: 是否包含时间戳
            
        Returns:
            Markdown格式字符串
        """
        lines = []
        
        # 添加元数据
        lines.append("---")
        lines.append(f"title: {video_info.get('title', 'Unknown')}")
        lines.append(f"author: {video_info.get('uploader', 'Unknown')}")
        lines.append(f"source: {video_info.get('original_url', '')}")
        lines.append(f"date: {video_info.get('upload_date', '')}")
        lines.append("type: raw-subtitle")
        lines.append("status: uncorrected")
        lines.append("---")
        lines.append("")
        
        # 添加标题
        lines.append(f"# {video_info.get('title', '视频字幕')}")
        lines.append("")
        lines.append(f"**作者**: {video_info.get('uploader', 'Unknown')}")
        lines.append(f"**来源**: [{video_info.get('original_url', '')}]({video_info.get('original_url', '')})")
        lines.append("")
        
        # 添加原始字幕
        lines.append("## 原始字幕")
        lines.append("")
        
        for segment in segments:
            lines.append(segment.to_markdown(include_timestamps))
            lines.append("")
        
        return '\n'.join(lines)
    
    def save_all_formats(self, segments: List[SubtitleSegment], 
                         full_text: str,
                         base_name: str,
                         video_info: Dict = None) -> Dict[str, str]:
        """
        保存所有格式的字幕文件
        
        Args:
            segments: 字幕片段列表
            full_text: 完整文本
            base_name: 基础文件名
            video_info: 视频信息
            
        Returns:
            格式 -> 文件路径的字典
        """
        output_files = {}
        
        # 保存SRT
        srt_path = self.output_dir / f"{base_name}.srt"
        self.save_srt(segments, str(srt_path))
        output_files['srt'] = str(srt_path)
        
        # 保存VTT
        vtt_path = self.output_dir / f"{base_name}.vtt"
        self.save_vtt(segments, str(vtt_path))
        output_files['vtt'] = str(vtt_path)
        
        # 保存纯文本
        txt_path = self.output_dir / f"{base_name}.txt"
        self.save_text(full_text, str(txt_path))
        output_files['txt'] = str(txt_path)
        
        # 保存原始Markdown
        if video_info:
            md_path = self.output_dir / f"{base_name}_raw.md"
            raw_md = self.generate_raw_markdown(segments, video_info)
            self.save_text(raw_md, str(md_path))
            output_files['raw_md'] = str(md_path)
        
        return output_files


# 便捷函数
def transcribe_audio(audio_path: str, config: Dict) -> Tuple[List[SubtitleSegment], str]:
    """
    便捷函数：转录音频
    
    Args:
        audio_path: 音频文件路径
        config: 配置字典
        
    Returns:
        (字幕片段列表, 完整文本)
    """
    transcriber = AudioTranscriber(config)
    return transcriber.transcribe(audio_path)
