
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda
)


# =====================================
# 1. 加载环境变量
# =====================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

if not api_key or not model_name:
    raise ValueError("请检查 .env 文件中的 API 配置")


# =====================================
# 2. 创建 Chat Model
# =====================================

llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url or None,
    temperature=0
)


# =====================================
# 3. 创建输出解析器
# =====================================

parser = StrOutputParser()


# =====================================
# 4. 创建三个 Prompt
# =====================================

category_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是跨境电商商品分类专家。

根据用户需求判断商品分类。

只能从以下分类中选择：

Electronics
Sports & Outdoors
Pet Supplies
Home & Kitchen
Office Supplies
Travel
Garden & Outdoor
Health & Personal Care
Toys & Crafts
Tools & Hardware
Other

只返回分类名称，不要解释。
"""
    ),
    ("human", "用户需求：{query}")
])


keyword_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是跨境电商商品搜索关键词专家。

根据用户需求提取3到6个英文商品搜索关键词或短语。

使用英文逗号分隔，不要解释。
"""
    ),
    ("human", "用户需求：{query}")
])


needs_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是跨境电商用户需求分析专家。

请使用中文分析：

1. 用户真正想解决的问题。
2. 用户的核心购买需求。
3. 用户选购商品时应该关注的重点。

不要编造用户没有提供的信息。
"""
    ),
    ("human", "用户需求：{query}")
])


# =====================================
# 5. 创建三个独立 Chain
# =====================================

category_chain = category_prompt | llm | parser

keyword_chain = keyword_prompt | llm | parser

needs_chain = needs_prompt | llm | parser


# =====================================
# 6. 测试 RunnablePassthrough
# =====================================

print("\n========== 第一步：原样传递数据 ==========")

input_data = {
    "query": "I need wireless headphones",
    "user_id": 1001,
    "source": "Amazon"
}

passthrough = RunnablePassthrough()

passthrough_result = passthrough.invoke(input_data)

print("原始数据：")
print(input_data)

print("\n传递后的数据：")
print(passthrough_result)

print("\n数据是否一致：", input_data == passthrough_result)


# =====================================
# 7. 使用 RunnableLambda 计算数据
# =====================================

print("\n========== 第二步：增加辅助字段 ==========")

prepare_chain = RunnablePassthrough.assign(

    query_length=RunnableLambda(
        lambda data: len(data["query"])
    ),

    query_upper=RunnableLambda(
        lambda data: data["query"].upper()
    )

)

prepare_result = prepare_chain.invoke(input_data)

print("增加字段后的数据：")
print(prepare_result)


# =====================================
# 8. 使用 RunnableAssign 增加 AI 分析结果
# =====================================

print("\n========== 第三步：增加 AI 分析结果 ==========")

analysis_chain = RunnablePassthrough.assign(

    category=category_chain,

    keyword=keyword_chain,

    needs=needs_chain

)

# 查看 assign 创建的对象类型
print(
    "Assign 对象类型：",
    type(analysis_chain)
)


# =====================================
# 9. 组合完整 Chain
# =====================================

full_chain = (

    RunnablePassthrough()

    | prepare_chain

    | analysis_chain

)


# =====================================
# 10. 执行完整 Chain
# =====================================

print("\n========== 开始执行完整 Chain ==========")

result = full_chain.invoke(input_data)


# =====================================
# 11. 输出最终数据
# =====================================

print("\n========== 最终分析结果 ==========")

print("\n1. 原始用户需求：")
print(result["query"])

print("\n2. 用户 ID：")
print(result["user_id"])

print("\n3. 数据来源：")
print(result["source"])

print("\n4. 需求字符长度：")
print(result["query_length"])

print("\n5. 大写需求：")
print(result["query_upper"])

print("\n6. 商品分类：")
print(result["category"])

print("\n7. 商品搜索关键词：")
print(result["keyword"])

print("\n8. 用户核心需求：")
print(result["needs"])


# =====================================
# 12. 检查数据是否完整
# =====================================

print("\n========== 数据完整性检查 ==========")

required_keys = [
    "query",
    "user_id",
    "source",
    "query_length",
    "query_upper",
    "category",
    "keyword",
    "needs"
]

for key in required_keys:

    print(
        key,
        "：",
        "存在" if key in result else "缺失"
    )

print("\nRunnablePassthrough 和 RunnableAssign 实战完成！")
