
import chromadb
from sentence_transformers import SentenceTransformer

# 1. 加载与商品建库时相同的 Embedding 模型
print("正在加载 Embedding 模型...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# 2. 连接已经保存的 Chroma 数据库
client = chromadb.PersistentClient(
    path="./chroma_db"
)

# 3. 获取已经存在的商品集合
collection = client.get_collection(
    name="products_semantic"
)

print("数据库商品数量：", collection.count())

# 4. 接收用户搜索需求
# 1. 接收商品分类
print("\n请选择商品分类：")
print("1. Pet Supplies")
print("2. Electronics")
print("3. Sports & Outdoors")
print("4. Home & Kitchen")
print("5. Office Supplies")
print("6. Travel")

category_options = {
    "1": "Pet Supplies",
    "2": "Electronics",
    "3": "Sports & Outdoors",
    "4": "Home & Kitchen",
    "5": "Office Supplies",
    "6": "Travel"
}

choice = input("请输入分类编号：")

category = category_options.get(choice)

if category is None:
    print("分类选择无效！")
    exit()

# 2. 接收用户搜索需求
query = input("请输入商品搜索需求：")

# 3. 生成查询向量
query_embedding = model.encode(
    query,
    convert_to_numpy=True
).tolist()

# 4. 根据用户选择的分类进行向量检索
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    where={
        "category": category
    }
)

# 5. 将用户问题转换成 384 维向量
query_embedding = model.encode(
    query,
    convert_to_numpy=True
).tolist()

# 6. 使用 Chroma 进行向量相似度检索

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    where={
       "category": category
    }
)


# 7. 输出检索结果
print("\n========== 商品语义检索结果 ==========")

for i in range(len(results["ids"][0])):

    product_id = results["ids"][0][i]
    document = results["documents"][0][i]
    metadata = results["metadatas"][0][i]
    distance = results["distances"][0][i]

    # Chroma 使用余弦距离，距离越小表示越相似
    similarity = 1 - distance

    print("\n商品编号：", product_id)
    print("商品名称：", metadata.get("name", "未知"))
    print("商品文本：", document)
    print("余弦距离：", round(distance, 4))
    print("余弦相似度：", round(similarity, 4))
    print("-" * 50)
