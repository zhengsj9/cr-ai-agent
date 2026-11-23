
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda


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
    base_url=base_url,
    temperature=0
)


# =====================================
# 3. 创建 Prompt Template
# =====================================

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
你是一个专业的跨境电商商品需求分析助手。

请分析用户的商品搜索需求。

请输出以下信息：

1. 商品分类
2. 商品搜索关键词
3. 用户的核心需求

分类只能从以下选项中选择：

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

请使用清晰的中文回答。
"""
    ),
    (
        "human",
        "用户的商品需求：{query}"
    )
])


# =====================================
# 4. 定义 Python 处理函数
# =====================================

# 步骤一：清理用户输入
def clean_query(query):

    query = query.strip()

    if not query:
        raise ValueError("商品搜索需求不能为空")

    print("步骤1：用户输入清理完成")

    return query


# 步骤二：整理输入数据
def prepare_input(query):

    data = {
        "query": query
    }

    print("步骤2：输入数据整理完成")

    return data


# 步骤六：整理最终结果
def format_result(result):

    print("步骤6：最终结果整理完成")

    return (
        "\n========== 商品需求分析结果 ==========\n"
        + result
    )


# =====================================
# 5. 将 Python 函数包装成 Runnable
# =====================================

clean_step = RunnableLambda(clean_query)

prepare_step = RunnableLambda(prepare_input)

format_step = RunnableLambda(format_result)


# =====================================
# 6. 组合多个 Runnable
# =====================================

chain = (
    clean_step
    | prepare_step
    | prompt
    | llm
    | StrOutputParser()
    | format_step
)


# =====================================
# 7. 接收用户输入
# =====================================

print("\n==============================")
print("LangChain 多步骤 Chain 系统")
print("==============================")

query = input("\n请输入商品搜索需求：")


# =====================================
# 8. 执行整个 Chain
# =====================================

print("\n开始执行 Chain...\n")

result = chain.invoke(query)


# =====================================
# 9. 输出最终结果
# =====================================

print(result)

print("\nChain 执行完成！")
