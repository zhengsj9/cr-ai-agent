
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from read_products import load_products


# ==================================
# 第一部分：加载环境配置
# ==================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

if not api_key or not base_url or not model_name:
    raise ValueError("请检查.env中的API配置")


# ==================================
# 第二部分：创建DeepSeek客户端
# ==================================

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60.0,
    max_retries=2
)


# ==================================
# 第三部分：定义Listing生成函数
# ==================================

def generate_listing(product):

    prompt = f"""
你是一名专业的Amazon美国站Listing文案专家。

请根据以下商品信息生成英文Listing。

商品编号：{product['product_id']}
商品名称：{product['name']}
目标市场：{product['market']}
商品卖点：{json.dumps(product['features'], ensure_ascii=False)}

请完成以下任务：

1. 生成一个专业的英文商品标题。
2. 生成5条英文Bullet Points。
3. 生成5个英文搜索关键词。

要求：

1. 只能使用提供的真实商品信息。
2. 不得编造商品功能、认证、材质和性能。
3. 不得添加没有提供的参数。
4. 使用自然、专业的美国英语。
5. 不要输出中文。
6. 只返回JSON，不要添加Markdown代码块。

JSON格式：

{{
    "title": "英文标题",
    "bullet_points": [
        "描述1",
        "描述2",
        "描述3",
        "描述4",
        "描述5"
    ],
    "keywords": [
        "关键词1",
        "关键词2",
        "关键词3",
        "关键词4",
        "关键词5"
    ]
}}
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "你是专业的Amazon Listing生成助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content

    result = json.loads(content)

    # 检查AI返回的数据结构
    if not isinstance(result.get("title"), str) or not result["title"].strip():
        raise ValueError("AI返回的标题无效")

    if not isinstance(result.get("bullet_points"), list) or len(result["bullet_points"]) != 5:
        raise ValueError("AI必须返回5条Bullet Points")

    if not isinstance(result.get("keywords"), list) or len(result["keywords"]) != 5:
        raise ValueError("AI必须返回5个关键词")

    if not all(isinstance(x, str) and x.strip() for x in result["bullet_points"]):
        raise ValueError("Bullet Points包含无效内容")

    if not all(isinstance(x, str) and x.strip() for x in result["keywords"]):
        raise ValueError("关键词包含无效内容")

    return {
        "product_id": product["product_id"],
        "product_name": product["name"],
        "title": result["title"],
        "bullet_points": result["bullet_points"],
        "keywords": result["keywords"]
    }


# ==================================
# 第四部分：批量处理商品
# ==================================

def batch_generate():

    products = load_products()

    results = []

    success_count = 0
    failed_count = 0

    print("==============================")
    print("Amazon AI 批量Listing生成系统")
    print("==============================")

    print(f"发现商品数量：{len(products)}")

    for index, product in enumerate(products, start=1):

        print(
            f"\n正在处理第 {index}/{len(products)} 个商品："
            f"{product['name']}"
        )

        try:

            result = generate_listing(product)

            results.append(result)

            success_count += 1

            print("生成成功！")

        except Exception as error:

            failed_count += 1

            print("生成失败：", error)

    # 创建输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # 保存JSON
    output_file = output_dir / "listings.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n========== 处理统计 ==========")

    print("商品总数：", len(products))
    print("成功数量：", success_count)
    print("失败数量：", failed_count)

    print("\n结果已保存：", output_file)


# ==================================
# 第五部分：程序入口
# ==================================

if __name__ == "__main__":
    batch_generate()
