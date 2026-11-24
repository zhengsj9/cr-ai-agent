
import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from profit_tools import (
    calculate_profit,
    convert_currency,
    analyze_margin
)
from listing_tools import generate_product_listing

# ==================================
# 第一部分：加载环境配置
# ==================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

if not api_key or not base_url or not model_name:
    raise ValueError("请检查.env配置")


# ==================================
# 第二部分：创建AI客户端
# ==================================

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60.0,
    max_retries=2
)


# ==================================
# 第三部分：定义AI可以使用的工具
# ==================================

tools = [

    # ==================================
    # 工具一：商品利润计算
    # ==================================

    {
        "type": "function",
        "function": {
            "name": "calculate_profit",
            "description": "计算跨境电商商品利润、总成本和利润率",
            "parameters": {
                "type": "object",
                "properties": {
                    "sale_price_usd": {
                        "type": "number",
                        "description": "商品美元售价"
                    },
                    "exchange_rate": {
                        "type": "number",
                        "description": "美元兑人民币汇率"
                    },
                    "purchase_cost_rmb": {
                        "type": "number",
                        "description": "人民币采购成本"
                    },
                    "shipping_cost_rmb": {
                        "type": "number",
                        "description": "人民币物流成本"
                    },
                    "commission_rate": {
                        "type": "number",
                        "description": "平台佣金比例，例如15%填写0.15"
                    },
                    "ad_cost_usd": {
                        "type": "number",
                        "description": "美元广告费用"
                    }
                },
                
                "required": [
                    "sale_price_usd",
                    "exchange_rate",
                    "purchase_cost_rmb",
                    "shipping_cost_rmb",
                    "commission_rate",
                    "ad_cost_usd"
                ],
                "additionalProperties": False
            }
            
        }
        
    },

    # ==================================
    # 工具二：货币换算
    # ==================================

    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "将美元和人民币相互换算",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "需要换算的金额"
                    },
                    "exchange_rate": {
                        "type": "number",
                        "description": "美元兑人民币汇率"
                    },
                    "from_currency": {
                        "type": "string",
                        "enum": ["USD", "RMB"],
                        "description": "原始货币"
                    },
                    "to_currency": {
                        "type": "string",
                        "enum": ["USD", "RMB"],
                        "description": "目标货币"
                    }
                },
                "required": [
                    "amount",
                    "exchange_rate",
                    "from_currency",
                    "to_currency"
                ],
                "additionalProperties": False
            }
        }
    },

    # ==================================
    # 工具三：利润率分析
    # ==================================

    {
        "type": "function",
        "function": {
            "name": "analyze_margin",
            "description": "分析商品实际利润率，并判断是否达到目标",
            "parameters": {
                "type": "object",
                "properties": {
                    "profit_rmb": {
                        "type": "number",
                        "description": "商品利润，人民币"
                    },
                    "revenue_rmb": {
                        "type": "number",
                        "description": "商品销售收入，人民币"
                    },
                    "target_margin_percent": {
                        "type": "number",
                        "description": "目标利润率，例如20代表20%"
                    }
                },
                "required": [
                    "profit_rmb",
                    "revenue_rmb"
                ],
                "additionalProperties": False
            }
        }
    }

    ,
    {
        "type": "function",
        "function": {
            "name": "generate_product_listing",
            "description": (
                "根据商品编号生成美国Amazon商品Listing。"
                "当用户要求生成、优化Amazon商品标题、"
                "五点描述或关键词时调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "商品编号，例如P001、P002、P003"
                    }
                },
                "required": ["product_id"],
                "additionalProperties": False
            }
        }
    }


]



# ==================================
# 第四部分：工具执行映射
# ==================================

available_functions = {
    "calculate_profit": calculate_profit,
    "convert_currency": convert_currency,
    "analyze_margin": analyze_margin,
    "generate_product_listing": generate_product_listing
}

