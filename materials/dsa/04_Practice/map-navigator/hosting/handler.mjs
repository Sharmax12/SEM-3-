export default {
  async fetch(request) {
    if (request.method !== 'GET' && request.method !== 'HEAD')
      return new Response('Method not allowed', {status:405, headers:{Allow:'GET, HEAD'}});
    const url = new URL(request.url);
    let response;
    if (url.pathname.startsWith('/api/')) {
      response = apiResponse(url);
    } else {
      const key = url.pathname === '/' ? '/static/index.html' : url.pathname;
      const file = Object.hasOwn(assets, key) ? assets[key] : null;
      if (!file) return new Response('Not found', {status:404});
      const [mime, content, base64] = file;
      const data = base64 ? Uint8Array.from(atob(content), c => c.charCodeAt(0)) : content;
      response = new Response(data, {headers:{'Content-Type':mime}});
    }
    return request.method === 'HEAD' ? new Response(null, response) : response;
  }
};
