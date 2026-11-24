
import asyncio
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


# 1. 获取 Server 文件路径
server_file = Path(__file__).with_name(
    "mcp_server.py"
)


# 2. 配置 Server 子进程
server_params = StdioServerParameters(
    command=sys.executable,
    args=[
        str(server_file)
    ]
)


# 3. 创建异步主函数
async def main():

    print("正在连接 MCP Server...")

    # 4. 建立 MCP 连接
    async with Client(server_params) as client:

        print("MCP Server 连接成功！")

        # 5. 获取工具列表
        tools_result = await client.list_tools()

        print("\n========== MCP 工具列表 ==========")

        for tool in tools_result.tools:

            print("工具名称：", tool.name)

            print("工具描述：", tool.description)

            print("参数结构：", tool.input_schema)

            print("-" * 40)
                    # =================================
        # 调用商品搜索工具
        # =================================

        print("\n========== 商品搜索测试 ==========")

        search_result = await client.call_tool(
            "search_product",
            {
                "keyword": "wireless"
            }
        )

        print("搜索结果：")

        for content in search_result.content:

            if hasattr(content, "text"):

                print(content.text)

        print("是否发生错误：", search_result.is_error)

        # =================================
        # 调用商品详情工具
        # =================================

        print("\n========== 商品详情测试 ==========")

        product_result = await client.call_tool(
            "get_product",
            {
                "product_id": "P001"
            }
        )

        print("商品详情：")

        for content in product_result.content:

            if hasattr(content, "text"):

                print(content.text)

        print("是否发生错误：", product_result.is_error)

        # =================================
        # 读取 MCP Resource
        # =================================

        print("\n========== 商品目录 Resource 测试 ==========")

        resource_result = await client.read_resource(
            "products://catalog"
        )

        print("商品目录内容：")

        for content in resource_result.contents:

            if hasattr(content, "text"):

                print(content.text)

        print("\nResource 读取完成！")

# 6. 程序入口
if __name__ == "__main__":
    asyncio.run(main())
