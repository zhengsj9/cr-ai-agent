
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ==========================================
# 1. 定义共享状态 State
# ==========================================

class ProductState(TypedDict, total=False):

    query: str
    cleaned_query: str
    category: str
    handler: str
    result: str


# ==========================================
# 2. Node 1：清理用户输入
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
# 3. Node 2：识别商品分类
# ==========================================

def classify_product(state: ProductState):

    print("\n========== Node 2：识别商品分类 ==========")

    query = state["cleaned_query"].lower()

    category_rules = {

        "Electronics": [
            "headphones",
            "earbuds",
            "wireless",
            "bluetooth",
            "keyboard",
            "mouse",
            "耳机",
            "蓝牙",
            "键盘",
            "鼠标"
        ],

        "Pet Supplies": [
            "dog",
            "cat",
            "pet",
            "grooming",
            "狗",
            "猫",
            "宠物",
            "狗粮"
        ],

        "Sports & Outdoors": [
            "camping",
            "hiking",
            "tent",
            "sleeping bag",
            "outdoor",
            "露营",
            "登山",
            "帐篷",
            "户外"
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
# 4. 创建路由函数
# ==========================================

def route_by_category(state: ProductState):

    print("\n========== Conditional Routing ==========")

    category = state["category"]

    if category == "Electronics":

        print("路由结果：进入电子产品处理节点")

        return "electronics"

    elif category == "Pet Supplies":

        print("路由结果：进入宠物用品处理节点")

        return "pet"

    elif category == "Sports & Outdoors":

        print("路由结果：进入户外用品处理节点")

        return "outdoor"

    else:

        print("路由结果：进入默认处理节点")

        return "other"


# ==========================================
# 5. Node 3：电子产品处理
# ==========================================

def electronics_node(state: ProductState):

    print("\n========== Electronics Node ==========")

    result = (
        "电子产品分析完成。"
        "建议重点关注连接方式、兼容性和续航能力。"
    )

    return {
        "handler": "Electronics Node",
        "result": result
    }


# ==========================================
# 6. Node 4：宠物用品处理
# ==========================================

def pet_node(state: ProductState):

    print("\n========== Pet Supplies Node ==========")

    result = (
        "宠物用品分析完成。"
        "建议重点关注宠物类型、使用场景和安全性。"
    )

    return {
        "handler": "Pet Supplies Node",
        "result": result
    }


# ==========================================
# 7. Node 5：户外用品处理
# ==========================================

def outdoor_node(state: ProductState):

    print("\n========== Sports & Outdoors Node ==========")

    result = (
        "户外用品分析完成。"
        "建议重点关注使用环境、耐用性和便携性。"
    )

    return {
        "handler": "Sports & Outdoors Node",
        "result": result
    }


# ==========================================
# 8. Node 6：默认处理
# ==========================================

def other_node(state: ProductState):

    print("\n========== Other Node ==========")

    result = (
        "暂时无法确定具体商品类别。"
        "建议用户提供更详细的商品需求。"
    )

    return {
        "handler": "Other Node",
        "result": result
    }


# ==========================================
# 9. Node 7：整理最终结果
# ==========================================

def format_result(state: ProductState):

    print("\n========== Format Node ==========")

    final_result = f"""
用户需求：{state["cleaned_query"]}

商品分类：{state["category"]}

执行节点：{state["handler"]}

处理结果：{state["result"]}
"""

    return {
        "result": final_result
    }


# ==========================================
# 10. 创建 StateGraph
# ==========================================

print("\n正在创建 Day 19 Agent 工作流...")

builder = StateGraph(ProductState)


# ==========================================
# 11. 注册所有 Node
# ==========================================

builder.add_node("clean", clean_query)

builder.add_node("classify", classify_product)

builder.add_node("electronics_node", electronics_node)

builder.add_node("pet_node", pet_node)

builder.add_node("outdoor_node", outdoor_node)

builder.add_node("other_node", other_node)

builder.add_node("format", format_result)


# ==========================================
# 12. 定义普通 Edge
# ==========================================

builder.add_edge(START, "clean")

builder.add_edge("clean", "classify")


# ==========================================
# 13. 定义 Conditional Edge
# ==========================================

builder.add_conditional_edges(

    "classify",

    route_by_category,

    {

        "electronics": "electronics_node",

        "pet": "pet_node",

        "outdoor": "outdoor_node",

        "other": "other_node"

    }

)


# ==========================================
# 14. 各个分支汇总到 Format Node
# ==========================================

builder.add_edge("electronics_node", "format")

builder.add_edge("pet_node", "format")

builder.add_edge("outdoor_node", "format")

builder.add_edge("other_node", "format")


builder.add_edge("format", END)


# ==========================================
# 15. 编译工作流
# ==========================================

graph = builder.compile()

print("Day 19 Agent 工作流创建成功！")


# ==========================================
# 16. 接收用户输入
# ==========================================

print("\n==============================")
print("跨境电商智能商品 Agent")
print("==============================")

query = input("\n请输入商品搜索需求：").strip()

if not query:

    raise ValueError("商品搜索需求不能为空")


# ==========================================
# 17. 初始化 State
# ==========================================

initial_state = {

    "query": query

}


# ==========================================
# 18. 执行 Agent
# ==========================================

print("\n开始执行 Agent 工作流...")

final_state = graph.invoke(initial_state)


# ==========================================
# 19. 输出最终结果
# ==========================================

print("\n========== 最终执行结果 ==========")

print(final_state["result"])

print("\n实际执行节点：", final_state["handler"])

print("\nDay 19 Agent 执行完成！")
