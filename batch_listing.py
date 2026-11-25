
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
# Shopify商品数据标准化
# ==================================

def normalize_shopify_product(shopify_product):

    # 获取商品变体
    variant_edges = (
        shopify_product.get("variants") or {}
    ).get("edges", [])

    variants = []

    for edge in variant_edges:

        variant = edge.get("node", {})

        variants.append({
            "price": variant.get("price"),
            "inventory_quantity": variant.get(
                "inventoryQuantity"
            )
        })

    # 获取SEO信息
    seo = shopify_product.get("seo") or {}

    # 转换为AI Agent统一商品结构
    product = {

        # Shopify商品唯一ID
        "product_id": shopify_product.get("id"),

        # 商品名称
        "name": shopify_product.get("title", ""),

        # 目标市场
        "market": os.getenv("SHOPIFY_MARKET", ""),

        # 目前没有经过验证的具体商品属性
       
        "features": extract_shopify_features(shopify_product),
        # 商品属性默认未经人工审核
        "features_approved": False,


        # 保留Shopify原始资料
        "source_description": (
            shopify_product.get("description") or ""
        ),

        "description_html": (
            shopify_product.get("descriptionHtml") or ""
        ),

        "vendor": shopify_product.get("vendor"),

        "product_type": shopify_product.get(
            "productType"
        ),

        "tags": shopify_product.get("tags", []),

        "seo": {
            "title": seo.get("title"),
            "description": seo.get("description")
        },

        "variants": variants
    }

    return product

# ==================================
# Shopify Metafields商品属性提取
# ==================================

def extract_shopify_features(shopify_product):

    features = []

    # 获取Metafields
    metafields = (
        shopify_product.get("metafields") or {}
    ).get("edges", [])

    for edge in metafields:

        metafield = edge.get("node") or {}

        namespace = metafield.get("namespace")
        key = metafield.get("key")
        raw_value = metafield.get("value")

        # 当前测试阶段只提取test_data命名空间
        # 排除global中的SEO信息
        if namespace != "test_data":
            continue

        if not key or raw_value is None:
            continue

        # 尝试解析JSON格式的Metafield
        try:
            parsed_value = json.loads(raw_value)

        except (TypeError, json.JSONDecodeError):
            parsed_value = raw_value

        # 处理带有value和unit的结构
        if isinstance(parsed_value, dict):

            value = parsed_value.get("value")
            unit = parsed_value.get("unit")

            if value is None:
                continue

            if unit:
                feature = f"{key}: {value} {unit}"
            else:
                feature = f"{key}: {value}"

        else:

            feature = f"{key}: {parsed_value}"

        features.append(feature)

    return features



# ==================================
# AI卖点来源完整性校验
# ==================================

def validate_selling_points(selling_points, product):

    # 1. 检查卖点是否为列表
    if not isinstance(selling_points, list):
        raise ValueError("selling_points必须是列表")

    # 2. 检查卖点数量
    if len(selling_points) > 5:
        raise ValueError("商品卖点不能超过5条")

    # 3. 获取商品原始属性
    source_features = product.get("features", [])

    if not isinstance(source_features, list):
        raise ValueError("商品features必须是列表")

    bullet_points = []

    # 4. 逐条检查卖点
    for index, point in enumerate(selling_points, start=1):

        if not isinstance(point, dict):
            raise ValueError(
                f"第{index}条卖点必须是字典"
            )

        text = point.get("text")

        point_sources = point.get("source_features")

        # 检查卖点文本
        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"第{index}条卖点文本无效"
            )

        # 检查来源列表
        if not isinstance(point_sources, list) or not point_sources:
            raise ValueError(
                f"第{index}条卖点缺少来源"
            )

        # 检查来源内容
        if not all(
            isinstance(source, str) and source.strip()
            for source in point_sources
        ):
            raise ValueError(
                f"第{index}条卖点来源无效"
            )

        # 检查来源是否存在于原始商品属性
        for source in point_sources:

            if source not in source_features:

                raise ValueError(
                    f"第{index}条卖点引用了不存在的商品属性："
                    f"{source}"
                )

        # 保存验证通过的卖点
        bullet_points.append(text)

    return bullet_points

