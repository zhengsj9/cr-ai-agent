
import chromadb

from sentence_transformers import SentenceTransformer

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings


# ==========================================
# 1. 创建 Sentence Transformers 适配器
# ==========================================

class LocalEmbeddings(Embeddings):

    def __init__(self):

        print("正在加载 Embedding 模型...")

        self.model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    # 将多条文本转换成向量
    def embed_documents(self, texts):

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        )

        return embeddings.tolist()

    # 将用户查询转换成向量
    def embed_query(self, text):

        embedding = self.model.encode(
            text,
            convert_to_numpy=True
        )

        return embedding.tolist()


# ==========================================
# 2. 创建 Embedding 实例
# ==========================================

embedding_function = LocalEmbeddings()


# ==========================================
# 3. 连接原来的 ChromaDB
# ==========================================

print("\n正在连接 ChromaDB...")

vector_store = Chroma(

    collection_name="products_semantic",

    embedding_function=embedding_function,

    persist_directory="./chroma_db"

)

print("ChromaDB 连接成功！")


# ==========================================
# 4. 创建 LangChain Retriever
# ==========================================

retriever = vector_store.as_retriever(

    search_type="similarity",

    search_kwargs={
        "k": 3
    }

)

print("\nRetriever 创建成功！")


# ==========================================
# 5. 接收用户搜索需求
# ==========================================

print("\n==============================")
print("LangChain 商品 Retriever 检索系统")
print("==============================")

query = input("\n请输入商品搜索需求：").strip()

if not query:

    raise ValueError("搜索需求不能为空")


# ==========================================
# 6. 使用 Retriever 检索商品
# ==========================================

print("\n正在使用 Retriever 检索商品...")

documents = retriever.invoke(query)


# ==========================================
# 7. 输出检索结果
# ==========================================

print("\n========== Retriever 检索结果 ==========")

if not documents:

    print("没有找到相关商品。")

else:

    for index, document in enumerate(documents, start=1):

        print(f"\n第 {index} 条商品")

        print("商品文本：")
        print(document.page_content)

        print("\n商品 Metadata：")
        print(document.metadata)

        print("-" * 50)


# ==========================================
# 8. 输出结果统计
# ==========================================

print("\n========== 检索统计 ==========")

print("用户搜索需求：", query)

print("检索结果数量：", len(documents))

print("Retriever 检索完成！")
