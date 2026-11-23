
import csv
from sentence_transformers import SentenceTransformer, util

# 1. 加载 Embedding 模型
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2. 读取商品 CSV 文件
products = []

with open("products.csv", "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        products.append(row)

# 3. 将每个商品转换成可检索文本
product_texts = []

for product in products:
    text = " ".join(str(value) for value in product.values() if value)
    product_texts.append(text)

# 4. 将商品文本转换成向量
product_embeddings = model.encode(product_texts, convert_to_tensor=True)

# 5. 接收用户搜索问题
query = input("请输入商品搜索需求：")

# 6. 将用户问题转换成向量
query_embedding = model.encode(query, convert_to_tensor=True)

# 7. 计算用户问题与商品的语义相似度
scores = util.cos_sim(query_embedding, product_embeddings)[0]

# 8. 按相似度从高到低排序
ranked_indices = scores.argsort(descending=True)

# 9. 输出搜索结果
print("\n商品语义搜索结果：")

for index in ranked_indices:
    i = index.item()
    print(f"商品：{product_texts[i]}")
    print(f"相似度：{scores[i].item():.4f}")
    print("-" * 40)