# ==================================
# Shopify商品AI生成前的数据检查
# ==================================


# ==================================
# Shopify商品AI生成前的数据检查
# ==================================

def assess_shopify_product_readiness(product):

    features = product.get("features", [])

    description = product.get(
        "source_description", ""
    )

    tags = product.get("tags", [])

    seo = product.get("seo") or {}

    # 检查商品属性结构
    if not isinstance(features, list):
        raise ValueError("商品features必须是列表")

    # 提取有效的候选属性
    candidate_features = [
        feature
        for feature in features
        if isinstance(feature, str) and feature.strip()
    ]

    # 检查人工审核状态
    features_approved = (
        product.get("features_approved") is True
    )

    warnings = []

    if not description.strip():
        warnings.append("商品缺少原始描述")

    if not candidate_features:
        warnings.append("商品缺少结构化属性")

    elif not features_approved:
        warnings.append(
            "商品属性尚未经过人工审核，"
            "暂时不能用于AI内容生成"
        )

    seo_complete = bool(
        seo.get("title") and seo.get("description")
    )

    # 必须同时满足有属性和人工审核通过
    ready_for_ai_generation = (
        len(candidate_features) > 0
        and features_approved
    )

    return {

        "product_id": product.get("product_id"),

        "product_name": product.get("name"),

        "description_available": bool(description.strip()),

        "candidate_feature_count": len(candidate_features),

        "features_approved": features_approved,

        "tag_count": len(tags),

        "seo_complete": seo_complete,

        "ready_for_ai_generation": ready_for_ai_generation,

        "warnings": warnings
    }

# ==================================
# 第四部分：定义Shopify商品生成函数
# ==================================

def generate_listing(product, target_language="English"):

    product_id = product.get("product_id")
    product_name = product.get("name")
    market = product.get("market")
    source_features = product.get("features", [])

    if not product_id or not product_name:
        raise ValueError("商品缺少product_id或name")
    
    # ==================================
    # AI生成前的数据完整性检查
    # ==================================

    readiness = assess_shopify_product_readiness(product)

    if not readiness["ready_for_ai_generation"]:

        warning_text = "；".join(readiness["warnings"])

        raise ValueError(
            f"商品 {product_name} 暂不允许生成AI内容："
            f"{warning_text}"
        )


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
目标生成语言：{target_language}

语言要求：
1. 商品标题必须使用目标语言。
2. 商品描述必须使用目标语言。
3. 商品卖点必须使用目标语言。
4. SEO标题和SEO描述必须使用目标语言。
5. 商品标签必须使用目标语言。
6. warnings警告信息必须使用目标语言。
7. JSON字段名称保持英文，不得翻译。
8. 不得因为翻译而编造或改变商品属性。
9.6. warnings中的所有面向用户的内容也必须使用目标语言，不允许混入其他语言。
商品原始属性：{json.dumps(source_features, ensure_ascii=False)}

请完成以下任务：

1. 生成商品标题title。

要求：
- 使用自然、清晰的商品名称。
- 不得添加不存在的品牌、型号或功能。

2. 生成商品描述description。

要求：
- - 使用自然、专业的目标语言（{target_language}）。
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

进一步约束：

- 商品卖点必须是原始商品属性的客观复述。
- 不得使用未经数据支持的比较性词语，例如较长、较短、较轻、较重。
- 不得从商品尺寸或重量推导便携性、操控性、舒适性或性能优势。
- 不得推测商品适用人群、使用场景和实际使用效果。
- 长度属性只能客观描述商品长度。
- 重量属性只能客观描述商品重量。
- 不允许为了让文案更有吸引力而添加未经验证的形容词。
- 如果没有足够的真实属性支持某条卖点，应当省略该卖点。

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




