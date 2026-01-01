(function(){
const tbody = document.querySelector("#runs tbody");
let ws;
function rowHtml(r){
  const badge = r.ok ? "✅ PASS" : "❌ FAIL";
  const bias = (r.bias !== undefined && r.bias !== null) ? (r.bias > 0 ? `+${r.bias.toFixed(2)}` : r.bias.toFixed(2)) : "—";
  return `<tr>
    <td><span class="badge">${r.run_id||"—"}</span></td>
    <td>${r.spec||"—"}</td>
    <td>${badge}</td>
    <td class="spark">${r.spark||bias}</td>
    <td>${r.report ? `<a href="${r.report}" target="_blank">report</a>` : "—"}</td>
  </tr>`;
}
async function poll(){
  try{
    const r = await fetch('/api/spec_runs'); const j = await r.json();
    tbody.innerHTML = (j.runs||[]).map(rowHtml).join('') || `<tr><td colspan="5">No runs yet</td></tr>`;
  }catch(e){/* ignore */}
}
function connectWS(){
  try{
    ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/spec_updates');
    ws.onmessage = (ev)=>{ try{ const j = JSON.parse(ev.data); if(j.type==='spec_run'){ poll(); } }catch(e){} };
    ws.onclose = ()=> setTimeout(connectWS, 1500);
  }catch(e){ setTimeout(connectWS, 1500); }
}
setInterval(poll, 1500); poll(); connectWS();
})();
