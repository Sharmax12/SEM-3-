# Map Navigator

Find the shortest route between 20 Indian cities using Dijkstra or A*. This Semester III DSA project models 30 two-way roads. Each road weight is 1.25 times the Haversine distance, rounded to the nearest 0.1 km. Travel time assumes an average speed of 60 km/h.

[Open the live demo](https://nsut-map-navigator.aniruddhsharma432.chatgpt.site)

## Run the Flask project

With Python 3.10 or newer, run these commands from this directory.

```console
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**. Select a source, destination and algorithm, then click **Find Shortest Route**. The map, city network and results work with local assets. Detailed OpenStreetMap tiles load when internet access is available.

## Try it

| Scenario | Distance | Dijkstra visits | A* visits |
| --- | ---: | ---: | ---: |
| Delhi → Kanpur | 528.0 km | 7 | 3 |
| Delhi → Chennai | 2,309.3 km | 20 | 13 |

For Delhi → Chennai, both algorithms return Delhi → Agra → Bhopal → Nagpur → Hyderabad → Chennai.

## Source and API

The Python algorithms and Flask routes are in `app.py`. The interface is in `static/index.html`. The live deployment uses a JavaScript Worker implementing the same four endpoints. Both implementations agreed on the path, distance, estimated time and nodes visited for all 380 ordered pairs of distinct cities under both algorithms.

| Endpoint | Output |
| --- | --- |
| `/api/health` | Server status |
| `/api/cities` | City names and coordinates |
| `/api/roads` | Graph edges with endpoint coordinates |
| `/api/route?source=Delhi&destination=Chennai&algo=astar` | Shortest path, distance, ETA, coordinates and visit count |

After installing the Python requirements, run `python hosting/build.py` to reproduce the deployed Worker module at `dist/server/index.js`. Map rendering uses Leaflet, the offline land outline uses Natural Earth public-domain data, and online tiles use OpenStreetMap. The Leaflet license is included under `static/leaflet/`.
