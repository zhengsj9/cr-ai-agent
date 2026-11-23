
from fastapi import FastAPI
from pydantic import BaseModel, Field


# ==========================================
# 1. 创建 FastAPI 应用
# ==========================================

app = FastAPI(
    title="Cross-border E-commerce AI Agent",
    description="跨境电商商品分析 API",
    version="1.0.0"
)


# ==========================================
# 2. 定义请求数据模型
# ==========================================

class ProductRequest(BaseModel):

    query: str = Field(
        min_length=1,
        description="用户的商品搜索需求"
    )


# ==========================================
# 3. 定义 GET 接口：健康检查
# ==========================================

@app.get("/")
def home():

    return {
        "message": "欢迎使用跨境电商 AI Agent API",
        "status": "running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "message": "API 服务运行正常"
    }


# ==========================================
# 4. 定义商品分类函数
# ==========================================

def classify_product(query: str):

    query = query.lower()

    category_rules = {

        "Electronics": [
            "headphones",
            "earbuds",
            "wireless",
            "bluetooth",
            "耳机",
            "蓝牙"
        ],

        "Pet Supplies": [
            "dog",
            "cat",
            "pet",
            "狗",
            "猫",
            "宠物"
        ],

        "Sports & Outdoors": [
            "camping",
            "hiking",
            "tent",
            "outdoor",
            "露营",
            "帐篷"
        ],

        "Home & Kitchen": [
            "kitchen",
            "coffee",
            "blender",
            "厨房",
            "咖啡"
        ],

        "Travel": [
            "luggage",
            "travel",
            "backpack",
            "旅行",
            "背包"
        ]
    }

    for category, keywords in category_rules.items():

        if any(keyword in query for keyword in keywords):

            return category

    return "Other"


# ==========================================
# 5. 定义 POST 接口：商品需求分析
# ==========================================

@app.post("/products/analyze")
def analyze_product(request: ProductRequest):

    query = request.query.strip()

    if not query:

        return {
            "status": "error",
            "message": "商品搜索需求不能为空"
        }

    category = classify_product(query)

    return {

        "status": "success",

        "query": query,

        "category": category,

        "message": "商品需求分析完成"

    }


# ==========================================
# 6. 定义 GET 接口：查看 API 信息
# ==========================================

@app.get("/api/info")
def api_info():

    return {

        "project": "Cross-border E-commerce AI Agent",

        "version": "1.0.0",

        "endpoints": [

            "GET /",

            "GET /health",

            "POST /products/analyze",

            "GET /api/info"

        ]

    }

