import { spawn } from 'node:child_process';
import { existsSync, copyFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const backend = join(root, 'backend');
const frontend = join(root, 'frontend');
const uvLocal = join(homedir(), '.local', 'bin', process.platform === 'win32' ? 'uv.exe' : 'uv');
const uv = existsSync(uvLocal) ? uvLocal : 'uv';
const env = { ...process.env, PATH: dirname(process.execPath) + (process.platform === 'win32' ? ';' : ':') + process.env.PATH };
const children = new Set();
let stopping = false;

function launch(executable, args, cwd) {
  const child = spawn(executable, args, {cwd,env,stdio:'inherit',windowsHide:true,shell:false});
  children.add(child);
  child.once('exit',()=>children.delete(child));
  return child;
}
function run(executable,args,cwd){
  return new Promise((resolve,reject)=>{
    const child=launch(executable,args,cwd);
    child.once('error',reject);
    child.once('exit',code=>code===0?resolve():reject(new Error(`Falló ${args.slice(0,2).join(' ')} (código ${code}).`)));
  });
}
function cleanup(){
  if(stopping)return;stopping=true;
  for(const child of children){if(child.exitCode===null)child.kill();}
}
process.once('SIGINT',()=>{cleanup();process.exitCode=0;});
process.once('SIGTERM',()=>{cleanup();process.exitCode=0;});
process.once('exit',cleanup);
async function health(){
  try{return (await (await fetch('http://127.0.0.1:8000/api/health',{signal:AbortSignal.timeout(2000)})).json()).database==='sqlserver';}catch{return false;}
}

try{
  await run(uv,['sync','--python','3.13'],backend);
  const envPath=join(backend,'.env');
  if(!existsSync(envPath))copyFileSync(join(backend,'.env.example'),envPath);
  await run(uv,['run','huellitas-sqlserver'],backend);
  if(!await health()){
    const python=process.platform==='win32'?join(backend,'.venv','Scripts','python.exe'):join(backend,'.venv','bin','python');
    const api=launch(python,['-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000'],backend);
    api.once('error',error=>{console.error(error.message);cleanup();process.exitCode=1;});
    let ready=false;
    for(let attempt=0;attempt<40;attempt++){
      if(stopping||api.exitCode!==null)throw new Error('La API no pudo iniciar.');
      if(await health()){ready=true;break;}
      await new Promise(resolve=>setTimeout(resolve,500));
    }
    if(!ready)throw new Error('La API no respondió a tiempo.');
  }
  if(!existsSync(join(frontend,'node_modules','bootstrap','dist','css','bootstrap.min.css'))){
    const npm=join(dirname(process.execPath),'node_modules','npm','bin','npm-cli.js');
    if(!existsSync(npm))throw new Error('Ejecuta npm ci desde frontend antes de iniciar.');
    await run(process.execPath,[npm,'ci','--no-audit','--no-fund'],frontend);
  }
  console.log('\nHuellitas: http://127.0.0.1:4200/\nAPI: http://127.0.0.1:8000/docs\nCtrl+C detiene la web y la API iniciadas aquí. SQL Server conserva los datos.\n');
  await run(process.execPath,['node_modules/@angular/cli/bin/ng.js','serve','--host','127.0.0.1','--port','4200'],frontend);
}catch(error){
  if(!stopping){console.error(error.message);process.exitCode=1;}
}finally{cleanup();}
