# xhs-to-llm-wiki

小红书视频 → 字幕转录 → LLM校正 → GitHub仓库 → LLM Wiki Ingest

## 快速开始（每次新会话）

```bash
cd /workspace/xhs-to-llm-wiki
bash init.sh
```

然后直接给我小红书链接即可，我会自动执行全流程。

## 工作流程

```
小红书链接 → yt-dlp下载 → ffmpeg提取音频 → Whisper转录 → LLM校正 → clone仓库 → 保存文件 → SKILL.md ingest → commit & push
```

## 配置

所有配置在 `config/config.yaml`，关键配置项：

| 配置 | 当前值 | 说明 |
|------|--------|------|
| `correction.mode` | `INTERNAL` | INTERNAL=SOLO内置LLM / EXTERNAL=OpenAI API |
| `ingestion.mode` | `SKILL_GUIDED` | SKILL_GUIDED=LLM深度理解 / PROGRAMMATIC=Python自动处理 |
| `transcription.model` | `base` | whisper模型，可选 tiny/base/small/medium |
| `github.branch` | `test` | GitHub推送分支 |

## 目录结构

```
xhs-to-llm-wiki/
├── init.sh                    # 一键初始化脚本（每次新会话运行）
├── main.py                    # 主程序
├── requirements.txt           # Python依赖
├── config/
│   ├── config.yaml           # 主配置
│   └── .env                  # 环境变量（GITHUB_TOKEN）
├── modules/
│   ├── downloader.py         # yt-dlp视频下载
│   ├── audio_extractor.py    # ffmpeg音频提取
│   ├── transcriber.py        # Whisper字幕转录
│   ├── github_repo_manager.py # Git仓库管理
│   └── ...
├── skills/
│   ├── subtitle_corrector/   # 字幕校正
│   ├── skill_guided_ingestor.py  # SKILL_GUIDED模式
│   └── llm_wiki_adapter.py   # PROGRAMMATIC模式
└── storage/
    ├── temp/                 # 临时文件（视频、音频）
    └── output/               # 输出文件（字幕）
```

## 注意事项

- **每次新会话需要运行 `bash init.sh`**（容器会重置，依赖需重装）
- Whisper 模型首次运行会自动下载（base ~139MB）
- `correction.mode: INTERNAL` 时不需要 OpenAI API Key
- `config/.env` 中的 GITHUB_TOKEN 用于推送到 GitHub
