#!/bin/bash
# ============================================================
#  xhs-to-llm-wiki 一键初始化脚本
#  每次新会话开始时运行一次，安装所有依赖
#  用法: bash init.sh
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  xhs-to-llm-wiki 环境初始化${NC}"
echo -e "${GREEN}========================================${NC}"

# ---------- 1. 系统依赖检查 ----------
echo ""
echo -e "${YELLOW}[1/4] 检查系统依赖...${NC}"

if ! command -v ffmpeg &> /dev/null; then
    echo "  ⚠ ffmpeg 未安装，尝试安装..."
    apt-get update -qq && apt-get install -y -qq ffmpeg 2>/dev/null || echo "  ⚠ ffmpeg 安装失败，请手动安装"
else
    echo "  ✅ ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
fi

if ! command -v git &> /dev/null; then
    echo "  ⚠ git 未安装，尝试安装..."
    apt-get install -y -qq git 2>/dev/null || echo "  ⚠ git 安装失败"
else
    echo "  ✅ git: $(git --version)"
fi

# ---------- 2. Python 依赖安装 ----------
echo ""
echo -e "${YELLOW}[2/4] 安装 Python 依赖...${NC}"

pip install -r requirements.txt --break-system-packages -q 2>&1 | tail -3

echo "  ✅ Python 依赖安装完成"

# ---------- 3. Whisper 模型预下载（可选）----------
echo ""
echo -e "${YELLOW}[3/4] Whisper 模型（首次运行 main.py 时会自动下载）${NC}"
echo "  当前配置: base 模型 (~139MB)"
echo "  可选: tiny (~39MB) / small (~244MB) / medium (~769MB)"
echo "  修改 config/config.yaml 中 transcription.model 可切换"

# ---------- 4. 环境变量检查 ----------
echo ""
echo -e "${YELLOW}[4/4] 环境变量检查...${NC}"

if [ -f config/.env ]; then
    echo "  ✅ config/.env 存在"
    if grep -q "GITHUB_TOKEN" config/.env 2>/dev/null; then
        echo "  ✅ GITHUB_TOKEN 已配置"
    else
        echo "  ⚠ GITHUB_TOKEN 未配置（SKILL_GUIDED 模式需要）"
    fi
else
    echo "  ⚠ config/.env 不存在"
    echo "  请复制 config/.env.example 为 config/.env 并填入 GITHUB_TOKEN"
fi

# ---------- 5. 创建必要目录 ----------
echo ""
echo -e "${YELLOW}[5/5] 创建工作目录...${NC}"
mkdir -p storage/temp storage/output

# ---------- 完成 ----------
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 初始化完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "使用方式:"
echo "  1. 给我一个小红书链接，我会自动执行全流程"
echo "  2. 或手动运行: python main.py <链接>"
echo ""
echo "当前配置:"
echo "  - 字幕校正: INTERNAL（SOLO内置LLM）"
echo "  - Ingest模式: SKILL_GUIDED（LLM按SKILL.md执行）"
echo "  - Whisper模型: base"
echo "  - GitHub仓库: ryankklam/llm-wiki-storage@test"
