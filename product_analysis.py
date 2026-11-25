
# ==========================================
# Product Analysis Agent
# 商品分析Agent
# ==========================================


# ==========================================
# 第一步：统计商品已有属性数量
# ==========================================

def count_provided_attributes(product):
    """
    统计商品已经提供的属性数量。
    """

    if not isinstance(product, dict):
        raise TypeError("product必须是字典")

    features = product.get("features", [])

    if not isinstance(features, list):
        raise ValueError("商品features必须是列表")

    for index, feature in enumerate(features, start=1):

        if not isinstance(feature, str) or not feature.strip():
            raise ValueError(
                f"第{index}条商品属性无效"
            )

    return len(features)


# ==========================================
# 第二步：分析商品缺失属性
# ==========================================

def find_missing_attributes(product, required_attributes):
    """
    检查商品缺少哪些必需属性。
    """

    if not isinstance(product, dict):
        raise TypeError("product必须是字典")

    features = product.get("features", [])

    if not isinstance(features, list):
        raise ValueError("商品features必须是列表")

    if not isinstance(required_attributes, list):
        raise TypeError("required_attributes必须是列表")

    provided_attributes = set()

    for index, feature in enumerate(features, start=1):

        if not isinstance(feature, str) or not feature.strip():
            raise ValueError(f"第{index}条商品属性无效")

        attribute_name, separator, attribute_value = feature.partition(":")

        if (
            not separator
            or not attribute_name.strip()
            or not attribute_value.strip()
        ):
            raise ValueError(f"第{index}条商品属性格式无效")

        provided_attributes.add(
            attribute_name.strip().lower()
        )

    missing_attributes = []

    for attribute in required_attributes:

        if not isinstance(attribute, str) or not attribute.strip():
            raise ValueError("必需属性名称必须是有效字符串")

        if attribute.strip().lower() not in provided_attributes:
            missing_attributes.append(attribute.strip())

    return missing_attributes


# ==========================================
# 第三步：商品完整性等级判断
# ==========================================

def assess_product_completeness(product, required_attributes):
    """
    判断商品资料完整程度。
    """

    if not isinstance(product, dict):
        raise TypeError("product必须是字典")

    if not isinstance(required_attributes, list):
        raise TypeError("required_attributes必须是列表")

    if not required_attributes:
        raise ValueError("required_attributes不能为空")

    # 检查必需属性并去重
    normalized_attributes = []
    seen = set()

    for attribute in required_attributes:

        if not isinstance(attribute, str) or not attribute.strip():
            raise ValueError("必需属性名称无效")

        attribute = attribute.strip()
        key = attribute.lower()

        if key not in seen:
            normalized_attributes.append(attribute)
            seen.add(key)

    # 获取缺失属性
    missing_attributes = find_missing_attributes(
        product,
        normalized_attributes
    )

    # 统计属性数量
    required_count = len(normalized_attributes)

    provided_count = required_count - len(missing_attributes)

    missing_count = len(missing_attributes)

    # 计算完整率
    completeness_ratio = provided_count / required_count

    # 判断完整性等级
    if missing_count == 0:

        status = "complete"

    elif completeness_ratio >= 0.5:

        status = "partially_complete"

    else:

        status = "incomplete"

    return {
        "status": status,
        "required_attribute_count": required_count,
        "provided_required_attribute_count": provided_count,
        "missing_attribute_count": missing_count,
        "completeness_ratio": round(completeness_ratio, 2),
        "missing_attributes": missing_attributes
    }


# ==========================================
# 第四步：统一商品基础分析报告
# ==========================================


# ==========================================
# 统一商品基础分析报告
# ==========================================

def analyze_product_basics(product, required_attributes):
    """
    整合商品基础分析功能。

    包含：
        1. 商品属性数量统计
        2. 商品缺失属性检查
        3. 商品完整性等级判断
        4. 商品风险分析
        5. 商品优化建议生成

    返回：
        dict: 完整商品分析报告
    """

    # 1. 检查商品数据
    if not isinstance(product, dict):
        raise TypeError("product必须是字典")

    # 2. 统计商品属性数量
    provided_attribute_count = count_provided_attributes(
        product
    )

    # 3. 判断商品完整性
    completeness = assess_product_completeness(
        product,
        required_attributes
    )

    # 4. 提取真实商品属性
    supported_features = product.get("features", [])

    # 5. 商品风险分析
    risk_analysis = detect_product_risks(product)

    # 6. 生成商品优化建议
    recommendations = generate_product_recommendations(
        completeness,
        risk_analysis
    )

    # 7. 生成统一分析报告
    report = {
        "product_id": product.get("product_id"),
        "product_name": product.get("name"),
        "provided_attribute_count": provided_attribute_count,
        "completeness": completeness,
        "supported_features": supported_features,
        "risk_analysis": risk_analysis,
        "risk_count": len(risk_analysis),
        "recommendations": recommendations,
        "recommendation_count": len(recommendations)
    }

    # 8. 返回完整分析报告
    return report


# ==========================================
# 统一商品基础分析报告
# ==========================================

