
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ==========================================
# 1. 定义 Agent 的共享状态 State
# ==========================================

class ProductState(TypedDict, total=False):

    query: str

    cleaned_query: str

    category: str

    result: str


# ==========================================
# 2. 创建第一个 Node：清理用户输入
# ==========================================

def clean_query(state: ProductState):

    print("\n========== Node 1：清理用户输入 ==========")

    query = state["query"].strip()

    print("原始需求：", state["query"])

    print("清理后需求：", query)

    return {
        "cleaned_query": query
    }


# ==========================================
# 3. 创建第二个 Node：分析商品分类
# ==========================================

def classify_product(state: ProductState):

    print("\n========== Node 2：商品分类 ==========")

    query = state["cleaned_query"].lower()

    # 这里使用规则分类，暂时不调用 AI

    category_rules = {

        "Electronics": [
            "headphones",
            "earbuds",
            "wireless",
            "bluetooth",
            "keyboard",
            "mouse"
        ],

        "Pet Supplies": [
            "dog",
            "cat",
            "pet",
            "grooming"
        ],

        "Sports & Outdoors": [
            "camping",
            "hiking",
            "tent",
            "sleeping bag",
            "outdoor"
        ],

        "Home & Kitchen": [
            "coffee",
            "kitchen",
            "vacuum",
            "blender"
        ],

        "Travel": [
            "luggage",
            "travel",
            "suitcase",
            "backpack"
        ]
    }

    category = "Other"

    for name, keywords in category_rules.items():

        if any(keyword in query for keyword in keywords):

            category = name

            break

    print("识别商品分类：", category)

    return {
        "category": category
    }


# ==========================================
# 4. 创建第三个 Node：整理结果
# ==========================================

def format_result(state: ProductState):

    print("\n========== Node 3：整理分析结果 ==========")

    result = (
        "用户需求：" + state["cleaned_query"]
        + "\n商品分类：" + state["category"]
    )

    print(result)

    return {
        "result": result
    }


# ==========================================
# 5. 创建 StateGraph
# ==========================================

print("\n正在创建 LangGraph 工作流...")

builder = StateGraph(ProductState)


# ==========================================
# 6. 注册三个 Node
# ==========================================

builder.add_node("clean", clean_query)

builder.add_node("classify", classify_product)

builder.add_node("format", format_result)


# ==========================================
# 7. 使用 Edge 连接节点
# ==========================================

builder.add_edge(START, "clean")

builder.add_edge("clean", "classify")

builder.add_edge("classify", "format")

builder.add_edge("format", END)


# ==========================================
# 8. 编译工作流
# ==========================================

graph = builder.compile()

print("LangGraph 工作流创建成功！")


# ==========================================
# 9. 接收用户输入
# ==========================================

print("\n================================")

print("跨境电商商品分析 Agent")

print("================================")

query = input("\n请输入商品搜索需求：")


if not query.strip():

    raise ValueError("商品搜索需求不能为空")


# ==========================================
# 10. 初始化 State
# ==========================================

initial_state = {

    "query": query

}


# ==========================================
# 11. 执行 LangGraph
# ==========================================

print("\n开始执行 LangGraph 工作流...")

final_state = graph.invoke(initial_state)


# ==========================================
# 12. 输出最终结果
# ==========================================

print("\n========== 最终 State ==========")

print(final_state)

print("\n========== 最终分析结果 ==========")

print(final_state["result"])

print("\nLangGraph 工作流执行完成！")
