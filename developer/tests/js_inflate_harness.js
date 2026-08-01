const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const start=html.indexOf('const BUILD_INFO = ');
const end=html.indexOf('let worker=',start);
if(start<0||end<0)throw new Error('Could not locate packed bundled data in HTML');
let code=html.slice(start,end);
code += '\n;globalThis.__inflated=BUNDLED_MASTER;';
eval(code);
process.stdout.write(JSON.stringify(globalThis.__inflated));
