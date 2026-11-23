
import os
import chromadb

from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer


# ==================================
# 第一部分：加载环境变量
# ==================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

if not api_key or not base_url or not model_name:
    raise ValueError("请检查 .env 中的 API 配置")


# ==================================
# 第二部分：初始化 LLM 客户端
# ==================================

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60.0,
    max_retries=2
)


# ==================================
# 第三部分：加载 Embedding 模型
# ==================================

print("正在加载 Embedding 模型...")

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ==================================
# 第四部分：连接 ChromaDB
# ==================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_collection(
    name="products_semantic"
)

print("知识库商品数量：", collection.count())


# ==================================
# 第五部分：检索相关商品
# ==================================

def retrieve_products(question):

    # 1. 将用户问题转换为向量
    query_embedding = embedding_model.encode(
        question,
        convert_to_numpy=True
    ).tolist()

    # 2. 使用 ChromaDB 检索相关商品
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(3, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    # 3. 整理检索结果
    products = []

    for i in range(len(results["ids"][0])):

        product = {
            "product_id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        }

        products.append(product)

    return products


# ==================================
# 第六部分：构建上下文
# ==================================

def build_context(products):

    context = []

    for product in products:

        metadata = product["metadata"]

        item = f"""
商品编号：{metadata.get("product_id", "未知")}
商品名称：{metadata.get("name", "未知")}
目标市场：{metadata.get("market", "未知")}
商品资料：{product["document"]}
"""

        context.append(item)

    return "\n".join(context)


# ==================================
# 第七部分：调用大语言模型
# ==================================

def ask_ai(question):

    # 第一步：检索知识库
    products = retrieve_products(question)

    if not products:
        return "知识库中没有找到相关商品。"

    # 第二步：构建上下文
    context = build_context(products)

    print("\n========== 检索到的商品资料 ==========")
    print(context)

    # 第三步：构建 Prompt
    messages = [
        {
            "role": "system",
            "content": """
你是一个专业的跨境电商商品知识库助手。

回答规则：
1. 必须依据提供的商品知识库回答。
2. 不得编造商品功能和参数。
3. 如果知识库没有提供相关信息，明确说明未知。
4. 使用中文回答。
5. 优先说明相关商品名称和商品编号。
"""
        },
        {
            "role": "user",
            "content": f"""
以下是从商品知识库检索到的资料：

{context}

用户问题：

{question}

请根据知识库资料回答。
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
# 第八部分：程序入口
# ==================================

def main():

    print("==============================")
    print("AI 商品向量知识库问答系统")
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

            print("\n正在检索知识库并生成回答...")

            answer = ask_ai(question)

            print("\n========== AI 最终回答 ==========")
            print(answer)

        except Exception as error:

            print("\n程序执行失败：", error)


if __name__ == "__main__":
    main()
