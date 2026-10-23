"""Check the frozen public schema and boot configuration before releasing a wheel."""
import json
from pathlib import Path
from quickcart_api.app import create_app
from quickcart_api.config import Settings, load_principals

ROOT = Path(__file__).resolve().parents[1]
app = create_app(Settings(load_principals(ROOT / "fixtures/synthetic-principals.json")))
actual = app.openapi()
baseline = json.loads((ROOT / "delivery/openapi-v1.json").read_text(encoding="utf-8"))
assert actual == baseline, "Public schema changed: review consumers and rollback compatibility before updating baseline"
print("PASS: v1 public schema and synthetic boot configuration")
