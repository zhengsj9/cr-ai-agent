
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ==========================================
# 1. 定义共享 State
# ==========================================

class ProductState(TypedDict, total=False):

    query: str
    cleaned_query: str
    category: str
    result: str
    status: str
    error: str


# ==========================================
# 2. Node 1：清理用户输入
# ==========================================

def clean_query(state: ProductState):

    print("\n========== Node 1：清理输入 ==========")

    try:

        query = state["query"].strip()

        if not query:

            raise ValueError("用户搜索需求不能为空")

        return {
            "cleaned_query": query,
            "status": "success",
            "error": ""
        }

    except Exception as e:

        print("输入处理失败：", e)

        return {
            "status": "error",
            "error": str(e)
        }


# ==========================================
# 3. Node 2：商品分类
# ==========================================

def classify_product(state: ProductState):

    print("\n========== Node 2：商品分类 ==========")

    try:

        query = state["cleaned_query"].lower()

        if "分类失败" in query:

            raise RuntimeError("模拟商品分类异常")

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
            ]

        }

        category = "Other"

        for name, keywords in category_rules.items():

            if any(keyword in query for keyword in keywords):

                category = name

                break

        print("识别分类：", category)

        return {
            "category": category,
            "status": "success",
            "error": ""
        }

    except Exception as e:

        print("商品分类失败：", e)

        return {
            "status": "error",
            "error": str(e)
        }


# ==========================================
# 4. Node 3：正常业务处理
# ==========================================

def process_product(state: ProductState):

    print("\n========== Node 3：商品业务处理 ==========")

    try:

        category = state["category"]

        if category == "Electronics":

            raise RuntimeError("模拟商品分析服务异常")

        result = (
            "商品需求分析成功！"
            f" 商品分类：{category}"
            "。可以继续进行商品检索。"
        )

        print(result)

        return {
            "result": result,
            "status": "success",
            "error": ""
        }

    except Exception as e:

        print("商品处理失败：", e)

        return {
            "status": "error",
            "error": str(e)
        }


# ==========================================
# 5. 路由函数：判断执行状态
# ==========================================

def route_by_status(state: ProductState):

    print("\n========== 判断工作流状态 ==========")

    if state.get("status") == "error":

        print("检测到异常，进入错误处理节点")

        return "error"

    print("执行正常，进入结果输出节点")

    return "success"


# ==========================================
# 6. Node 4：异常处理
# ==========================================

def error_handler(state: ProductState):

    print("\n========== Error Handler ==========")

    error_message = state.get(
        "error",
        "未知错误"
    )

    print("捕获的错误：", error_message)

    result = (
        "很抱歉，商品 Agent 执行失败。"
        f" 错误原因：{error_message}"
        "。请稍后重试或联系技术支持。"
    )

    return {
        "result": result,
        "status": "error"
    }


# ==========================================
# 7. Node 5：统一输出结果
# ==========================================

def format_result(state: ProductState):

    print("\n========== 最终结果 ==========")

    print(state["result"])

    return {}


# ==========================================
# 8. 创建 StateGraph
# ==========================================

builder = StateGraph(ProductState)


# ==========================================
# 9. 注册节点
# ==========================================

builder.add_node("clean", clean_query)

builder.add_node("classify", classify_product)

builder.add_node("process", process_product)

builder.add_node("error_handler", error_handler)

builder.add_node("format", format_result)


# ==========================================
# 10. 定义普通 Edge
# ==========================================

builder.add_edge(START, "clean")


# ==========================================
# 11. 清理输入后的条件路由
# ==========================================

builder.add_conditional_edges(

    "clean",

    route_by_status,

    {
        "success": "classify",
        "error": "error_handler"
    }

)


# ==========================================
# 12. 分类后的条件路由
# ==========================================

builder.add_conditional_edges(

    "classify",

    route_by_status,

    {
        "success": "process",
        "error": "error_handler"
    }

)


# ==========================================
# 13. 业务处理后的条件路由
# ==========================================

builder.add_conditional_edges(

    "process",

    route_by_status,

    {
        "success": "format",
        "error": "error_handler"
    }

)


# ==========================================
# 14. 异常处理后的统一输出
# ==========================================

builder.add_edge("error_handler", "format")

builder.add_edge("format", END)


# ==========================================
# 15. 编译工作流
# ==========================================

graph = builder.compile()

print("\nDay 20 LangGraph 工作流创建成功！")


# ==========================================
# 16. 接收用户需求
# ==========================================

query = input("\n请输入商品搜索需求：")


# ==========================================
# 17. 初始化 State
# ==========================================

initial_state = {

    "query": query

}


# ==========================================
# 18. 执行工作流
# ==========================================

print("\n开始执行 Agent 工作流...")

final_state = graph.invoke(initial_state)


# ==========================================
# 19. 输出最终状态
# ==========================================

print("\n========== 最终 State ==========")

print(final_state)

print("\n工作流执行结束！")

print("执行状态：", final_state.get("status"))
