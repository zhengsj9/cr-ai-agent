
import os
import requests
from dotenv import load_dotenv

# 1. 加载 .env 文件
load_dotenv()

# 2. 读取 Shopify 配置
shop = os.getenv("SHOPIFY_SHOP")
client_id = os.getenv("SHOPIFY_CLIENT_ID")
client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")

# 3. 检查配置是否完整
if not all([shop, client_id, client_secret]):
    raise ValueError("Shopify 配置不完整，请检查 .env 文件")

# 4. 构建获取 Token 的地址
url = f"https://{shop}.myshopify.com/admin/oauth/access_token"

# 5. 向 Shopify 申请 Access Token
response = requests.post(
    url,
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    },
    timeout=30
)

# 6. 检查 HTTP 请求是否成功
response.raise_for_status()

# 7. 解析 Shopify 返回的 JSON
token_data = response.json()

access_token = token_data["access_token"]

# 8. 显示结果，但不打印真实 Token
print("========== Shopify Token 测试 ==========")
print("Access Token 获取成功！")
print("授权权限：", token_data.get("scope"))
print("有效时间：", token_data.get("expires_in"), "秒")
print("Token 已安全获取，没有输出密钥。")
