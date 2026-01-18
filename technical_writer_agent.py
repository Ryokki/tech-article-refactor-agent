# agent/technical_writer_agent.py

import os
import sys
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# 将当前目录添加到路径中，以便我们可以导入 prompts 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompts import (
    ANALYST_SYSTEM_PROMPT, ANALYST_USER_PROMPT_TEMPLATE,
    ARCHITECT_SYSTEM_PROMPT, ARCHITECT_USER_PROMPT_TEMPLATE,
    WRITER_SYSTEM_PROMPT, WRITER_USER_PROMPT_TEMPLATE
)
from db import OptimizationLogRepository

# 加载环境变量 (.env 文件)
load_dotenv()

console = Console()

class TechnicalWriterAgent:
    """
    技术写作 Agent

    采用三阶段流程：
    1. 分析师 (Analyst): 诊断文章问题
    2. 架构师 (Architect): 设计重写蓝图
    3. 作家 (Writer): 执行重写
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # 获取 API Key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            console.print("[bold red]错误:[/bold red] 未找到 GEMINI_API_KEY 环境变量。")
            sys.exit(1)

        # 配置 Google GenAI
        genai.configure(api_key=self.api_key)
        self.model_name = model or os.getenv("GEMINI_MODEL") or "gemini-3-flash-preview"

    def _call_llm(self, system_prompt: str, user_prompt: str, step_name: str) -> str:
        """
        调用 LLM 的辅助函数，带有进度提示。

        Args:
            system_prompt: 系统提示词 (System Instruction)
            user_prompt: 用户提示词
            step_name: 当前步骤名称 (用于显示进度)

        Returns:
            str: LLM 的响应文本
        """
        with console.status(f"[bold green]正在运行 {step_name}..."):
            try:
                # 初始化模型，传入 system_instruction
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_prompt
                )

                # 配置生成参数 (降低安全过滤阈值以防止误杀技术内容)
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }

                # 发起生成请求
                response = model.generate_content(
                    user_prompt,
                    safety_settings=safety_settings,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=8192, # Gemini 支持长输出
                    )
                )

                return response.text
            except Exception as e:
                console.print(f"[bold red]LLM 调用失败:[/bold red] {e}")
                # 如果是特定的 API 错误，可以在这里做更细致的处理
                sys.exit(1)

    def process(self, article_path: str, output_path: str):
        """
        执行主工作流

        Args:
            article_path: 原始文章路径
            output_path: 最终输出文件路径 (包含所有步骤的详细结果)
        """

        # 0. 读取输入文件
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                article_content = f.read()
        except FileNotFoundError:
            console.print(f"[bold red]错误:[/bold red] 找不到文件: {article_path}")
            return

        console.print(Panel(f"开始优化文章: {article_path}\n使用模型: {self.model_name}", title="Technical Writer Agent"))

        # 初始化过程记录字符串
        process_log = ""

        # 第一步：分析 (Analyst)
        # 目标：找出认知负荷过高的地方，不留情面地批评
        console.print("[bold]步骤 1: 正在分析文章 (Analyst Agent)...[/bold]")
        analyst_user_prompt = ANALYST_USER_PROMPT_TEMPLATE.format(article_content=article_content)
        analysis = self._call_llm(
            ANALYST_SYSTEM_PROMPT,
            analyst_user_prompt,
            "分析师 Agent (Analyst)"
        )
        console.print(Panel(Markdown(analysis), title="步骤 1 输出: 诊断报告", border_style="yellow"))

        # 记录第一步输出
        process_log += f"# 步骤 1: 诊断报告 (Analyst)\n\n{analysis}\n\n---\n\n"

        # 第二步：设计蓝图 (Architect)
        # 目标：根据诊断报告，设计重写策略，而不是直接重写
        console.print("[bold]步骤 2: 正在设计蓝图 (Architect Agent)...[/bold]")
        architect_user_prompt = ARCHITECT_USER_PROMPT_TEMPLATE.format(
            article_content=article_content,
            analysis_content=analysis
        )
        blueprint = self._call_llm(
            ARCHITECT_SYSTEM_PROMPT,
            architect_user_prompt,
            "架构师 Agent (Architect)"
        )
        console.print(Panel(Markdown(blueprint), title="步骤 2 输出: 重构蓝图", border_style="blue"))

        # 记录第二步输出
        process_log += f"# 步骤 2: 重构蓝图 (Architect)\n\n{blueprint}\n\n---\n\n"

        # 第三步：重写 (Writer)
        # 目标：严格按照蓝图执行，产出最终 Markdown
        console.print("[bold]步骤 3: 正在重写文章 (Writer Agent)...[/bold]")
        writer_user_prompt = WRITER_USER_PROMPT_TEMPLATE.format(
            article_content=article_content,
            analysis_content=analysis,
            blueprint_content=blueprint
        )
        rewritten_article = self._call_llm(
            WRITER_SYSTEM_PROMPT,
            writer_user_prompt,
            "作家 Agent (Writer)"
        )

        process_log += f"# 步骤 3: 最终文章 (Article)\n\n{rewritten_article}\n\n"

        # 保存输出 (包含所有步骤)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(process_log)

        # 显示预览
        preview_len = 500
        preview_text = rewritten_article[:preview_len] + "\n\n...(内容已截断)..." if len(rewritten_article) > preview_len else rewritten_article
        console.print(Panel(Markdown(preview_text), title="步骤 3 输出: 最终结果预览", border_style="green"))
        console.print(f"[bold green]成功![/bold green] 包含完整步骤的输出已保存至: {output_path}")

        # 记录到数据库
        try:
            # 组合完整的 prompts
            full_analyst_prompt = f"System Prompt:\n{ANALYST_SYSTEM_PROMPT}\n\nUser Prompt:\n{analyst_user_prompt}"
            full_architect_prompt = f"System Prompt:\n{ARCHITECT_SYSTEM_PROMPT}\n\nUser Prompt:\n{architect_user_prompt}"
            full_writer_prompt = f"System Prompt:\n{WRITER_SYSTEM_PROMPT}\n\nUser Prompt:\n{writer_user_prompt}"

            record_id = OptimizationLogRepository.insert(
                original_content=article_content,
                analyst_prompt=full_analyst_prompt,
                analyst_result=analysis,
                architect_prompt=full_architect_prompt,
                architect_result=blueprint,
                writer_prompt=full_writer_prompt,
                writer_result=rewritten_article
            )
            console.print(f"[dim]数据库记录 ID: {record_id}[/dim]")
        except Exception as e:
            console.print(f"[yellow]警告: 数据库记录失败[/yellow]: {e}")

if __name__ == "__main__":
    # 简单的命令行参数处理
    if len(sys.argv) < 3:
        console.print("用法: python technical_writer_agent.py <markdown文章路径> <输出路径>")
        sys.exit(1)

    agent = TechnicalWriterAgent()
    agent.process(sys.argv[1], sys.argv[2])
