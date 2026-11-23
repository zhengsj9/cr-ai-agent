
import os
from dotenv import load_dotenv

# LangChain 组件
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# ==================================
# 1. 加载环境变量
# ==================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")


# ==================================
# 2. 创建 LangChain Chat Model
# ==================================

llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0
)


# ==================================
# 3. 创建 Prompt Template
# ==================================

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是一个专业的跨境电商商品分类助手。

请判断用户需要什么类型的商品。

只返回商品分类名称：
Electronics
Pet Supplies
Sports & Outdoors
Home & Kitchen
Office Supplies
Travel
Other

不要解释。
"""
    ),
    (
        "human",
        "用户的商品需求：{query}"
    )
])


# ==================================
# 4. 创建 LangChain Chain
# ==================================

chain = prompt | llm


# ==================================
# 5. 接收用户输入
# ==================================

query = input("请输入商品搜索需求：")


# ==================================
# 6. 调用 LangChain
# ==================================

print("\nAI 正在分析商品需求...")

response = chain.invoke({
    "query": query
})


# ==================================
# 7. 输出结果
# ==================================

print("\n========== LangChain 运行结果 ==========")

print("用户需求：", query)

print("AI 分类结果：", response.content)
