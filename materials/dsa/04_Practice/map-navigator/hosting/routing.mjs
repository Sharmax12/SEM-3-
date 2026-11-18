const graph = new Map(cities.map(city => [city.name, []]));
const locations = new Map(cities.map(city => [city.name, [city.lat, city.lng]]));
for (const [from, to, weight] of edges) {
  graph.get(from).push([to, weight]);
  graph.get(to).push([from, weight]);
}
const roads = edges.map(([from, to]) => ({
  from, to, from_coords: locations.get(from), to_coords: locations.get(to)
}));

function haversine(first, second) {
  const radians = Math.PI / 180;
  const [lat1, lon1] = locations.get(first).map(n => n * radians);
  const [lat2, lon2] = locations.get(second).map(n => n * radians);
  const value = Math.sin((lat2 - lat1) / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin((lon2 - lon1) / 2) ** 2;
  return 12742 * Math.asin(Math.sqrt(value));
}

// Tie-break equal priorities by city name, like the Python heapq tuples.
function before(a, b) {
  return a.priority < b.priority || (a.priority === b.priority && a.city < b.city);
}
class MinHeap {
  constructor() { this.items = []; }
  push(entry) {
    const items = this.items;
    let i = items.length;
    items.push(entry);
    while (i > 0) {
      const parent = Math.floor((i - 1) / 2);
      if (!before(entry, items[parent])) break;
      items[i] = items[parent];
      i = parent;
    }
    items[i] = entry;
  }
  pop() {
    const items = this.items;
    const first = items[0];
    const tail = items.pop();
    if (items.length > 0) {
      let i = 0;
      while (2 * i + 1 < items.length) {
        let child = 2 * i + 1;
        if (child + 1 < items.length && before(items[child + 1], items[child])) child++;
        if (!before(items[child], tail)) break;
        items[i] = items[child];
        i = child;
      }
      items[i] = tail;
    }
    return first;
  }
}

function findRoute(source, destination, algorithm) {
  const estimate = city => algorithm === 'astar' ? haversine(city, destination) : 0;
  const pending = new MinHeap();
  const previous = new Map();
  const closed = new Set();
  const costs = new Map([[source, 0]]);
  pending.push({city: source, priority: estimate(source)});
  while (pending.items.length) {
    const {city} = pending.pop();
    if (closed.has(city)) continue;
    closed.add(city);
    if (city === destination) {
      const path = [city];
      while (path[path.length - 1] !== source) path.push(previous.get(path[path.length - 1]));
      path.reverse();
      const distance = Math.round(costs.get(city) * 10) / 10;
      const totalMinutes = Math.trunc(distance);
      return {
        path, distance_km: distance, algorithm, nodes_visited: closed.size,
        coords: path.map(name => locations.get(name)),
        estimated_time: Math.floor(totalMinutes / 60) + ' hr ' + totalMinutes % 60 + ' min'
      };
    }
    for (const [next, weight] of graph.get(city)) {
      const cost = costs.get(city) + weight;
      if (cost < (costs.get(next) ?? Infinity)) {
        costs.set(next, cost);
        previous.set(next, city);
        pending.push({city: next, priority: cost + estimate(next)});
      }
    }
  }
  return null;
}

function apiResponse(url) {
  if (url.pathname === '/api/health') return Response.json({status: 'ok'});
  if (url.pathname === '/api/cities') return Response.json(cities);
  if (url.pathname === '/api/roads') return Response.json(roads);
  if (url.pathname !== '/api/route') return Response.json({error:'Not found'}, {status:404});
  const source = url.searchParams.get('source');
  const destination = url.searchParams.get('destination');
  const algorithm = (url.searchParams.get('algo') ?? 'dijkstra').toLowerCase();
  let error;
  if (!graph.has(source) || !graph.has(destination)) error = 'Invalid source or destination city';
  else if (source === destination) error = 'Source and destination same hain';
  else if (!['dijkstra', 'astar'].includes(algorithm)) error = "algo must be 'dijkstra' or 'astar'";
  if (error) return Response.json({error}, {status:400});
  const route = findRoute(source, destination, algorithm);
  return route ? Response.json(route) : Response.json({error:'Koi route nahi mila'}, {status:404});
}
