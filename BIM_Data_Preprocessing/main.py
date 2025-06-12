import GraphDataStoring


def main():
    # Connect to the Neo4j database
    try:
        # 初始化连接
        GraphDataStoring.graph_data_storing()
        print("✅ Neo4j 数据存储成功")

        #GraphDataQuery.graph_data_query()

    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    main()