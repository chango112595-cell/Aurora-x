// tools/aurora-cli.js
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const ROOT = process.cwd();
const STATE = path.join(ROOT, '.aurora');
const PIDS = path.join(STATE, 'pids');
const LOGS = path.join(STATE, 'logs');
if (!fs.existsSync(STATE)) fs.mkdirSync(STATE,{recursive:true});
if (!fs.existsSync(PIDS)) fs.mkdirSync(PIDS,{recursive:true});
if (!fs.existsSync(LOGS)) fs.mkdirSync(LOGS,{recursive:true});
function write(pidFile, pid){ fs.writeFileSync(pidFile, String(pid)); }
function read(pidFile){ try { return Number(fs.readFileSync(pidFile,'utf8')); } catch(e){ return null; } }
function remove(pidFile){ try{ fs.unlinkSync(pidFile);}catch(e){} }

const APPS = [
  { name:'aurora-core', cmd:'python3', args:['tools/aurora_core.py'] },
  { name:'aurora-nexus3', cmd:'python3', args:['aurora_nexus_v3/main.py'] },
  { name:'aurora-nexus2', cmd:'python3', args:['tools/luminar_nexus_v2.py','serve'] },
  { name:'aurora-express', cmd:'npx', args:['tsx','server/index.ts'] }
];

function spawnApp(a){
  const out = fs.openSync(path.join(LOGS,`${a.name}.out.log`),'a');
  const err = fs.openSync(path.join(LOGS,`${a.name}.err.log`),'a');
  const child = spawn(a.cmd, a.args, { cwd:ROOT, stdio:['ignore',out,err], detached:true });
  write(path.join(PIDS, `${a.name}.pid`), child.pid);
  console.log(`started ${a.name} pid=${child.pid}`);
  child.unref();
}

function killPid(pid){
  try {
    if (process.platform==='win32') spawn('taskkill',['/PID',String(pid),'/F','/T']);
    else process.kill(pid,'SIGTERM');
  } catch(e){ try{ process.kill(pid,'SIGKILL'); }catch(e){} }
}

async function startNative(){
  for(const a of APPS){
    const pid = read(path.join(PIDS,`${a.name}.pid`));
    if(pid){ console.log(`skip ${a.name}, pidFile present ${pid}`); continue; }
    spawnApp(a);
    await new Promise(r=>setTimeout(r,400));
  }
}

async function stopNative(){
  for(let i=APPS.length-1;i>=0;i--){
    const a=APPS[i];
    const pid = read(path.join(PIDS,`${a.name}.pid`));
    if(pid){
      console.log(`stopping ${a.name} pid ${pid}`);
      killPid(pid);
      remove(path.join(PIDS,`${a.name}.pid`));
    } else console.log(`no pid for ${a.name}`);
  }
}

async function hasPM2(){
  try{ require.resolve('pm2'); return true; } catch(e){ return false; }
}

async function startPM2(){
  const pm2 = require('pm2');
  return new Promise((res,rej)=>{
    pm2.connect(err=>{
      if(err) return rej(err);
      const apps = APPS.map(a=>({
        name:a.name, script:a.cmd, args:a.args.join(' '), cwd:ROOT,
        out_file:path.join(LOGS,`${a.name}.out.log`),
        error_file:path.join(LOGS,`${a.name}.err.log`),
        autorestart:true
      }));
      pm2.start(apps,(e)=>{ pm2.disconnect(); if(e) return rej(e); res(); });
    });
  });
}

async function stopPM2(){
  const pm2 = require('pm2');
  return new Promise((res,rej)=>{
    pm2.connect(err=>{
      if(err) return rej(err);
      const names = APPS.map(a=>a.name);
      pm2.delete(names,(e)=>{ pm2.disconnect(); res(); });
    });
  });
}

async function main(){
  const cmd = (process.argv[2]||'help').toLowerCase();
  const pm2ok = await hasPM2();
  if(cmd==='start'){
    if(pm2ok){ try{ await startPM2(); console.log('started via pm2'); return; }catch(e){ console.warn('pm2 failed',e); } }
    await startNative();
  } else if(cmd==='stop'){
    if(pm2ok){ try{ await stopPM2(); return;}catch(e){ console.warn('pm2 stop failed'); } }
    await stopNative();
  } else if(cmd==='status'){
    console.log('PID files in',PIDS); const files = fs.readdirSync(PIDS);
    files.forEach(f=>console.log(f, fs.readFileSync(path.join(PIDS,f),'utf8')));
  } else {
    console.log('usage: node aurora-cli.js <start|stop|status>');
  }
}

main().catch(console.error);
