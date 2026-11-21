
import os
import csv
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# ==================================
# 第一部分：读取环境配置
# ==================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

if not api_key or not base_url or not model_name:
    raise ValueError("请检查 .env 中的 API 配置")


# ==================================
# 第二部分：创建大模型客户端
# ==================================

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60.0,
    max_retries=2
)


# ==================================
# 第三部分：定义 AI 生成函数
# ==================================

def generate_listing(product):

    system_prompt = """
你是一名专业的跨境电商运营文案专家。

请根据商品资料，生成适用于 Amazon 美国站的英文Listing，
并提供对应的中文翻译。

要求：
1. 生成一个英文商品标题。
2. 生成恰好5条英文卖点。
3. 生成5个英文SEO关键词。
4. 生成对应的中文标题。
5. 生成对应的5条中文卖点。
6. 生成对应的中文关键词。
7. 不得编造商品资料中没有提供的功能。
8. 仅输出合法JSON，不要输出Markdown。

JSON格式：
{
    "title_en": "英文标题",
    "title_zh": "中文标题",
    "bullet_points_en": [
        "英文卖点1",
        "英文卖点2",
        "英文卖点3",
        "英文卖点4",
        "英文卖点5"
    ],
    "bullet_points_zh": [
        "中文卖点1",
        "中文卖点2",
        "中文卖点3",
        "中文卖点4",
        "中文卖点5"
    ],
    "keywords_en": [
        "英文关键词1",
        "英文关键词2",
        "英文关键词3",
        "英文关键词4",
        "英文关键词5"
    ],
    "keywords_zh": [
        "中文关键词1",
        "中文关键词2",
        "中文关键词3",
        "中文关键词4",
        "中文关键词5"
    ]
}
"""

    user_prompt = (
        "请处理以下商品：\n"
        + json.dumps(product, ensure_ascii=False)
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
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI没有返回内容")

    content = content.strip()

    # 兼容模型返回Markdown代码围栏
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[-1].strip() == "```":
            content = "\n".join(lines[1:-1])

    result = json.loads(content)

    # 验证返回数据
    required_fields = [
        "title_en",
        "title_zh",
        "bullet_points_en",
        "bullet_points_zh",
        "keywords_en",
        "keywords_zh"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"AI返回结果缺少字段：{field}")

    for field in [
        "bullet_points_en",
        "bullet_points_zh",
        "keywords_en",
        "keywords_zh"
    ]:
        if not isinstance(result[field], list):
            raise ValueError(f"{field} 必须是列表")

        if len(result[field]) != 5:
            raise ValueError(f"{field} 必须包含5条内容")

    return result


# ==================================
# 第四部分：读取商品CSV
# ==================================

def read_products():

    input_file = Path("products.csv")

    if not input_file.exists():
        raise FileNotFoundError("没有找到 products.csv")

    products = []

    with input_file.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
            "product_id",
            "name",
            "market",
            "features"
        }

        if not required_columns.issubset(
            set(reader.fieldnames or [])
        ):
            raise ValueError("products.csv 缺少必要字段")

        for row in reader:

            if not row["product_id"].strip():
                continue

            product = {
                "product_id": row["product_id"].strip(),
                "name": row["name"].strip(),
                "market": row["market"].strip(),
                "features": [
                    item.strip()
                    for item in row["features"].split(";")
                    if item.strip()
                ]
            }

            products.append(product)

    return products


# ==================================
# 第五部分：批量处理商品
# ==================================

def process_products(products):

    results = []

    total = len(products)

    for index, product in enumerate(products, start=1):

        print(
            f"\n正在处理第 {index}/{total} 个商品："
            f"{product['name']}"
        )

        try:

            listing = generate_listing(product)

            result = {
                "product_id": product["product_id"],
                "product_name": product["name"],
                "market": product["market"],
                "status": "SUCCESS",
                "title_en": listing["title_en"],
                "title_zh": listing["title_zh"],
                "bullet_points_en": "\n".join(
                    listing["bullet_points_en"]
                ),
                "bullet_points_zh": "\n".join(
                    listing["bullet_points_zh"]
                ),
                "keywords_en": ", ".join(
                    listing["keywords_en"]
                ),
                "keywords_zh": ", ".join(
                    listing["keywords_zh"]
                ),
                "error": ""
            }

            print("生成成功！")

        except Exception as error:

            print(f"生成失败：{error}")

            result = {
                "product_id": product["product_id"],
                "product_name": product["name"],
                "market": product["market"],
                "status": "FAILED",
                "title_en": "",
                "title_zh": "",
                "bullet_points_en": "",
                "bullet_points_zh": "",
                "keywords_en": "",
                "keywords_zh": "",
                "error": str(error)
            }

        results.append(result)

    return results


# ==================================
# 第六部分：导出CSV
# ==================================

def save_results(results):

    output_dir = Path("output")

    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "listings.csv"

    if not results:
        print("没有可导出的商品结果")
        return

    fieldnames = list(results[0].keys())

    with output_file.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(results)

    print(f"\n结果已经保存：{output_file}")


# ==================================
# 第七部分：程序入口
# ==================================

def main():

    print("================================")
    print("Amazon AI 批量Listing生成系统")
    print("================================")

    try:

        products = read_products()

        print(f"成功读取 {len(products)} 个商品")

        if not products:
            print("商品列表为空，程序结束")
            return

        results = process_products(products)

        save_results(results)

        success_count = sum(
            1 for item in results
            if item["status"] == "SUCCESS"
        )

        failed_count = len(results) - success_count

        print("\n========== 处理统计 ==========")
        print(f"总商品数量：{len(products)}")
        print(f"成功数量：{success_count}")
        print(f"失败数量：{failed_count}")

    except Exception as error:

        print(f"程序执行失败：{error}")


if __name__ == "__main__":
    main()
