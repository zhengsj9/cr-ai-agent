


def calculate_profit(
    sale_price_usd,
    exchange_rate,
    purchase_cost_rmb,
    shipping_cost_rmb,
    commission_rate,
    ad_cost_usd
):
    """
    计算跨境电商商品利润。

    sale_price_usd: 美元售价
    exchange_rate: 美元兑人民币汇率
    purchase_cost_rmb: 人民币采购成本
    shipping_cost_rmb: 人民币物流成本
    commission_rate: 平台佣金比例，例如0.15
    ad_cost_usd: 美元广告费用
    """

    # ==================================
    # 参数校验：检查用户输入是否合理
    # ==================================

    # 1. 售价必须大于0
    if sale_price_usd <= 0:
        raise ValueError("商品售价必须大于0")

    # 2. 汇率必须大于0
    if exchange_rate <= 0:
        raise ValueError("汇率必须大于0")

    # 3. 采购成本不能为负数
    if purchase_cost_rmb < 0:
        raise ValueError("采购成本不能为负数")

    # 4. 物流成本不能为负数
    if shipping_cost_rmb < 0:
        raise ValueError("物流成本不能为负数")

    # 5. 广告费用不能为负数
    if ad_cost_usd < 0:
        raise ValueError("广告费用不能为负数")

    # 6. 佣金比例必须在0到1之间
    if not 0 <= commission_rate <= 1:
        raise ValueError("佣金比例必须在0到1之间")


    # 1. 美元售价换算成人民币
    revenue_rmb = sale_price_usd * exchange_rate

    # 2. 计算平台佣金
    commission_rmb = revenue_rmb * commission_rate

    # 3. 广告费换算成人民币
    ad_cost_rmb = ad_cost_usd * exchange_rate

    # 4. 计算总成本
    total_cost_rmb = (
        purchase_cost_rmb
        + shipping_cost_rmb
        + commission_rmb
        + ad_cost_rmb
    )

    # 5. 计算利润
    profit_rmb = revenue_rmb - total_cost_rmb

    # 6. 计算利润率
    profit_margin = (
        profit_rmb / revenue_rmb * 100
        if revenue_rmb > 0
        else 0
    )

    return {
        "revenue_rmb": round(revenue_rmb, 2),
        "purchase_cost_rmb": round(purchase_cost_rmb, 2),
        "shipping_cost_rmb": round(shipping_cost_rmb, 2),
        "commission_rmb": round(commission_rmb, 2),
        "ad_cost_rmb": round(ad_cost_rmb, 2),
        "total_cost_rmb": round(total_cost_rmb, 2),
        "profit_rmb": round(profit_rmb, 2),
        "profit_margin": round(profit_margin, 2)
    }


def convert_currency(
    amount,
    exchange_rate,
    from_currency,
    to_currency
):
    """
    美元和人民币双向换算。
    """

    # 1. 参数校验
    if amount < 0:
        raise ValueError("换算金额不能为负数")

    if exchange_rate <= 0:
        raise ValueError("汇率必须大于0")

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    # 2. 美元换人民币
    if from_currency == "USD" and to_currency == "RMB":
        result = amount * exchange_rate

    # 3. 人民币换美元
    elif from_currency == "RMB" and to_currency == "USD":
        result = amount / exchange_rate

    # 4. 相同货币
    elif from_currency == to_currency:
        result = amount

    else:
        raise ValueError("目前只支持USD和RMB换算")

    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "exchange_rate": exchange_rate,
        "converted_amount": round(result, 2)
    }

def analyze_margin(
    profit_rmb,
    revenue_rmb,
    target_margin_percent=20
):
    """
    分析商品利润率是否达到目标。
    """

    # 1. 参数校验
    if revenue_rmb <= 0:
        raise ValueError("销售收入必须大于0")

    if not 0 <= target_margin_percent <= 100:
        raise ValueError("目标利润率必须在0到100之间")

    # 2. 计算实际利润率
    actual_margin = (
        profit_rmb / revenue_rmb * 100
    )

    # 3. 判断经营状态
    if profit_rmb < 0:
        status = "亏损"
        message = "商品目前处于亏损状态，需要调整售价或成本。"

    elif actual_margin >= target_margin_percent:
        status = "达到目标"
        message = "商品利润率达到目标，可以进一步评估销售规模。"

    else:
        status = "未达到目标"
        message = "商品利润率低于目标，建议优化采购、物流或广告成本。"

    return {
        "profit_rmb": round(profit_rmb, 2),
        "actual_margin": round(actual_margin, 2),
        "target_margin_percent": target_margin_percent,
        "status": status,
        "message": message
    }

# 单独测试工具
if __name__ == "__main__":

    result = calculate_profit(
        sale_price_usd=29.99,
        exchange_rate=7.2,
        purchase_cost_rmb=35,
        shipping_cost_rmb=12,
        commission_rate=0.15,
        ad_cost_usd=3
    )
    

    print("跨境电商利润计算结果：")

    for key, value in result.items():
        print(f"{key}: {value}")
