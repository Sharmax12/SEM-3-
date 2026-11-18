"""
Map Navigator - DSA Minor Project
Graph + Dijkstra + A* search, exposed as a REST API using Flask.
"""
import os
import heapq
import math
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

# ---------------------------------------------------------------
# 1. DATA: cities (nodes) with latitude / longitude
# ---------------------------------------------------------------
CITIES = {
    "Delhi": (28.6139, 77.2090),
    "Chandigarh": (30.7333, 76.7794),
    "Amritsar": (31.6340, 74.8723),
    "Jaipur": (26.9124, 75.7873),
    "Agra": (27.1767, 78.0081),
    "Lucknow": (26.8467, 80.9462),
    "Kanpur": (26.4499, 80.3319),
    "Varanasi": (25.3176, 82.9739),
    "Patna": (25.5941, 85.1376),
    "Kolkata": (22.5726, 88.3639),
    "Udaipur": (24.5854, 73.7125),
    "Ahmedabad": (23.0225, 72.5714),
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Indore": (22.7196, 75.8577),
    "Bhopal": (23.2599, 77.4126),
    "Nagpur": (21.1458, 79.0882),
    "Hyderabad": (17.3850, 78.4867),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
}

# ---------------------------------------------------------------
# 2. DATA: roads (edges) between cities (undirected)
# ---------------------------------------------------------------
ROADS = [
    ("Delhi", "Chandigarh"), ("Delhi", "Jaipur"), ("Delhi", "Agra"),
    ("Chandigarh", "Amritsar"), ("Delhi", "Amritsar"),
    ("Agra", "Jaipur"), ("Agra", "Kanpur"), ("Agra", "Bhopal"),
    ("Kanpur", "Lucknow"), ("Lucknow", "Varanasi"), ("Varanasi", "Patna"),
    ("Patna", "Kolkata"), ("Varanasi", "Kolkata"),
    ("Jaipur", "Udaipur"), ("Jaipur", "Indore"), ("Udaipur", "Ahmedabad"),
    ("Ahmedabad", "Mumbai"), ("Ahmedabad", "Indore"),
    ("Mumbai", "Pune"), ("Indore", "Bhopal"), ("Indore", "Mumbai"),
    ("Bhopal", "Nagpur"), ("Nagpur", "Hyderabad"), ("Pune", "Hyderabad"),
    ("Hyderabad", "Bengaluru"), ("Bengaluru", "Chennai"),
    ("Pune", "Bengaluru"), ("Hyderabad", "Chennai"), ("Nagpur", "Kolkata"),
    ("Lucknow", "Delhi"),
]

ROAD_FACTOR = 1.25   # straight-line distance ko road distance me approx convert karne ke liye


def haversine(a, b):
    """Do (lat, lng) points ke beech straight-line distance in km."""
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


# ---------------------------------------------------------------
# 3. GRAPH: adjacency list
# ---------------------------------------------------------------
graph = {city: [] for city in CITIES}
for u, v in ROADS:
    w = round(haversine(CITIES[u], CITIES[v]) * ROAD_FACTOR, 1)
    graph[u].append((v, w))
    graph[v].append((u, w))


# ---------------------------------------------------------------
# 4. ALGORITHMS
# ---------------------------------------------------------------
def dijkstra(src, dst):
    """Priority queue (min-heap) based Dijkstra. Returns (path, distance, nodes_visited)."""
    dist = {c: math.inf for c in graph}
    prev = {}
    dist[src] = 0
    pq = [(0, src)]
    visited = 0
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        visited += 1
        if u == dst:
            break
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return build_path(prev, src, dst, dist[dst]), visited


def a_star(src, dst):
    """A* search with haversine heuristic (admissible since ROAD_FACTOR >= 1)."""
    g = {c: math.inf for c in graph}
    prev = {}
    g[src] = 0
    pq = [(haversine(CITIES[src], CITIES[dst]), src)]
    visited = 0
    closed = set()
    while pq:
        _, u = heapq.heappop(pq)
        if u in closed:
            continue
        closed.add(u)
        visited += 1
        if u == dst:
            break
        for v, w in graph[u]:
            ng = g[u] + w
            if ng < g[v]:
                g[v] = ng
                prev[v] = u
                f = ng + haversine(CITIES[v], CITIES[dst])
                heapq.heappush(pq, (f, v))
    return build_path(prev, src, dst, g[dst]), visited


def build_path(prev, src, dst, total):
    if total == math.inf:
        return None
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    path.reverse()
    return {"path": path, "distance_km": round(total, 1)}


# ---------------------------------------------------------------
# 5. REST API
# ---------------------------------------------------------------
@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/api/cities")
def api_cities():
    return jsonify([{"name": n, "lat": c[0], "lng": c[1]} for n, c in CITIES.items()])


@app.route("/api/roads")
def api_roads():
    out = []
    for u, v in ROADS:
        out.append({"from": u, "to": v, "from_coords": CITIES[u], "to_coords": CITIES[v]})
    return jsonify(out)


@app.route("/api/route")
def api_route():
    src = request.args.get("source")
    dst = request.args.get("destination")
    algo = request.args.get("algo", "dijkstra").lower()

    if src not in CITIES or dst not in CITIES:
        return jsonify({"error": "Invalid source or destination city"}), 400
    if src == dst:
        return jsonify({"error": "Source and destination same hain"}), 400
    if algo not in ("dijkstra", "astar"):
        return jsonify({"error": "algo must be 'dijkstra' or 'astar'"}), 400

    result, visited = dijkstra(src, dst) if algo == "dijkstra" else a_star(src, dst)
    if result is None:
        return jsonify({"error": "Koi route nahi mila"}), 404

    result["algorithm"] = algo
    result["nodes_visited"] = visited
    result["coords"] = [CITIES[c] for c in result["path"]]
    # simple avg speed 60 km/h => estimated time
    hours, minutes = divmod(int(result["distance_km"]), 60)
    result["estimated_time"] = f"{hours} hr {minutes} min"
    return jsonify(result)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
