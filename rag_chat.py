
import os

from dotenv import load_dotenv
from openai import OpenAI

from rag_search import load_products


# ==================================
# 第一部分：加载 DeepSeek 配置
# ==================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

if not api_key or not base_url or not model_name:
    raise ValueError("请检查 .env 中的 API 配置")


client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60.0,
    max_retries=2
)


# ==================================
# 第二部分：中文关键词映射
# ==================================

KEYWORD_MAP = {
    "蓝牙耳机": ["bluetooth earbuds"],
    "蓝牙": ["bluetooth"],
    "充电": ["charging"],
    "usb-c": ["usb-c"],
    "防漏": ["leak-resistant"],
    "保温": ["vacuum insulation"],
    "不锈钢": ["stainless steel"],
    "宠物刷": ["pet grooming brush"],
    "宠物": ["pet"],
    "柔软刷毛": ["soft bristles"]
}


# ==================================
# 第三部分：检索相关商品
# ==================================

def retrieve_products(question):

    products = load_products()

    query = question.lower()

    search_terms = []

    # 将用户的中文关键词转换成商品资料中的英文关键词
    for chinese_word, english_words in KEYWORD_MAP.items():

        if chinese_word in query:

            search_terms.extend(english_words)

    # 允许用户直接使用英文关键词
    search_terms.extend([
        word.lower()
        for word in [
            "bluetooth",
            "earbuds",
            "usb-c",
            "charging",
            "stainless steel",
            "water bottle",
            "pet grooming brush"
        ]
        if word in query
    ])

    # 去除重复关键词
    search_terms = list(set(search_terms))

    results = []

    for product in products:

        content = (
            product["name"] + " " +
            " ".join(product["features"])
        ).lower()

        score = sum(
            1 for term in search_terms
            if term in content
        )

        if score > 0:
            results.append((score, product))

    # 按照匹配分数从高到低排序
    results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [product for score, product in results[:3]]


# ==================================
# 第四部分：整理知识库资料
# ==================================

def build_context(products):

    context = []

    for product in products:

        features = "\n".join(
            f"- {feature}"
            for feature in product["features"]
        )

        item = f"""
商品编号：{product['product_id']}
商品名称：{product['name']}
目标市场：{product['market']}
商品卖点：
{features}
"""

        context.append(item)

    return "\n".join(context)


# ==================================
# 第五部分：调用 DeepSeek 回答
# ==================================

def ask_ai(question):

    # 第一步：检索商品
    products = retrieve_products(question)

    if not products:
        return "知识库中没有找到相关商品，请尝试提供更具体的商品名称或卖点。"

    # 第二步：构建上下文
    context = build_context(products)

    print("\n========== 知识库检索结果 ==========")
    print(context)

    # 第三步：组织 AI 消息
    messages = [
        {
            "role": "system",
            "content": """
你是专业的跨境电商商品知识库助手。

回答规则：
1. 必须依据提供的商品知识库回答。
2. 不得编造商品功能、规格和参数。
3. 如果资料没有提供某项信息，明确说明未知。
4. 使用中文回答。
5. 可以介绍商品编号、商品名称和已知卖点。
6. 不要把推测当成真实商品信息。
"""
        },
        {
            "role": "user",
            "content": f"""
商品知识库资料：

{context}

用户问题：
{question}

请根据以上资料回答。
"""
        }
    ]

    # 第四步：调用 DeepSeek
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )

    return response.choices[0].message.content


# ==================================
# 第六部分：程序入口
# ==================================

def main():

    print("==============================")
    print("跨境电商 RAG 商品知识库助手")
    print("==============================")

    print("输入 exit 退出程序")

    while True:

        question = input("\n请输入你的问题：").strip()

        if question.lower() == "exit":
            print("程序已退出")
            break

        if not question:
            print("问题不能为空")
            continue

        try:

            print("\nAI 正在检索知识库并生成回答...")

            answer = ask_ai(question)

            print("\n========== AI 回答 ==========")
            print(answer)

        except Exception as error:

            print("\n程序执行失败：", error)


if __name__ == "__main__":
    main()
