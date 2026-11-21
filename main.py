
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 第1步：加载环境变量
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

if not api_key or not base_url or not model_name:
    raise ValueError("请检查 .env 中的 API 配置")


# 第2步：创建大模型客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60.0,
    max_retries=2
)


# 第3步：准备跨境电商商品数据
product = {
    "name": "Wireless Bluetooth Earbuds",
    "market": "United States",
    "features": [
        "Bluetooth wireless connection",
        "USB-C charging",
        "Touch controls",
        "Built-in microphone"
    ]
}


# 第4步：编写系统提示词
system_prompt = """
你是一名专业的跨境电商商品文案助手。

请根据商品资料生成美国市场的英文商品Listing。

要求：
1. 生成一个英文商品标题。
2. 生成恰好5条英文卖点。
3. 生成5个英文搜索关键词。
4. 不得编造商品功能、认证或性能参数。
5. 仅输出合法JSON，不要输出Markdown。

JSON结构：
{
  "title": "商品标题",
  "bullet_points": [
    "卖点1",
    "卖点2",
    "卖点3",
    "卖点4",
    "卖点5"
  ],
  "keywords": [
    "关键词1",
    "关键词2",
    "关键词3",
    "关键词4",
    "关键词5"
  ]
}
"""


# 第5步：定义AI生成函数
def generate_listing(product_data):
    user_prompt = (
        "请根据以下商品资料生成英文Listing：\n"
        + json.dumps(product_data, ensure_ascii=False)
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("模型没有返回内容")

    # 去掉模型可能附加的Markdown代码围栏
    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        if lines[-1].strip() == "```":
            content = "\n".join(lines[1:-1])

    result = json.loads(content)

    # 检查输出格式
    if not isinstance(result, dict):
        raise ValueError("AI返回结果不是JSON对象")

    if not isinstance(result.get("title"), str):
        raise ValueError("商品标题格式错误")

    if not isinstance(result.get("bullet_points"), list):
        raise ValueError("五点描述格式错误")

    if len(result["bullet_points"]) != 5:
        raise ValueError("五点描述数量错误")

    if not isinstance(result.get("keywords"), list):
        raise ValueError("关键词格式错误")

    if len(result["keywords"]) != 5:
        raise ValueError("关键词数量错误")

    return result


# 第6步：程序入口
def main():
    print("=== Amazon AI Listing Generator ===")
    print("正在调用DeepSeek，请稍候...")

    try:
        listing = generate_listing(product)

        print("\nAI生成结果：")
        print(json.dumps(
            listing,
            ensure_ascii=False,
            indent=2
        ))

        # 保存结果到JSON文件
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "listing.json"

        output_file.write_text(
            json.dumps(
                listing,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print("\n结果已保存到：", output_file)

    except Exception as error:
        print("程序执行失败：", error)


if __name__ == "__main__":
    main()
