
import csv
import chromadb
from sentence_transformers import SentenceTransformer

# 1. 加载 Embedding 模型
print("正在加载 Embedding 模型...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# 2. 读取商品 CSV 文件
products = []

with open("products.csv", "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        products.append(row)

print("读取商品数量：", len(products))

# 3. 将每个商品转换成可检索文本
product_texts = []

for product in products:
    text = " ".join(
        str(value)
        for value in product.values()
        if value
    )
    product_texts.append(text)

# 4. 生成商品向量
print("正在生成商品 Embedding...")

product_embeddings = model.encode(
    product_texts,
    convert_to_numpy=True
).tolist()

print("向量维度：", len(product_embeddings[0]))

# 5. 提取商品 ID
product_ids = [
    product["product_id"]
    for product in products
]

# 6. 整理商品 Metadata
metadatas = []

for product in products:
    metadata = {
        key: value
        for key, value in product.items()
        if value and value.strip()
    }
    metadatas.append(metadata)

# 7. 创建 Chroma 持久化客户端
client = chromadb.PersistentClient(
    path="./chroma_db"
)

# 8. 创建新的商品语义集合
collection = client.get_or_create_collection(
    name="products_semantic",
    metadata={"hnsw:space": "cosine"}
)

# 9. 将商品数据写入 Chroma
collection.upsert(
    ids=product_ids,
    documents=product_texts,
    embeddings=product_embeddings,
    metadatas=metadatas
)

# 10. 验证保存结果
print("\n========== 向量数据库保存结果 ==========")

print("商品数量：", collection.count())

print("集合名称：", collection.name)

print("第一条商品 ID：", product_ids[0])

print("第一条商品向量维度：", len(product_embeddings[0]))

print("第一条商品文本：", product_texts[0])

print("\n商品向量保存成功！")
