# llm-wiki-workflow

视频/图文 → 转录提取 → LLM校正 → GitHub Wiki Ingest

支持**小红书**和**抖音**的**视频**和**图文笔记**链接，自动完成从下载到知识入库的全流程。

## 快速开始（每次新会话）

```bash
cd /workspace/xhs-to-llm-wiki
bash init.sh
```

然后直接给我链接即可，我会自动判断类型并执行对应流程。

## 工作流程

### 视频笔记

```
视频链接 → 去重检查 → 下载视频 → 提取音频 → Whisper转录 → LLM校正 → clone仓库 → 保存文件 → SKILL.md ingest → commit & push
```

### 图文笔记（新增 🆕）

```
图文链接 → 去重检查 → 抓取笔记信息 → 下载图片 → 生成Markdown → clone仓库 → 保存图片+MD → SKILL.md ingest → commit & push
```

系统会自动判断笔记类型：
- **视频笔记**（`type: video`）→ 走视频流程
- **图文笔记**（`type: normal`）→ 走图文流程

### 去重检查

每次处理链接前会自动检查该笔记是否已处理过：

- 检查 `raw/{platform}/subtitle/` 或 `raw/{platform}/content/` 是否存在相关文件
- 检查 `raw/{platform}/video/` 或 `raw/{platform}/images/` 是否存在媒体文件
- 检查 `wiki/sources/` 是否存在相关页面

**如果检测到重复**：会提示用户并显示已存在的文件列表，避免重复处理。

## 支持平台

| 平台 | 链接格式 | 视频下载 | 图文抓取 |
|------|----------|----------|----------|
| 小红书 | `http://xhslink.com/o/xxx` | yt-dlp | requests + __INITIAL_STATE__ |
| 抖音 | `https://v.douyin.com/xxx` | requests（无需cookies） | 待支持 |

抖音视频自动保存到 `raw/douyin/`，小红书保存到 `raw/rednote/`。

## 配置

所有配置在 `config/config.yaml`，关键配置项：

| 配置 | 当前值 | 说明 |
|------|--------|------|
| `correction.mode` | `INTERNAL` | INTERNAL=SOLO内置LLM / EXTERNAL=OpenAI API |
| `ingestion.mode` | `SKILL_GUIDED` | SKILL_GUIDED=LLM深度理解 / PROGRAMMATIC=Python自动处理 |
| `transcription.model` | `base` | whisper模型，可选 tiny/base/small/medium |
| `github.branch` | `test` | GitHub推送分支 |
| `ingestion.skill_guided.remote_repo.branch` | `test` | Wiki仓库推送分支 |

## 目录结构

```
xhs-to-llm-wiki/
├── init.sh                         # 一键初始化脚本（每次新会话运行）
├── main.py                         # 主程序
├── requirements.txt                # Python依赖
├── config/
│   ├── config.yaml                # 主配置
│   ├── .env.example                # 环境变量模板
│   └── .env                       # 环境变量（GITHUB_TOKEN，不提交到Git）
├── modules/
│   ├── downloader.py              # 视频下载 + 笔记类型检测
│   ├── rednote_scraper.py         # 🆕 小红书图文笔记抓取
│   ├── audio_extractor.py         # ffmpeg音频提取
│   ├── transcriber.py             # Whisper字幕转录
│   ├── github_repo_manager.py     # Git仓库管理
│   └── utils.py                   # 工具函数
├── skills/
│   ├── subtitle_corrector/        # 字幕校正（INTERNAL/EXTERNAL双模式）
│   ├── skill_guided_ingestor.py   # SKILL_GUIDED模式（视频+图文）
│   └── llm_wiki_adapter.py        # PROGRAMMATIC模式
└── storage/
    ├── temp/                      # 临时文件（视频、音频、图片）
    └── output/                    # 输出文件（原始/校正后字幕、MD文档）
```

## 核心模块说明

### downloader.py — 多平台下载 + 类型检测

- **小红书视频**：通过 yt-dlp 下载
- **抖音视频**：通过 requests 直接获取（绕过 yt-dlp 的 cookies 限制）
- **笔记类型检测**：`detect_note_type(url)` → `video` / `normal` / `error`
- 自动检测平台：`detect_platform(url)` → `xiaohongshu` / `douyin` / `unknown`

### rednote_scraper.py — 🆕 小红书图文笔记抓取

- **fetch_note_info(url)**：获取笔记信息（标题、正文、标签、作者、图片列表）
- **download_images()**：批量下载高清图片
- **generate_markdown()**：生成结构化 Markdown 文档
- **scrape(url)**：一键完成全流程（获取 → 下载 → 生成MD）
- 通过解析 `window.__INITIAL_STATE__` JSON 获取完整数据

### skill_guided_ingestor.py — SKILL_GUIDED Ingest

- **prepare()**：clone仓库 + 保存视频/字幕到 `raw/{platform}/`（视频流程）
- **prepare_image_note()** 🆕：clone仓库 + 保存图片/MD到 `raw/{platform}/`（图文流程）
- **commit_and_push()**：提交前自动校验 index/overview/log 是否已更新
- **_validate_ingest_completeness()**：通过时间戳对比检测遗漏的索引文件更新

### 字幕校正双模式

| 模式 | 说明 | 依赖 |
|------|------|------|
| `INTERNAL` | SOLO内置LLM直接校正 | 无需额外配置 |
| `EXTERNAL` | 调用OpenAI API校正 | 需要 `OPENAI_API_KEY` |

## Wiki 仓库结构（llm-wiki-storage）

```
llm-wiki-storage/
├── raw/
│   ├── rednote/                   # 小红书原始文件
│   │   ├── video/                 # 视频文件
│   │   ├── subtitle/              # 校正后字幕
│   │   ├── images/                # 🆕 图文笔记图片
│   │   └── content/               # 🆕 图文笔记MD文档
│   └── douyin/                    # 抖音原始文件
│       ├── video/
│       └── subtitle/
├── wiki/
│   ├── index.md                   # 内容目录
│   ├── overview.md                # 整体概览
│   ├── log.md                     # 操作日志
│   ├── sources/                   # 来源摘要页
│   ├── concepts/                  # 概念页
│   ├── entities/                  # 实体页
│   ├── topics/                    # 主题页
│   └── solutions/                 # 经验文档
└── .agent/skills/llm-wiki/SKILL.md  # Ingest规范
```

## Ingest 完整性保障

每次 `commit_and_push()` 前会自动检查三个索引文件是否已更新：

- `wiki/index.md` — 内容目录
- `wiki/overview.md` — 整体概览
- `wiki/log.md` — 操作日志

检测到遗漏时会打印 `⚠️` 警告，防止索引文件过时。

## 注意事项

- **每次新会话需要运行 `bash init.sh`**（容器会重置，依赖需重装）
- Whisper 模型首次运行会自动下载（base ~139MB）
- `correction.mode: INTERNAL` 时不需要 OpenAI API Key
- `config/.env` 中的 GITHUB_TOKEN 用于推送到 GitHub
- 抖音视频通过移动端 UA 获取，不需要登录 cookies
- 🆕 小红书图文笔记通过解析 `__INITIAL_STATE__` 获取数据，如遇反爬可尝试更新 User-Agent
