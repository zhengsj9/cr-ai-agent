
import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


# =====================================
# 1. 加载环境变量
# =====================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")


if not api_key or not model_name:
    raise ValueError("请检查 .env 中的 API 配置")


# =====================================
# 2. 创建 Chat Model
# =====================================

llm = ChatOpenAI(
    model=model_name,
    api_key=api_key,
    base_url=base_url,
    temperature=0
)


# =====================================
# 3. 定义 AI 返回的数据结构
# =====================================

class ProductClassification(BaseModel):

    category: Literal[
        "Electronics",
        "Sports & Outdoors",
        "Pet Supplies",
        "Home & Kitchen",
        "Office Supplies",
        "Travel",
        "Garden & Outdoor",
        "Health & Personal Care",
        "Toys & Crafts",
        "Tools & Hardware",
        "Other"
    ] = Field(description="商品所属分类")

    keyword: str = Field(
        description="提取出的英文商品搜索关键词"
    )

    confidence: float = Field(
        ge=0,
        le=1,
        description="AI 对分类结果的置信度，范围是 0 到 1"
    )


# =====================================
# 4. 创建 Pydantic Output Parser
# =====================================

parser = PydanticOutputParser(
    pydantic_object=ProductClassification
)


# =====================================
# 5. 创建 Prompt Template
# =====================================

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是一个跨境电商商品分类助手。

请分析用户的商品搜索需求。

你必须返回以下信息：

1. category：商品分类
2. keyword：英文商品搜索关键词
3. confidence：分类置信度，范围 0 到 1

必须遵守以下输出格式：

{format_instructions}

不要添加格式之外的解释。
"""
    ),
    (
        "human",
        "用户的商品需求：{query}"
    )
])


# =====================================
# 6. 组合 LangChain Chain
# =====================================

chain = prompt | llm | parser


# =====================================
# 7. 接收用户输入
# =====================================

query = input("\n请输入商品搜索需求：")


# =====================================
# 8. 调用 AI 并解析结果
# =====================================

print("\nAI 正在分析商品需求...")


result = chain.invoke({
    "query": query,
    "format_instructions": parser.get_format_instructions()
})


# =====================================
# 9. 输出结构化数据
# =====================================

print("\n========== AI 结构化分类结果 ==========")

print("商品分类：", result.category)

print("搜索关键词：", result.keyword)

print("分类置信度：", result.confidence)

print("\n数据类型：", type(result))


# =====================================
# 10. 转换成 Python 字典
# =====================================

result_dict = result.model_dump()

print("\n========== Python 字典 ==========")

print(result_dict)

print("\n字典中的商品分类：", result_dict["category"])

print("\n结构化解析完成！")
