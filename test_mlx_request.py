import asyncio

from nexus_sdk.nexus_client.mlx_client import NexusMLXClient


async def main():
    # MLXサーバーのURLを指定
    base_url = "http://127.0.0.1:8080"

    # MLXクライアントを初期化
    client = NexusMLXClient(base_url=base_url)

    # テストメッセージ
    messages = [{"role": "user", "content": "Hello, how are you?"}]

    # モデルを指定（MLXサーバーから取得したモデル）
    payload = {
        "model": "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "messages": messages,
    }

    try:
        # リクエストを送信
        response = await client.invoke(payload)
        print("Response:", response)
    except Exception as e:
        print("Error:", e)
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
