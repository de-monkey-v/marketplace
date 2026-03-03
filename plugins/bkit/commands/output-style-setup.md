---
name: output-style-setup
description: |
  Install bkit output styles to your project or user directory.
  Copies output style files from bkit plugin to the appropriate location.

  Triggers: output style setup, install output style, setup style,
  아웃풋 스타일 설치, 스타일 설정, 出力スタイル設定,
  输出样式安装, instalar estilo, installer style,
  Stil installieren, installare stile
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
---

# Output Style Setup

bkit의 Output Style을 설치합니다.

## Available Styles

| Style | Recommended For | Description |
|-------|----------------|-------------|
| bkit-learning | Starter | 학습 모드 - PDCA를 배우며 개발 |
| bkit-pdca-guide | Dynamic | PDCA 워크플로우 가이드 + 자동 체크리스트 |
| bkit-enterprise | Enterprise | CTO 관점 아키텍처/보안/성능 분석 |
| bkit-pdca-enterprise | Enterprise | PDCA + CTO 통합 (가장 상세) |

## Instructions

Ask the user where to install using AskUserQuestion:

**Option 1: Project level** (current project only)
- Copy from `${CLAUDE_PLUGIN_ROOT}/output-styles/*.md` to `.claude/output-styles/`
- Best for: project-specific style preference

**Option 2: User level** (all projects)
- Copy from `${CLAUDE_PLUGIN_ROOT}/output-styles/*.md` to `~/.claude/output-styles/`
- Best for: consistent style across all projects

## Setup Steps

1. Ask user: project level or user level installation
2. Create target directory if not exists
3. Copy all 4 output style files to target
4. Confirm installation with file list
5. Suggest running `/output-style` to activate

## Post-Setup

After copying, inform user:
- Use `/output-style` to select from the installed styles
- Recommended style based on project level detection
- Styles can be changed anytime during session
