import json
from pathlib import Path
cases = json.loads(Path('data/help_requests/historical_data.json').read_text())
texts = [(c.get('subject','') + ' ' + c.get('description','')).strip() for c in cases]
print(f'Total: {len(texts)}')
for i, t in enumerate(texts[:5]):
    print(f'[{i}] len={len(t)} {repr(t[:100])}')
