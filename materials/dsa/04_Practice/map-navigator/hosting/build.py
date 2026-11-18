"""Build the web worker using the same graph weights and map assets as Flask."""
import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent


def build():
    # Import the same Python model used by the local REST API.
    sys.path.insert(0, str(ROOT))
    from app import CITIES, ROADS, graph

    def encode(value):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    cities = [{"name": name, "lat": lat, "lng": lng} for name, (lat, lng) in CITIES.items()]
    edges = [[u, v, dict(graph[u])[v]] for u, v in ROADS]
    mime_types = {
        ".html": "text/html; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".png": "image/png",
    }
    assets = {}
    for file in sorted((ROOT / "static").rglob("*")):
        if not file.is_file():
            continue
        binary = file.suffix == ".png"
        content = base64.b64encode(file.read_bytes()).decode("ascii") if binary else file.read_text(encoding="utf-8")
        assets["/" + file.relative_to(ROOT).as_posix()] = [mime_types[file.suffix], content, binary]
    source = (
        "const cities = " + encode(cities) + ";\nconst edges = " + encode(edges) + ";\n"
        + (ROOT / "hosting/routing.mjs").read_text(encoding="utf-8")
        + "\nconst assets = " + encode(assets) + ";\n"
        + (ROOT / "hosting/handler.mjs").read_text(encoding="utf-8")
    )
    output = ROOT / "dist/server/index.js"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(source, encoding="utf-8")
    print(f"Built {output}")


if __name__ == "__main__":
    build()
