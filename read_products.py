
import csv
from pathlib import Path


# ==================================
# 第一部分：定义CSV文件路径
# ==================================

CSV_FILE = Path("products.csv")


# ==================================
# 第二部分：读取商品数据
# ==================================

def load_products():

    # 判断文件是否存在
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"找不到商品文件：{CSV_FILE}"
        )

    products = []

    # 打开CSV文件
    with open(
        CSV_FILE,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        # 将CSV内容转换成字典
        reader = csv.DictReader(file)

        # 检查必要字段是否存在
        required_fields = [
            "product_id",
            "name",
            "market",
            "features"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in (reader.fieldnames or [])
        ]

        if missing_fields:
            raise ValueError(
                f"CSV缺少字段：{missing_fields}"
            )

        # 逐行读取商品
        for row_number, row in enumerate(reader, start=2):

            # 提取并清理数据
            product = {
                "product_id": (row["product_id"] or "").strip(),
                "name": (row["name"] or "").strip(),
                "market": (row["market"] or "").strip(),
                "features": [
                    feature.strip()
                    for feature in (row["features"] or "").split(";")
                    if feature.strip()
                ]
            }

            # 检查字段内容是否为空
            if not all([
                product["product_id"],
                product["name"],
                product["market"],
                product["features"]
            ]):
                print(f"第{row_number}行数据不完整，已跳过")
                continue

            products.append(product)

    return products


# ==================================
# 第三部分：显示读取结果
# ==================================

def main():

    print("==============================")
    print("Amazon商品数据读取系统")
    print("==============================")

    try:

        products = load_products()

        print(f"\n成功读取商品数量：{len(products)}")

        for product in products:

            print("\n------------------------------")

            print("商品编号：", product["product_id"])
            print("商品名称：", product["name"])
            print("目标市场：", product["market"])

            print("商品卖点：")

            for feature in product["features"]:
                print("-", feature)

        print("\n商品数据读取完成！")

    except Exception as error:

        print("\n程序执行失败：", error)


if __name__ == "__main__":
    main()