# ==================================
# 第五部分：Agent运行函数
# ==================================


def run_agent(messages):

    # 最多允许5轮模型请求
    for step in range(5):

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            }
        )

        assistant_message = response.choices[0].message

        # 如果AI不再要求调用工具，说明本轮回答完成
        if not assistant_message.tool_calls:

            answer = assistant_message.content or ""

            # 把AI最终回答也保存到对话历史中
            messages.append({
                "role": "assistant",
                "content": answer
            })

            return answer

        # 保存AI的工具调用请求
        messages.append(assistant_message)

        # 执行AI要求调用的工具
        for tool_call in assistant_message.tool_calls:

            function_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(f"\nAI决定调用工具：{function_name}")
            print("工具参数：", arguments)

            # 检查工具是否在白名单中
            if function_name not in available_functions:
                raise ValueError("不允许调用该工具")

            # 找到对应的Python函数
            function_to_call = available_functions[
                function_name
            ]

            # 执行Python函数
            function_result = function_to_call(
                **arguments
            )

            print("Python计算结果：", function_result)

            # 将工具执行结果加入对话历史
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    function_result,
                    ensure_ascii=False
                )
            })

    raise RuntimeError("Agent工具调用次数超过限制")

# ==================================
# 第六部分：程序入口
# ==================================


def main():

    print("==============================")
    print("跨境电商 AI 智能助手")
    print("==============================")

    print("输入 exit 可以退出程序")
    print("输入 reset 可以清空当前对话")

    # 创建对话历史
    messages = [
        {
            "role": "system",
            "content": """
你是一个专业的跨境电商AI经营分析助手。

你拥有四个Python工具：

1. calculate_profit：计算商品利润。
2. convert_currency：进行货币换算。
3. analyze_margin：分析利润率。
4. generate_product_listing：生成Amazon商品Listing。

工作规则：

1. 理解用户需求。
2. 缺少必要参数时，主动询问用户。
3. 不允许猜测缺失的业务数据。
4. 用户补充参数后，结合之前的对话继续分析。
5. 需要计算时调用对应Python工具。
6. 后续工具使用前面工具返回的真实结果。
7. 最终使用中文生成经营分析报告。
8. 明确说明没有纳入计算的成本。
8. 当用户要求生成Amazon Listing时，调用
   generate_product_listing工具。

9. 当用户只提供商品编号时，使用该编号生成Listing。

10. 如果用户询问利润，则调用利润分析工具。

11. 如果用户同时要求生成Listing和计算利润，

9. 不得编造行业平均利润率或市场数据。
10. 如果没有行业数据，不得声称商品利润率高于行业平均水平。
11. 所有利润计算必须以Python工具返回结果为准。
12. 用户明确表示不考虑某些成本时，
    按用户指定的计算范围进行分析。
13. 不得将理论利润等同于实际净利润。
14. 如果建议增加广告预算或降低售价，
    必须说明这是经营建议，不能直接保证利润增长。
15. 缺少必要参数时必须主动询问，
    不得擅自假设。

"""
        }
    ]

    # 持续接收用户输入
    while True:

        question = input("\n请输入你的问题：")

        # 去除首尾空格
        question = question.strip()

        # 判断是否为空
        if not question:
            print("问题不能为空，请重新输入。")
            continue

        # 输入exit退出
        if question.lower() == "exit":
            print("感谢使用，再见！")
            break

        # 输入reset清空对话
        if question.lower() == "reset":

            messages = [
                messages[0]
            ]

            print("当前对话已经清空。")
            continue

        # 保存用户本次输入
        messages.append({
            "role": "user",
            "content": question
        })

        print("\nAI正在思考，请稍候...\n")

        try:

            # 把完整对话历史交给Agent
            answer = run_agent(messages)

            print("\n========== AI回答 ==========")
            print(answer)

        except Exception as error:

            print("\n程序执行失败：", error)


if __name__ == "__main__":
    main()

