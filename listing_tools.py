
from read_products import load_products
from batch_listing import generate_listing


# ==================================
# 第一部分：定义Listing工具
# ==================================

def generate_product_listing(product_id):
    """
    根据商品编号生成Amazon Listing。

    参数：
        product_id：商品编号，例如P001

    返回：
        商品Listing生成结果
    """

    # 1. 读取CSV中的商品
    products = load_products()

    # 2. 根据商品编号查找商品
    target_product = None

    for product in products:

        if product["product_id"] == product_id:
            target_product = product
            break

    # 3. 如果没有找到商品，返回错误
    if target_product is None:
        raise ValueError(
            f"找不到商品编号：{product_id}"
        )

    # 4. 调用之前已经开发好的Listing生成函数
    result = generate_listing(target_product)

    # 5. 返回生成结果
    return result
