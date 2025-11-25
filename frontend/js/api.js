// If running locally (developer machine) use backend on localhost:5000,
// otherwise use relative `/api` so the Docker/Nginx setup keeps working.
const API = (function(){
  try{
    const host = window.location.hostname;
    if(host === 'localhost' || host === '127.0.0.1'){
      return `${window.location.protocol}//${host}:5000/api`;
    }
  }catch(e){}
  return "/api";
})();

async function apiGet(path) {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(`GET ${path} -> ${r.status}`);
  return r.json();
}
async function apiPost(path, body) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const text = await r.text();
  const data = text ? JSON.parse(text) : null;
  if (!r.ok) throw Object.assign(new Error(`POST ${path} -> ${r.status}`), { data });
  return data;
}
