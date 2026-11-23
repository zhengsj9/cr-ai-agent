
import chromadb

# 1. 重新连接之前创建的本地数据库
client = chromadb.PersistentClient(path="./chroma_db")

# 2. 获取已经存在的商品集合
collection = client.get_collection(
    name="products"
)

# 3. 查询商品数量
print("数据库商品数量：", collection.count())

# 4. 只读取数据，不执行写入
result = collection.get(
    ids=["P001"],
    include=["embeddings"]
)

# 5. 输出查询结果
print("商品 ID：", result["ids"])
print("商品文本：", result["documents"])
print("商品向量：", result["embeddings"])
print("向量前5个数值：", result["embeddings"][0][:5])
