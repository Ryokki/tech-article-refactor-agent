# Tech Article Refactorer ✍️🔄

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Gemini](https://img.shields.io/badge/AI-Gemini_Pro-orange.svg)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](#english) | [中文说明](#中文说明)

**Tech Article Refactorer** is an AI-powered agentic workflow that **refactors** your technical drafts into masterpiece articles.

Unlike standard AI writing tools that simply fix grammar or generate generic content, this tool treats writing like software engineering. It employs a **Multi-Agent System** grounded in **Cognitive Science** and **Educational Psychology** (Constructivism, Cognitive Load Theory) to deconstruct, architect, and rebuild your content for maximum reader impact.

---

<a name="english"></a>
## 🇬🇧 English

### Why Refactor Your Writing?
Code needs refactoring to be maintainable; technical writing needs refactoring to be understandable. This tool turns raw ideas (brain dumps, rough notes, internal wikis) into **Deep, Insightful, and Structured** technical blogs suitable for senior engineers.

### 🤖 The 3-Stage Agentic Pipeline

1.  **🕵️ The Analyst (Critic):**
    *   Diagnoses your draft based on "Cognitive Load Theory".
    *   Identifies "Curse of Knowledge" blind spots.
    *   Critiques structure and missing context without mercy.
2.  **🏗️ The Architect (Planner):**
    *   Designs a "Refactoring Blueprint" based on the Analyst's report.
    *   Applies scaffolding strategies and "First Principles" thinking.
    *   Structures the logic chain for deep processing.
3.  **✍️ The Writer (Executor):**
    *   Re-implements the article following the Blueprint strictly.
    *   Uses the "Feynman Technique" to explain complex concepts.
    *   Produces the final Markdown output.

### 🚀 Quick Start

#### Prerequisites
*   Python 3.10+
*   A Google Gemini API Key

#### Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Usage

Run the agent on your markdown draft:

```bash
uv run technical_writer_agent.py "path/to/your/draft.md" "path/to/output_article.md"
```

The tool will display the real-time thought process of each agent in the console.

---

<a name="中文说明"></a>
## 🇨🇳 中文说明

### 像重构代码一样重构你的文章
**Tech Article Refactorer** 不仅仅是一个 AI 润色工具。它是一个基于**认知科学**原理构建的智能体工作流，旨在将平庸的草稿重构为大师级的技术文章。

普通的 AI 工具只是在修补文字，而本工具通过模拟人类专家的思维链（Chain of Thought），通过**分析、设计、重写**三个阶段，确保文章符合**第一性原理**，适合深度学习者（如资深工程师）阅读。

### 🧠 核心原理与流程

本工具内置了三个专业的 AI Agent 协作：

1.  **🕵️ 分析师 (The Analyst)**
    *   **职责**：基于“认知负荷理论”对原文进行“恶毒”诊断。
    *   **能力**：识别“知识诅咒”（作者觉得简单但读者看不懂的地方），指出逻辑断层。
2.  **🏗️ 架构师 (The Architect)**
    *   **职责**：基于诊断报告，设计文章的重构蓝图。
    *   **能力**：运用“建构主义”教学法，设计脚手架（Scaffolding），规划章节逻辑链。
3.  **✍️ 作家 (The Writer)**
    *   **职责**：严格执行蓝图。
    *   **能力**：运用“费曼技巧”进行深度阐述，生成最终的高质量 Markdown 文章。

### 🛠️ 快速开始

#### 环境要求
*   Python 3.10+
*   Google Gemini API Key

#### 配置

在项目根目录创建 `.env` 文件：

```env
GEMINI_API_KEY=xxx
```

#### 使用方法

```bash
python technical_writer_agent.py "你的草稿路径.md" "输出文件路径.md"
```

运行后，你将在终端看到绚丽的 CLI 界面，实时展示三个 Agent 的思考和交互过程。

## 📄 License

MIT License
