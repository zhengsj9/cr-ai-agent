
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

2. 生成一段英文商品长描述（Product Description）。

长描述要求：
- 使用自然、专业的美国英语。
- 将商品真实卖点组织成连贯的介绍。
- 只能描述商品资料明确提供的属性。
- 不得根据常识推测商品功能。
- 不得添加未经证实的商品参数。
- 不得编造续航、防水、降噪、认证等信息。
- 商品资料不足时，不得自行推测。

3. 生成最多5条英文Bullet Points。

Bullet Points要求：
- 每条描述围绕一个真实商品特征。
- 使用自然、专业的美国英语。
- 只能使用商品资料中明确提供的信息。
- 不得为了凑够5条而编造或重复卖点。
- 如果只有4条真实卖点，就只返回4条。
- 不得将资料不足的提示作为商品卖点。

4. 生成5个英文搜索关键词。

关键词要求：
- 必须与商品名称和真实属性相关。
- 不得包含未经证实的商品功能。
- 不得虚构品牌或商品参数。

5. 生成warnings警告信息。

warnings要求：
- 如果商品资料不足以支持5条独立卖点，
  请说明资料不足。
- 如果商品资料存在其他明显缺失，
  请指出需要人工确认的内容。
- 如果没有需要提醒的问题，返回空列表。

其他要求：

1. 只能使用提供的真实商品信息。
2. 不得编造商品功能、认证、材质和性能。
3. 不得添加没有提供的参数。
4. 使用自然、专业的美国英语。
5. 不要输出中文。
6. 只返回JSON，不要添加Markdown代码块。

JSON格式：

{{
    "title": "英文标题",
    "description": "英文商品长描述",
    "bullet_points": [
        "真实卖点1",
        "真实卖点2",
        "真实卖点3",
        "真实卖点4"
    ],
    "keywords": [
        "关键词1",
        "关键词2",
        "关键词3",
        "关键词4",
        "关键词5"
    ],
    "warnings": [
        "资料不足提醒"
    ]
}}
"""

    # 调用DeepSeek API
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

    # 获取AI返回内容
    content = response.choices[0].message.content

    # 将JSON字符串转换成Python字典
    result = json.loads(content)

    # 检查返回的数据结构
    if not isinstance(result, dict):
        raise ValueError("AI返回的数据必须是JSON对象")

    # ==================================
    # 第四部分：数据校验
    # ==================================

    # 1. 检查标题
    if not isinstance(result.get("title"), str) or not result["title"].strip():
        raise ValueError("AI返回的标题无效")

    # 2. 检查商品长描述
    if not isinstance(result.get("description"), str) or not result["description"].strip():
        raise ValueError("AI返回的商品长描述无效")

    # 3. 检查五点描述
    bullet_points = result.get("bullet_points")

    if not isinstance(bullet_points, list):
        raise ValueError("Bullet Points必须是列表")

    if len(bullet_points) > 5:
        raise ValueError("Bullet Points不能超过5条")

    if not all(
        isinstance(x, str) and x.strip()
        for x in bullet_points
    ):
        raise ValueError("Bullet Points包含无效内容")

    # 4. 检查关键词
    keywords = result.get("keywords")

    if not isinstance(keywords, list) or len(keywords) != 5:
        raise ValueError("AI必须返回5个关键词")

    if not all(
        isinstance(x, str) and x.strip()
        for x in keywords
    ):
        raise ValueError("关键词包含无效内容")

    # 5. 检查warnings
    warnings = result.get("warnings", [])

    if not isinstance(warnings, list):
        raise ValueError("warnings必须是列表")

    if not all(
        isinstance(x, str) and x.strip()
        for x in warnings
    ):
        raise ValueError("warnings包含无效内容")

    # 如果真实卖点不足5条，自动增加提醒
    if len(bullet_points) < 5:

        warning_message = (
            f"当前只有{len(bullet_points)}条有资料支持的商品卖点，"
            "不足5条，不应编造额外卖点。"
        )

        if warning_message not in warnings:
            warnings.append(warning_message)

    # ==================================
    # 第五部分：返回完整Listing
    # ==================================

    return {
        "product_id": product["product_id"],
        "product_name": product["name"],
        "title": result["title"],
        "description": result["description"],
        "bullet_points": bullet_points,
        "keywords": keywords,
        "warnings": warnings
    }


# ==================================
# 第六部分：批量处理商品
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

            if result["warnings"]:
                print("注意：该商品存在以下提醒：")

                for warning in result["warnings"]:
                    print("-", warning)

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
# 第七部分：程序入口
# ==================================

if __name__ == "__main__":
    batch_generate()
