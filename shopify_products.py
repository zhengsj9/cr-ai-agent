
import os
import json
import csv
import requests
from dotenv import load_dotenv


# ==========================================
# 1. 加载环境变量
# ==========================================

load_dotenv()

SHOP = os.getenv("SHOPIFY_SHOP")
CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SHOPIFY_CLIENT_SECRET")

if not all([SHOP, CLIENT_ID, CLIENT_SECRET]):
    raise ValueError(
        "Shopify 配置不完整，请检查 .env 文件！"
    )


# ==========================================
# 2. 获取 Shopify Access Token
# ==========================================

def get_access_token():

    print("正在获取 Shopify Access Token...")

    url = (
        f"https://{SHOP}.myshopify.com"
        "/admin/oauth/access_token"
    )

    response = requests.post(
        url,
        json={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        },
        timeout=30
    )

    response.raise_for_status()

    token_data = response.json()

    access_token = token_data["access_token"]

    print("Access Token 获取成功！")

    return access_token


# ==========================================
# 3. 分页获取 Shopify 商品
# ==========================================

def get_products(token):

    print("\n正在连接 Shopify GraphQL API...")

    url = (
        f"https://{SHOP}.myshopify.com"
        "/admin/api/2026-10/graphql.json"
    )

    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token
    }

    # 保存所有商品
    all_products = []

    # 初始游标
    cursor = None

    # 分页计数
    page_number = 0

    while True:

        query = """
        query GetProducts($cursor: String) {
            products(first: 10, after: $cursor) {

                pageInfo {
                    hasNextPage
                    endCursor
                }

                edges {
                    node {
                        id
                        title
                        status
                        vendor
                        productType

                        variants(first: 5) {
                            edges {
                                node {
                                    price
                                    inventoryQuantity
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        # 发送 GraphQL 请求
        response = requests.post(
            url,
            headers=headers,
            json={
                "query": query,
                "variables": {
                    "cursor": cursor
                }
            },
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        # 检查 GraphQL 错误
        if result.get("errors"):
            raise RuntimeError(
                f"GraphQL 查询失败：{result['errors']}"
            )

        # 获取商品数据
        products_data = result["data"]["products"]

        edges = products_data["edges"]

        # 保存当前页商品
        for edge in edges:

            product = edge["node"]

            all_products.append(product)

        # 获取分页信息
        page_info = products_data["pageInfo"]

        page_number += 1

        print(
            f"第 {page_number} 页获取 "
            f"{len(edges)} 件商品，"
            f"累计获取 {len(all_products)} 件"
        )

        # 判断是否还有下一页
        if not page_info["hasNextPage"]:

            print("\n所有商品分页读取完成！")

            break

        # 更新游标
        cursor = page_info["endCursor"]

    return all_products


# ==========================================
# 4. 打印商品信息
# ==========================================

def print_products(products):

    print("\n========== Shopify 商品采集结果 ==========")

    print(f"\n成功获取 {len(products)} 件商品！")

    for index, product in enumerate(products, start=1):

        print("\n" + "=" * 45)

        print(f"商品编号：{index}")

        print("商品 ID：", product["id"])

        print("商品名称：", product["title"])

        print("商品状态：", product["status"])

        print("品牌：", product["vendor"])

        print("商品类型：", product["productType"])

        variants = product["variants"]["edges"]

        print(f"\n商品变体数量：{len(variants)}")

        for variant_index, variant in enumerate(
            variants,
            start=1
        ):

            variant_data = variant["node"]

            print(f"\n变体 {variant_index}")

            print("价格：", variant_data["price"])

            print(
                "库存：",
                variant_data["inventoryQuantity"]
            )

    print("\n" + "=" * 45)

    print("Shopify 商品采集完成！")

    print(f"本次共采集：{len(products)} 件商品")


# ==========================================
# 5. 保存 JSON 和 CSV 文件
# ==========================================

def save_products(products):

    # -------------------------------
    # 5.1 保存 JSON
    # -------------------------------

    json_file = "shopify_products.json"

    with open(
        json_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            products,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"\nJSON 保存成功：{json_file}")

    # -------------------------------
    # 5.2 保存 CSV
    # -------------------------------

    csv_file = "shopify_products.csv"

    csv_headers = [
        "商品ID",
        "商品名称",
        "商品状态",
        "品牌",
        "商品类型",
        "价格",
        "库存"
    ]

    with open(
        csv_file,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=csv_headers
        )

        # 写入表头
        writer.writeheader()

        # 遍历商品
        for product in products:

            variants = product["variants"]["edges"]

            # 没有变体时也保存商品信息
            if not variants:
                variants = [{"node": {}}]

            # 遍历商品变体
            for variant in variants:

                variant_data = variant["node"]

                writer.writerow({

                    "商品ID": product["id"],

                    "商品名称": product["title"],

                    "商品状态": product["status"],

                    "品牌": product["vendor"],

                    "商品类型": product["productType"],

                    "价格": variant_data.get(
                        "price", ""
                    ),

                    "库存": variant_data.get(
                        "inventoryQuantity", ""
                    )

                })

    print(f"CSV 保存成功：{csv_file}")

    print("\n商品数据保存完成！")


# ==========================================
# 6. 主程序入口
# ==========================================

if __name__ == "__main__":

    try:

        print("========== Shopify 商品采集程序 ==========")

        # 第一步：获取 Token
        token = get_access_token()

        # 第二步：分页获取商品
        products = get_products(token)

        # 第三步：打印商品
        print_products(products)

        # 第四步：保存 JSON 和 CSV
        save_products(products)

        print("\n========== 全部任务执行完成 ==========")

    except requests.exceptions.RequestException as e:

        print("\nShopify 网络请求失败：")
        print(e)

    except (KeyError, TypeError) as e:

        print("\n商品数据解析失败：")
        print(e)

    except Exception as e:

        print("\n程序发生错误：")
        print(e)
