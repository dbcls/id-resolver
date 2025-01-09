import requests
import json

def fetch_and_merge_data(idorg_api_url, togoid_api_url, bioregistry_api_url):
    try:
        # ID.org APIリクエストを送信
        idorg_response = requests.get(idorg_api_url)
        idorg_response.raise_for_status()
        idorg_data = idorg_response.json()

        # TogoID APIリクエストを送信
        togoid_response = requests.get(togoid_api_url)
        togoid_response.raise_for_status()
        togoid_data = togoid_response.json()

        # Bioregistry APIリクエストを送信
        bioregistry_response = requests.get(bioregistry_api_url)
        bioregistry_response.raise_for_status()
        bioregistry_data = bioregistry_response.json()

        # ID.orgデータを処理
        idorg_results = []
        idorg_payload = idorg_data.get('payload', {}).get('namespaces', [])
        for namespace in idorg_payload:
            pattern = namespace.get('pattern', None)
            if 'resources' in namespace:
                for resource in namespace['resources']:
                    if 'urlPattern' in resource and 'id' in resource:
                        idorg_results.append({
                            "urlPattern": resource['urlPattern'],
                            "pattern": pattern,
                            "derived_from": [
                                {
                                    "namespece": "idorg",
                                    "id": resource['id']
                                }
                            ]
                        })

        # TogoIDデータを処理
        togoid_results = []
        for key, value in togoid_data.items():
            url_pattern = value.get('prefix', None)
            pattern = value.get('regex', None)
            if url_pattern and pattern:
                # urlPatternに"{$id}"を追記
                url_pattern_with_id = f"{url_pattern}{{$id}}"
                togoid_results.append({
                    "urlPattern": url_pattern_with_id,
                    "pattern": pattern,
                    "derived_from": [
                        {
                            "namespece": "togoid",
                            "id": key
                        }
                    ]
                })

        # Bioregistryデータを処理
        bioregistry_results = []
        for prefix, value in bioregistry_data.items():
            url_pattern = value.get('uri_format', None)
            pattern = value.get('pattern', None)
            if url_pattern and pattern:
                bioregistry_results.append({
                    "urlPattern": url_pattern,
                    "pattern": pattern,
                    "derived_from": [
                        {
                            "namespece": "bioregistry",
                            "id": prefix
                        }
                    ]
                })

        # データのマージ
        merged_results = []
        all_results = idorg_results + togoid_results + bioregistry_results
        for entry in all_results:
            matching_entry = next((result for result in merged_results if result['urlPattern'] == entry['urlPattern']), None)
            if matching_entry:
                matching_entry['derived_from'].extend(entry['derived_from'])
            else:
                merged_results.append(entry)

        # JSON Line形式で出力
        for result in merged_results:
            print(json.dumps(result, ensure_ascii=False))

        return merged_results

    except requests.exceptions.RequestException as e:
        print(f"HTTPリクエストエラー: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON解析エラー: {e}")
    return []

# メイン処理
if __name__ == "__main__":
    idorg_api_url = "https://registry.api.identifiers.org/resolutionApi/getResolverDataset"
    togoid_api_url = "https://api.togoid.dbcls.jp/config/dataset"
    bioregistry_api_url = "https://bioregistry.io/api/registry"
    fetch_and_merge_data(idorg_api_url, togoid_api_url, bioregistry_api_url)
