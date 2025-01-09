import requests
import json

def fetch_url_patterns_and_ids(api_url):
    try:
        # APIリクエストを送信
        response = requests.get(api_url)
        response.raise_for_status()

        # JSONレスポンスを解析
        data = response.json()

        # namespace配列内のresourcesを取得
        results = []
        payload = data.get('payload', {}).get('namespaces', [])
        for namespace in payload:
            pattern = namespace.get('pattern', None)
            if 'resources' in namespace:
                for resource in namespace['resources']:
                    if 'urlPattern' in resource and 'id' in resource:
                        results.append({
                            "urlPattern": resource['urlPattern'],
                            "pattern": pattern,
                            "derived_from": [
                                {
                                    "namespece": "idorg",
                                    "id": resource['id']
                                }
                            ]
                        })

        if not results:
            print("データが見つかりませんでした。レスポンス構造を確認してください。")
            return []

        # JSON Line形式で出力
        for result in results:
            print(json.dumps(result, ensure_ascii=False))

        return results

    except requests.exceptions.RequestException as e:
        print(f"HTTPリクエストエラー: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON解析エラー: {e}")
    return []

# メイン処理
if __name__ == "__main__":
    api_url = "https://registry.api.identifiers.org/resolutionApi/getResolverDataset"
    fetch_url_patterns_and_ids(api_url)
