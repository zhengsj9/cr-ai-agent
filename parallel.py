
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel


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
# 4. 创建商品分类 Prompt
# =====================================

category_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是跨境电商商品分类专家。

根据用户的需求判断商品分类。

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
    (
        "human",
        "用户需求：{query}"
    )
])


# =====================================
# 5. 创建关键词提取 Prompt
# =====================================

keyword_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是跨境电商商品搜索关键词专家。

请根据用户需求提取最相关的英文商品搜索关键词。

要求：
1. 返回英文关键词。
2. 提取3到6个相关关键词或短语。
3. 使用逗号分隔。
4. 不要解释。
"""
    ),
    (
        "human",
        "用户需求：{query}"
    )
])


# =====================================
# 6. 创建用户需求分析 Prompt
# =====================================

needs_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是跨境电商用户需求分析专家。

请分析用户真正想解决的问题。

要求：
1. 使用中文回答。
2. 说明用户的核心购买需求。
3. 说明选购时应该关注的重点。
4. 不要编造用户没有提供的信息。
"""
    ),
    (
        "human",
        "用户需求：{query}"
    )
])


# =====================================
# 7. 创建三个独立 Chain
# =====================================

category_chain = (
    category_prompt
    | llm
    | parser
)

keyword_chain = (
    keyword_prompt
    | llm
    | parser
)

needs_chain = (
    needs_prompt
    | llm
    | parser
)


# =====================================
# 8. 使用 RunnableParallel 并行执行
# =====================================

parallel_chain = RunnableParallel(

    category=category_chain,

    keyword=keyword_chain,

    needs=needs_chain
)


# =====================================
# 9. 接收用户输入
# =====================================

print("\n==============================")
print("LangChain 并行商品分析系统")
print("==============================")

query = input("\n请输入商品搜索需求：").strip()

if not query:
    raise ValueError("商品搜索需求不能为空")


# =====================================
# 10. 执行并行 Chain
# =====================================

print("\nAI 正在并行分析商品需求...")

result = parallel_chain.invoke({
    "query": query
})


# =====================================
# 11. 输出三个任务的结果
# =====================================

print("\n========== 并行分析结果 ==========")

print("\n1. 商品分类：")
print(result["category"])

print("\n2. 商品搜索关键词：")
print(result["keyword"])

print("\n3. 用户核心需求：")
print(result["needs"])


# =====================================
# 12. 输出完整结果
# =====================================

print("\n========== 完整结果字典 ==========")

print(result)

print("\n并行 Chain 执行完成！")
