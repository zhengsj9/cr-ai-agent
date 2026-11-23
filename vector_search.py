
import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================
# 第一部分：加载环境配置
# ==========================================

print("正在加载环境配置...")

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL")

if not api_key or not base_url or not model_name:
    raise ValueError("请检查 .env 文件中的 OpenAI 配置！")


# ==========================================
# 第二部分：创建 OpenAI 客户端
# ==========================================

openai_client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60.0,
    max_retries=2
)


# ==========================================
# 第三部分：加载 Embedding 模型
# ==========================================

print("正在加载 Embedding 模型...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ==========================================
# 第四部分：连接 ChromaDB
# ==========================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_collection(
    name="products_semantic"
)

print("数据库商品数量：", collection.count())


# ==========================================
# 第五部分：定义商品分类
# ==========================================

categories = [
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
]


# ==========================================
# 第六部分：AI 自动识别商品分类
# ==========================================

def classify_category(query):

    response = openai_client.chat.completions.create(
        model=model_name,

        messages=[
            {
                "role": "system",

                "content": f"""
你是一个专业的跨境电商商品分类助手。

你的任务是根据用户的商品搜索需求，
判断用户最想寻找的商品属于哪个分类。

只能从以下分类中选择：

{categories}

分类规则：

1. 电子产品归入 Electronics。
2. 运动、露营、户外用品归入 Sports & Outdoors。
3. 宠物用品归入 Pet Supplies。
4. 家居和厨房用品归入 Home & Kitchen。
5. 办公用品归入 Office Supplies。
6. 旅行用品归入 Travel。
7. 花园和园艺用品归入 Garden & Outdoor。
8. 健康及个人护理用品归入 Health & Personal Care。
9. 玩具和手工用品归入 Toys & Crafts。
10. 工具和五金用品归入 Tools & Hardware。
11. 无法判断时归入 Other。

要求：

1. 只能返回一个分类名称。
2. 不要解释。
3. 不要输出其他内容。
4. 不要创造新的分类名称。
"""
            },

            {
                "role": "user",
                "content": query
            }
        ],

        temperature=0
    )

    # 获取 AI 返回的分类
    category = response.choices[0].message.content.strip()

    # 检查分类是否合法
    if category not in categories:

        print("AI 返回了无效分类：", category)

        return "Other"

    return category


# ==========================================
# 第七部分：接收用户搜索需求
# ==========================================

print("\n==============================")
print("AI 商品智能语义搜索系统")
print("==============================")

query = input("\n请输入商品搜索需求：").strip()

if not query:

    print("搜索需求不能为空！")

    exit()


# ==========================================
# 第八部分：AI 自动识别商品分类
# ==========================================

print("\nAI 正在分析用户需求...")

category = classify_category(query)

print("\n========== AI 分类结果 ==========")

print("用户搜索需求：", query)

print("AI 识别的商品分类：", category)


# ==========================================
# 第九部分：生成用户问题的 Embedding
# ==========================================

print("\n正在生成查询向量...")

query_embedding = model.encode(
    query,
    convert_to_numpy=True
).tolist()


# ==========================================
# 第十部分：Metadata 过滤 + 向量检索
# ==========================================

print("\n正在检索商品知识库...")

results = collection.query(

    query_embeddings=[query_embedding],

    n_results=3,

    where={
        "category": category
    }
)


# ==========================================
# 第十一部分：输出商品检索结果
# ==========================================

print("\n========== 商品语义检索结果 ==========")

result_count = len(results["ids"][0])

if result_count == 0:

    print("没有找到符合条件的商品。")

else:

    for i in range(result_count):

        product_id = results["ids"][0][i]

        document = results["documents"][0][i]

        metadata = results["metadatas"][0][i]

        distance = results["distances"][0][i]

        # ChromaDB 使用余弦距离
        # 相似度 = 1 - 距离

        similarity = 1 - distance

        print("\n商品编号：", product_id)

        print(
            "商品名称：",
            metadata.get("name", "未知")
        )

        print(
            "商品分类：",
            metadata.get("category", "未知")
        )

        print("商品文本：", document)

        print("余弦距离：", round(distance, 4))

        print("余弦相似度：", round(similarity, 4))

        print("-" * 50)


print("\n商品检索完成！")
