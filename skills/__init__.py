"""
Skills模块 - 可复用的功能组件
"""

from .subtitle_corrector.correct_subtitle import SubtitleCorrector, correct_subtitle_text
from .wiki_ingestor.ingest_to_wiki import WikiIngestor, ingest_to_wiki

__all__ = [
    'SubtitleCorrector',
    'correct_subtitle_text',
    'WikiIngestor',
    'ingest_to_wiki',
]
