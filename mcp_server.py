
import json

from mcp.server import MCPServer


# =====================================
# 1. 创建 MCP Server
# =====================================

mcp = MCPServer(
    "E-commerce Product Server",
    instructions="提供跨境电商商品查询服务"
)


# =====================================
# 2. 创建模拟商品数据库
# =====================================

products_db = {

    "P001": {
        "product_id": "P001",
        "name": "Wireless Bluetooth Earbuds",
        "category": "Electronics",
        "price": 29.99,
        "market": "United States"
    },

    "P015": {
        "product_id": "P015",
        "name": "Noise Cancelling Headphones",
        "category": "Electronics",
        "price": 79.99,
        "market": "United States"
    },

    "P060": {
        "product_id": "P060",
        "name": "Dog Harness",
        "category": "Pet Supplies",
        "price": 19.99,
        "market": "United States"
    }

}


# =====================================
# 3. 注册商品搜索工具
# =====================================

@mcp.tool()
def search_product(keyword: str) -> list[dict]:
    """
    根据关键词搜索商品。
    """

    keyword = keyword.strip().lower()

    if not keyword:
        return []

    results = []

    for product in products_db.values():

        searchable_text = (
            product["name"] + " " +
            product["category"] + " " +
            product["product_id"]
        ).lower()

        if keyword in searchable_text:

            results.append(product)

    return results


# =====================================
# 4. 注册商品详情查询工具
# =====================================

@mcp.tool()
def get_product(product_id: str) -> dict:
    """
    根据商品 ID 查询商品详情。
    """

    product = products_db.get(product_id)

    if product is None:

        return {
            "status": "error",
            "message": "商品不存在"
        }

    return {
        "status": "success",
        "product": product
    }


# =====================================
# 5. 注册商品目录 Resource
# =====================================

@mcp.resource("products://catalog")
def get_product_catalog() -> str:
    """
    获取全部商品目录。
    """

    return json.dumps(
        list(products_db.values()),
        ensure_ascii=False,
        indent=2
    )


# =====================================
# 6. 启动 MCP Server
# =====================================

if __name__ == "__main__":

    mcp.run(transport="stdio")
