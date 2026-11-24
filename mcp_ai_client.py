
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import Client, StdioServerParameters


# ==========================================
# 1. 加载环境变量
# ==========================================

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError(
        "没有找到 DEEPSEEK_API_KEY，请检查 .env 文件！"
    )


# ==========================================
# 2. 初始化 DeepSeek 客户端
# ==========================================

ai_client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

MODEL = "deepseek-flash"


# ==========================================
# 3. 配置 MCP Server
# ==========================================

server_file = Path(__file__).with_name(
    "mcp_server.py"
)

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(server_file)]
)


# ==========================================
# 4. 将 MCP Schema 转换为 AI 工具格式
# ==========================================

def convert_mcp_tools(mcp_tools):

    ai_tools = []

    for tool in mcp_tools:

        ai_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema
            }
        }

        ai_tools.append(ai_tool)

    return ai_tools


# ==========================================
# 5. 将 MCP 工具返回结果转换成字符串
# ==========================================


def format_tool_result(result):

    # 1. 优先读取结构化数据
    structured_data = getattr(
        result,
        "structuredContent",
        None
    )

    if structured_data is None:
        structured_data = getattr(
            result,
            "structured_content",
            None
        )

    if structured_data is not None:

        return json.dumps(
            structured_data,
            ensure_ascii=False,
            indent=4,
            default=str
        )

    # 2. 如果没有结构化数据，读取普通文本
    contents = []

    for content in result.content:

        if hasattr(content, "text"):

            contents.append(content.text)

    if contents:
        return "\n".join(contents)

    # 3. 如果两种格式都没有，返回完整结果用于排查
    if hasattr(result, "model_dump"):

        return json.dumps(
            result.model_dump(
                mode="json",
                exclude_none=True
            ),
            ensure_ascii=False,
            indent=4,
            default=str
        )

    return str(result)



# ==========================================
# 6. AI Agent 核心逻辑
# ==========================================

async def run_agent(client, user_question):

    print("\n用户：", user_question)

    # 获取 MCP Server 提供的工具
    tools_result = await client.list_tools()

    # 转换成 DeepSeek 可以理解的工具格式
    ai_tools = convert_mcp_tools(
        tools_result.tools
    )

    print("\n发现 MCP 工具：")

    for tool in ai_tools:

        print(
            "工具名称：",
            tool["function"]["name"]
        )

    # 建立对话历史
    messages = [

        {
            "role": "system",
            "content": (
                "你是一个跨境电商商品助手。"
                "当用户需要搜索商品时，使用 search_product。"
                "当用户需要查询商品详情时，使用 get_product。"
                "必须根据工具返回的真实数据回答，"
                "不要编造商品信息。"
            )
        },

        {
            "role": "user",
            "content": user_question
        }

    ]

    # 防止模型无限循环调用工具
    max_tool_rounds = 5

    for round_number in range(max_tool_rounds):

        print(
            f"\n========== AI 思考轮次 "
            f"{round_number + 1} =========="
        )

        # 请求 DeepSeek
        response = await ai_client.chat.completions.create(

            model=MODEL,

            messages=messages,

            tools=ai_tools,

            tool_choice="auto",

            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            }

        )

        ai_message = response.choices[0].message

        # 将 AI 回复加入对话历史
        messages.append(
            ai_message.model_dump(exclude_none=True)
        )

        # 判断 AI 是否要求调用工具
        if not ai_message.tool_calls:

            print("\n========== AI 最终回答 ==========")

            print(ai_message.content or "AI 没有返回文字内容。")

            return

        # 遍历 AI 要求调用的工具
        for tool_call in ai_message.tool_calls:

            tool_name = tool_call.function.name

            tool_arguments = json.loads(
                tool_call.function.arguments
            )

            print("\nAI 选择工具：", tool_name)

            print("AI 生成参数：", tool_arguments)

            # 检查工具是否由 MCP Server 提供
            available_tools = {
                tool.name
                for tool in tools_result.tools
            }
            # 定义允许调用的工具白名单
            allowed_tools = {
                "search_product",
                 "get_product"
                            }
            if tool_name not in available_tools or tool_name not in allowed_tools:

                tool_output = json.dumps({
                    "error": "工具不存在或不允许调用"
                }, ensure_ascii=False)

            else:

                try:

                    # 让 MCP Client 执行工具
                    tool_result = await client.call_tool(
                        tool_name,
                        tool_arguments
                    )

                    # 检查工具执行结果
                    if tool_result.is_error:

                        tool_output = (
                            "工具执行失败："
                            + format_tool_result(tool_result)
                        )

                    else:

                        tool_output = format_tool_result(
                            tool_result
                        )

                except Exception as error:

                    tool_output = (
                        f"工具调用发生错误：{error}"
                    )

            print("\n工具执行结果：")

            print(tool_output)

            # 将工具结果返回给 DeepSeek
            messages.append({

                "role": "tool",

                "tool_call_id": tool_call.id,

                "content": tool_output

            })

    print("\nAI 工具调用轮数已达到上限。")


# ==========================================
# 7. 主程序
# ==========================================

async def main():

    print("正在启动 DeepSeek + MCP AI Agent...")

    async with Client(server_params) as client:

        print("MCP Server 连接成功！")

        print("DeepSeek AI Agent 已准备就绪！")

        print("\n输入 exit 可以退出程序。")

        while True:

            user_question = input(
                "\n请输入你的商品问题："
            ).strip()

            if user_question.lower() in [
                "exit",
                "quit"
            ]:

                print("AI Agent 已退出。")

                break

            if not user_question:

                continue

            try:

                await run_agent(
                    client,
                    user_question
                )

            except Exception as error:

                print("\n执行失败：", error)


# ==========================================
# 8. 程序入口
# ==========================================

if __name__ == "__main__":

    asyncio.run(main())
