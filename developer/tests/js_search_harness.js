const fs=require('fs'),vm=require('vm');
const workerPath=process.argv[2],cardsPath=process.argv[3],params=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
let src=fs.readFileSync(workerPath,'utf8');const cards=JSON.parse(fs.readFileSync(cardsPath,'utf8'));src=src.replace('__CARDS__',JSON.stringify(cards));
let out=null;const context={console,performance:{now:()=>Date.now()},self:{postMessage:m=>{if(m.type==='done'||m.type==='error')out=m;}},structuredClone:global.structuredClone};vm.createContext(context);vm.runInContext(src,context,{timeout:1200000});const t=Date.now();context.self.onmessage({data:params});
process.stdout.write(JSON.stringify({elapsedMs:Date.now()-t,...out}));
