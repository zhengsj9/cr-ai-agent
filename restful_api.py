
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


# ==========================================
# 1. 创建 FastAPI 应用
# ==========================================

app = FastAPI(
    title="E-commerce Product Management API",
    description="跨境电商商品 CRUD 管理系统",
    version="1.0.0"
)


# ==========================================
# 2. 定义商品数据模型
# ==========================================

class Product(BaseModel):

    product_id: str = Field(
        min_length=1
    )

    name: str = Field(
        min_length=1
    )

    category: str

    price: float = Field(
        gt=0
    )

    market: str


# PATCH 使用的部分更新模型
class ProductUpdate(BaseModel):

    name: str | None = None

    category: str | None = None

    price: float | None = Field(
        default=None,
        gt=0
    )

    market: str | None = None


# ==========================================
# 3. 模拟商品数据库
# ==========================================

products_db = {

    "P001": {
        "product_id": "P001",
        "name": "Wireless Bluetooth Earbuds",
        "category": "Electronics",
        "price": 29.99,
        "market": "United States"
    },

    "P060": {
        "product_id": "P060",
        "name": "Dog Harness",
        "category": "Pet Supplies",
        "price": 19.99,
        "market": "United States"
    },

    "P015": {
        "product_id": "P015",
        "name": "Noise Cancelling Headphones",
        "category": "Electronics",
        "price": 79.99,
        "market": "United States"
    }

}


# ==========================================
# 4. GET：查询所有商品
# ==========================================

@app.get("/products")
def get_products(

    category: str | None = None,

    market: str | None = None,

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    )

):

    result = list(products_db.values())

    # 按分类筛选
    if category:

        result = [
            product
            for product in result
            if product["category"].lower() == category.lower()
        ]

    # 按市场筛选
    if market:

        result = [
            product
            for product in result
            if product["market"].lower() == market.lower()
        ]

    # 限制返回数量
    result = result[:limit]

    return {

        "status": "success",

        "total": len(result),

        "products": result

    }


# ==========================================
# 5. GET：查询单个商品
# ==========================================

@app.get("/products/{product_id}")
def get_product(product_id: str):

    product = products_db.get(product_id)

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )

    return {

        "status": "success",

        "product": product

    }


# ==========================================
# 6. POST：新增商品
# ==========================================

@app.post("/products", status_code=201)
def create_product(product: Product):

    product_id = product.product_id

    if product_id in products_db:

        raise HTTPException(
            status_code=409,
            detail="商品 ID 已经存在"
        )

    products_db[product_id] = product.model_dump()

    return {

        "status": "success",

        "message": "商品创建成功",

        "product": products_db[product_id]

    }


# ==========================================
# 7. PUT：完整替换商品
# ==========================================

@app.put("/products/{product_id}")
def replace_product(

    product_id: str,

    product: Product

):

    if product_id not in products_db:

        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )

    if product.product_id != product_id:

        raise HTTPException(
            status_code=400,
            detail="商品 ID 与路径 ID 不一致"
        )

    products_db[product_id] = product.model_dump()

    return {

        "status": "success",

        "message": "商品完整更新成功",

        "product": products_db[product_id]

    }


# ==========================================
# 8. PATCH：部分修改商品
# ==========================================

@app.patch("/products/{product_id}")
def update_product(

    product_id: str,

    update_data: ProductUpdate

):

    product = products_db.get(product_id)

    if product is None:

        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )

    update_fields = update_data.model_dump(
        exclude_unset=True
    )

    if not update_fields:

        raise HTTPException(
            status_code=400,
            detail="没有提供需要修改的字段"
        )

    product.update(update_fields)

    return {

        "status": "success",

        "message": "商品部分更新成功",

        "product": product

    }


# ==========================================
# 9. DELETE：删除商品
# ==========================================

@app.delete("/products/{product_id}")
def delete_product(product_id: str):

    if product_id not in products_db:

        raise HTTPException(
            status_code=404,
            detail="商品不存在"
        )

    deleted_product = products_db.pop(product_id)

    return {

        "status": "success",

        "message": "商品删除成功",

        "product": deleted_product

    }


# ==========================================
# 10. 健康检查
# ==========================================

@app.get("/health")
def health_check():

    return {

        "status": "ok",

        "message": "商品管理 API 运行正常"

    }


print("商品管理 API 已加载！")
