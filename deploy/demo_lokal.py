"""API demo potret lokal; tidak memakai atau mengubah database produksi."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ['DATABASE_URL'] = ''  # Mendahului load_dotenv; potret bertanggal.
sys.path.insert(0, str(ROOT / 'backend'))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.main:app', host='127.0.0.1', port=8012)
