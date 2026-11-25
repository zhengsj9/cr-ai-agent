
import os
import json
import html
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
# 第三部分：Shopify描述HTML生成
# ==================================

def build_shopify_description_html(description, bullet_points):

    paragraphs = [
        item.strip()
        for item in description.split("\n\n")
        if item.strip()
    ]

    html_parts = [
        f"<p>{html.escape(paragraph, quote=False)}</p>"
        for paragraph in paragraphs
    ]

    if bullet_points:

        list_items = "".join(
            f"<li>{html.escape(point, quote=False)}</li>"
            for point in bullet_points
        )

        html_parts.append(f"<ul>{list_items}</ul>")

    return "\n".join(html_parts)


# ==================================
# 第四部分：定义Shopify商品生成函数
# ==================================

def generate_listing(product):

    product_id = product.get("product_id")
    product_name = product.get("name")
    market = product.get("market")
    source_features = product.get("features", [])

    if not product_id or not product_name:
        raise ValueError("商品缺少product_id或name")

    if not isinstance(source_features, list):
        raise ValueError("商品features必须是列表")

    if not source_features:
        raise ValueError(
            f"商品{product_id}没有可用的原始属性"
        )

    prompt = f"""
你是一名专业的Shopify独立站商品内容与SEO文案专家。

请根据以下真实商品资料生成Shopify商品内容。

商品编号：{product_id}
商品名称：{product_name}
目标市场：{market}
商品原始属性：{json.dumps(source_features, ensure_ascii=False)}

请完成以下任务：

1. 生成商品标题title。

要求：
- 使用自然、清晰的商品名称。
- 不得添加不存在的品牌、型号或功能。

2. 生成商品描述description。

要求：
- 使用自然、专业的英语。
- 只能描述商品资料明确提供的属性。
- 不得推测商品功能。
- 不得编造续航、防水、降噪、认证等信息。
- 返回纯文本，不要输出HTML。

3. 提取最多5条结构化商品卖点selling_points。

每条卖点必须包含：
- text：商品卖点文案。
- source_features：对应的原始商品属性。

要求：
- source_features必须与输入的原始商品属性完全一致。
- 每条卖点至少对应一条真实商品属性。
- 不得编造或夸大商品属性。
- 不得重复卖点。
- 不得为了凑够5条而编造卖点。
- 如果只有4条真实卖点，就只返回4条。

4. 生成Shopify SEO信息seo。

必须包含：
- title：SEO标题。
- description：SEO描述。

要求：
- 与商品真实名称和属性相关。
- 不得堆砌关键词。
- 不得加入未经证实的功能。

5. 生成5个Shopify商品标签tags。

要求：
- 与商品名称或真实属性相关。
- 标签简洁、具有相关性。
- 不得包含未经证实的功能。
- 不得重复。

注意：
Shopify商品标签用于商品分类和管理，
不能将其虚构成真实搜索量或关键词排名数据。

6. 生成warnings警告信息。

要求：
- 指出缺失的商品规格、材质、尺寸等信息。
- 指出商品名称与属性之间的冲突。
- 不要重复说明卖点不足5条。
- 没有其他提醒时返回空列表。

其他要求：
- 只能使用提供的真实商品信息。
- 不得编造商品功能、认证、材质和性能。
- 只返回JSON对象。
- 不要添加Markdown代码块。

JSON格式：

{{
    "title": "Shopify商品标题",
    "description": "商品纯文本描述",
    "selling_points": [
        {{
            "text": "商品卖点文案",
            "source_features": [
                "原始商品属性"
            ]
        }}
    ],
    "seo": {{
        "title": "SEO标题",
        "description": "SEO描述"
    }},
    "tags": [
        "tag-one",
        "tag-two",
        "tag-three",
        "tag-four",
        "tag-five"
    ],
    "warnings": []
}}
"""

    # 1. 调用DeepSeek API
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是专业的Shopify商品内容与SEO助手。"
                    "必须严格依据输入的商品资料生成内容。"
                )
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

    # 2. 获取AI返回内容
    content = response.choices[0].message.content

    if not content:
        raise ValueError("DeepSeek没有返回内容")

    # 3. JSON字符串转换成Python字典
    result = json.loads(content)

    if not isinstance(result, dict):
        raise ValueError("AI返回的数据必须是JSON对象")


    # ==================================
    # 第五部分：数据校验
    # ==================================

    # 1. 检查商品标题

    title = result.get("title")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("AI返回的商品标题无效")


    # 2. 检查商品描述

    description = result.get("description")

    if not isinstance(description, str) or not description.strip():
        raise ValueError("AI返回的商品描述无效")


    # 3. 检查结构化商品卖点

    selling_points = result.get("selling_points")

    if not isinstance(selling_points, list):
        raise ValueError("selling_points必须是列表")

    if len(selling_points) > 5:
        raise ValueError("商品卖点不能超过5条")

    for index, point in enumerate(selling_points, start=1):

        if not isinstance(point, dict):
            raise ValueError(f"第{index}条卖点必须是字典")

        point_text = point.get("text")
        point_sources = point.get("source_features")

        if not isinstance(point_text, str) or not point_text.strip():
            raise ValueError(f"第{index}条卖点文本无效")

        if not isinstance(point_sources, list) or not point_sources:
            raise ValueError(f"第{index}条卖点缺少原始属性来源")

        if not all(
            isinstance(source, str) and source.strip()
            for source in point_sources
        ):
            raise ValueError(f"第{index}条卖点来源内容无效")

        # 检查来源是否真实存在
        if not all(
            source in source_features
            for source in point_sources
        ):
            raise ValueError(
                f"第{index}条卖点引用了不存在的商品属性"
            )

    # 4. 提取卖点文本

    bullet_points = [
        point["text"]
        for point in selling_points
    ]


    # 5. 检查SEO信息

    seo = result.get("seo")

    if not isinstance(seo, dict):
        raise ValueError("seo必须是JSON对象")

    seo_title = seo.get("title")
    seo_description = seo.get("description")

    if not isinstance(seo_title, str) or not seo_title.strip():
        raise ValueError("SEO标题无效")

    if not isinstance(seo_description, str) or not seo_description.strip():
        raise ValueError("SEO描述无效")


    # 6. 检查Shopify商品标签

    tags = result.get("tags")

    if not isinstance(tags, list) or len(tags) != 5:
        raise ValueError("AI必须返回5个Shopify商品标签")

    if not all(
        isinstance(tag, str) and tag.strip()
        for tag in tags
    ):
        raise ValueError("Shopify商品标签包含无效内容")

    normalized_tags = [
        tag.strip().casefold()
        for tag in tags
    ]

    if len(set(normalized_tags)) != len(normalized_tags):
        raise ValueError("Shopify商品标签不能重复")


    # 7. 检查warnings

    warnings = result.get("warnings", [])

    if not isinstance(warnings, list):
        raise ValueError("warnings必须是列表")

    if not all(
        isinstance(item, str) and item.strip()
        for item in warnings
    ):
        raise ValueError("warnings包含无效内容")


    # 8. 卖点不足5条时自动添加提醒

    if len(selling_points) < 5:

        warning_message = (
            f"Only {len(selling_points)} verified selling points "
            "are available. Additional selling points "
            "must not be invented."
        )

        if warning_message not in warnings:
            warnings.append(warning_message)


    # ==================================
    # 第六部分：生成Shopify商品描述HTML
    # ==================================

    description_html = build_shopify_description_html(
        description,
        bullet_points
    )


    # ==================================
    # 第七部分：返回完整Shopify商品数据
    # ==================================

    return {

        # 项目内部商品编号
        "product_id": product_id,

        "product_name": product_name,

        # Shopify商品数据
        "shopify_product": {

            "title": title,

            "descriptionHtml": description_html,

            "seo": {
                "title": seo_title,
                "description": seo_description
            },

            "tags": tags
        },

        # Agent内部审核数据
        "description": description,

        "selling_points": selling_points,

        "bullet_points": bullet_points,

        "warnings": warnings
    }


# ==================================
# 第八部分：批量处理商品
# ==================================

def batch_generate():

    products = load_products()

    results = []

    success_count = 0
    failed_count = 0

    print("==============================")
    print("Shopify AI 批量商品内容生成系统")
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


    # 保存JSON文件

    output_file = output_dir / "shopify_products.json"

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


    # 输出统计

    print("\n========== 处理统计 ==========")

    print("商品总数：", len(products))

    print("成功数量：", success_count)

    print("失败数量：", failed_count)

    print("\n结果已保存：", output_file)


# ==================================
# 第九部分：程序入口
# ==================================

if __name__ == "__main__":

    batch_generate()
