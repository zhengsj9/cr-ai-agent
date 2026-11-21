
import csv
from pathlib import Path


# 1. 获取当前 Python 文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# 2. 拼接商品数据文件路径
PRODUCT_FILE = BASE_DIR / "products.csv"


# 3. 加载商品知识库
def load_products():
    products = []

    with PRODUCT_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
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


# 4. 根据商品编号检索
def search_product(product_id):
    products = load_products()

    for product in products:
        if product["product_id"].upper() == product_id.upper():
            return product

    return None


# 5. 格式化检索结果
def format_product(product):
    features = "\n".join(
        f"- {feature}"
        for feature in product["features"]
    )

    return (
        f"商品编号：{product['product_id']}\n"
        f"商品名称：{product['name']}\n"
        f"目标市场：{product['market']}\n"
        f"商品卖点：\n{features}"
    )


# 6. 程序入口
def main():
    print("=== 跨境电商商品知识库 ===")

    product_id = input("请输入商品编号：").strip()

    if not product_id:
        print("商品编号不能为空")
        return

    try:
        product = search_product(product_id)

        if product is None:
            print("知识库中未找到该商品")
            return

        print("\n=== 检索结果 ===")
        print(format_product(product))

    except (OSError, KeyError) as error:
        print("读取商品知识库失败：", error)


if __name__ == "__main__":
    main()
