import sys
import server
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')
client = TestClient(server.app)

for query in ['brostrom', 'bankart', 'smith-petersen', 'latarjet', 'chevron', 'putti-platt']:
    res = client.get(f'/api/techniques?q={query}')
    data = res.json()
    print(f'Query "{query}": {data["total"]} results')
    for item in data['items'][:2]:
        print(f'   -> [{item["tech_id"]}] {item["name"]} (p.{item["pdf_page"]})')

res = client.get('/api/techniques/89-6')
print('\nDetail 89-6:')
print(res.json()['name'])
print('Extracted preview:', res.json()['extracted_text'][:200])