# ==================================
# 使用独立函数校验AI卖点
# ==================================

    selling_points = result.get("selling_points")

    bullet_points = validate_selling_points(
        selling_points,
        product
    )



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


   
    # 8. 卖点不足5条时，根据目标语言自动添加提醒

    if len(selling_points) < 5:

        selling_point_count = len(selling_points)

        warning_messages = {

            "English": (
                f"Only {selling_point_count} verified selling points "
                "are available. Additional selling points "
                "must not be invented."
            ),

            "Japanese": (
                f"確認済みの商品訴求ポイントは"
                f"{selling_point_count}件です。"
                "追加の訴求ポイントを創作してはいけません。"
            ),

            "Chinese": (
                f"目前只有{selling_point_count}条经过验证的商品卖点。"
                "不得编造额外卖点。"
            )
        }

        warning_message = warning_messages.get(
            target_language,
            warning_messages["English"]
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

        "warnings": warnings,
        "target_language": target_language
    }


# ==================================
# 多语言Listing批量生成
# ==================================


# ==================================
# 多语言Listing批量生成
# 增加异常处理
# ==================================

def generate_multilingual_listings(product, languages):

    if not isinstance(languages, list) or not languages:
        raise ValueError("languages必须是非空列表")

    results = []

    failed_languages = []

    for language in languages:

        if not isinstance(language, str) or not language.strip():
            raise ValueError("目标语言必须是有效字符串")

        print(f"\n正在生成 {language} 版本...")

        try:

            result = generate_listing(
                product,
                target_language=language
            )

            results.append(result)

            print(f"{language} 版本生成成功！")

        except Exception as error:

            failed_languages.append(language)

            print(f"{language} 版本生成失败：{error}")

            continue

    # 输出失败统计
    if failed_languages:

        print("\n========== 语言生成失败统计 ==========")

        for language in failed_languages:
            print("-", language)

    print("\n========== 多语言生成统计 ==========")

    print("成功数量:", len(results))
    print("失败数量:", len(failed_languages))

    return results


# ==================================
# 保存多语言Listing
# ==================================

def save_multilingual_listings(results):

    if not isinstance(results, list) or not results:
        raise ValueError("results必须是非空列表")

    # 语言与文件名映射
    language_files = {
        "English": "english",
        "Japanese": "japanese",
        "Chinese": "chinese"
    }

    # 创建多语言输出目录
    output_dir = Path("output") / "multilingual"

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    saved_files = []

    # 分别保存不同语言
    for result in results:

        language = result.get("target_language")

        if language not in language_files:
            raise ValueError(f"不支持的语言：{language}")

        product_id = result.get("product_id")

        if not product_id:
            raise ValueError("商品ID不能为空")

        output_file = output_dir / (
            f"listings_{language_files[language]}.json"
        )

        # 读取已有数据
        existing_results = []

        if output_file.exists():

            with open(
                output_file,
                "r",
                encoding="utf-8"
            ) as file:

                existing_results = json.load(file)

            if not isinstance(existing_results, list):
                raise ValueError("已有JSON数据格式错误")

        # 根据商品ID更新或追加
        for index, old_result in enumerate(existing_results):

            if (
                isinstance(old_result, dict)
                and old_result.get("product_id") == product_id
            ):
                existing_results[index] = result
                break

        else:
            existing_results.append(result)

        # 保存JSON
        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                existing_results,
                file,
                ensure_ascii=False,
                indent=4
            )

        saved_files.append(str(output_file))

        print("保存成功：", output_file)

    return saved_files

# ==================================
# 第八部分：批量处理商品
# ==================================



# ==================================
# 多语言Listing完整处理流程
# ==================================

def generate_and_save_multilingual_listings(
    product,
    languages
):

    # 第一步：生成多语言Listing
    results = generate_multilingual_listings(
        product,
        languages
    )

    # 第二步：保存多语言Listing
    saved_files = save_multilingual_listings(
        results
    )

    # 第三步：返回处理结果
    return {
        "product_id": product["product_id"],
        "generated_count": len(results),
        "saved_files": saved_files,
        "results": results
    }

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