def analyze_product_basics(product, required_attributes):
    """
    整合商品基础分析功能。

    包含：
        1. 商品属性数量统计
        2. 商品缺失属性检查
        3. 商品完整性等级判断
        4. 商品风险分析
        5. 商品优化建议生成

    返回：
        dict: 完整商品分析报告
    """

    # 1. 检查商品数据
    if not isinstance(product, dict):
        raise TypeError("product必须是字典")

    # 2. 统计商品属性数量
    provided_attribute_count = count_provided_attributes(
        product
    )

    # 3. 判断商品完整性
    completeness = assess_product_completeness(
        product,
        required_attributes
    )

    # 4. 提取真实商品属性
    supported_features = product.get("features", [])

    # 5. 商品风险分析
    risk_analysis = detect_product_risks(product)

    # 6. 生成商品优化建议
    recommendations = generate_product_recommendations(
        completeness,
        risk_analysis
    )

    # 7. 生成统一分析报告
    report = {
        "product_id": product.get("product_id"),
        "product_name": product.get("name"),
        "provided_attribute_count": provided_attribute_count,
        "completeness": completeness,
        "supported_features": supported_features,
        "risk_analysis": risk_analysis,
        "risk_count": len(risk_analysis),
        "recommendations": recommendations,
        "recommendation_count": len(recommendations)
    }

    # 8. 返回完整分析报告
    return report

# ==========================================
# 第五步：商品信息风险识别
# ==========================================

def detect_product_risks(product):
    """
    根据商品名称和已有属性识别潜在信息风险。

    注意：
        这里只进行基础规则识别，
        不代表已经完成AI语义分析。
    """

    if not isinstance(product, dict):
        raise TypeError("product必须是字典")

    # 获取商品名称
    product_name = product.get("name", "")

    if not isinstance(product_name, str):
        raise ValueError("商品名称必须是字符串")

    # 获取商品属性
    features = product.get("features", [])

    if not isinstance(features, list):
        raise ValueError("商品features必须是列表")

    # 提取已经提供的属性名称
    provided_attributes = set()

    for index, feature in enumerate(features, start=1):

        if not isinstance(feature, str) or not feature.strip():
            raise ValueError(f"第{index}条商品属性无效")

        attribute_name, separator, attribute_value = (
            feature.partition(":")
        )

        if (
            not separator
            or not attribute_name.strip()
            or not attribute_value.strip()
        ):
            raise ValueError(f"第{index}条商品属性格式无效")

        provided_attributes.add(
            attribute_name.strip().lower()
        )

    # 定义配件相关属性
    accessory_attributes = {
        "binding",
        "bindings",
        "binding_compatibility",
        "accessories",
        "included_items",
        "package_contents"
    }

    # 判断是否提供配件信息
    has_accessory_info = bool(
        provided_attributes & accessory_attributes
    )

    risks = []

    # 检查商品名称中的潜在歧义
    if (
        "complete" in product_name.casefold()
        and not has_accessory_info
    ):

        risks.append({
            "risk_type": "ambiguous_product_name",
            "severity": "review_required",
            "message": (
                "商品名称包含Complete，"
                "但商品属性未说明是否包含固定器或其他配件，"
                "需要人工核实。"
            )
        })

    return risks


# ==========================================
# 第六步：商品优化建议生成
# ==========================================

def generate_product_recommendations(
    completeness,
    risk_analysis
):
    """
    根据商品缺失属性和风险分析生成优化建议。

    参数：
        completeness: 商品完整性分析结果
        risk_analysis: 商品风险分析结果

    返回：
        list: 商品优化建议
    """

    # 1. 检查输入数据
    if not isinstance(completeness, dict):
        raise TypeError("completeness必须是字典")

    if not isinstance(risk_analysis, list):
        raise TypeError("risk_analysis必须是列表")

    # 2. 获取缺失属性
    missing_attributes = completeness.get(
        "missing_attributes", []
    )

    if not isinstance(missing_attributes, list):
        raise ValueError("missing_attributes必须是列表")

    # 3. 定义属性与优化建议的映射
    recommendation_mapping = {
        "brand": "补充商品品牌信息。",
        "material": "补充商品材质信息。",
        "snowboard_width": "补充滑雪板宽度信息。",
        "binding_compatibility": "补充固定器兼容性信息。"
    }

    recommendations = []

    # 4. 根据缺失属性生成建议
    for attribute in missing_attributes:

        if not isinstance(attribute, str) or not attribute.strip():
            raise ValueError("缺失属性名称无效")

        attribute_key = attribute.strip().lower()

        recommendation = recommendation_mapping.get(
            attribute_key,
            f"补充商品属性信息：{attribute.strip()}。"
        )

        # 清理建议文字前后的空格
        recommendation = recommendation.strip()

        # 避免重复添加
        if recommendation not in recommendations:
            recommendations.append(recommendation)

    # 5. 根据商品风险生成建议
    for risk in risk_analysis:

        if not isinstance(risk, dict):
            raise ValueError("风险信息必须是字典")

        risk_type = risk.get("risk_type")

        if risk_type == "ambiguous_product_name":

            recommendation = (
                "核实商品名称中的Complete是否意味着"
                "包含固定器或其他配件，并明确实际包含内容。"
            )

            # 清理建议文字前后的空格
            recommendation = recommendation.strip()

            # 避免重复添加
            if recommendation not in recommendations:
                recommendations.append(recommendation)

    # 6. 返回优化建议
    return recommendations


# ==========================================
# Product Analysis Agent 基础模块结束
# ==========================================
