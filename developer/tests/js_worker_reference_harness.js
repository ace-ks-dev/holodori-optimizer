const fs=require('fs');
const workerPath=process.argv[2], cardsPath=process.argv[3], casesPath=process.argv[4];
const cards=JSON.parse(fs.readFileSync(cardsPath,'utf8'));
const cases=JSON.parse(fs.readFileSync(casesPath,'utf8'));
globalThis.self={postMessage(){}};
let src=fs.readFileSync(workerPath,'utf8').replace('__CARDS__',JSON.stringify(cards));
src += `\n;globalThis.__qcOut=(function(){const out=[];for(const q of ${JSON.stringify(cases)}){const ids=q.cardIds.map(cid=>CARDS.findIndex(c=>c.id===cid));if(ids.some(i=>i<0))throw new Error('Unknown card in QC case');buildMasks(q.song);calcCounts(ids,COUNTS);const counts=new Int32Array(COUNTS);const params={song:q.song,specialMode:q.specialMode,other:q.other,outfitMode:'fixed',outfitKey:q.outfitId,ownedOutfitIds:OUTFIT_UNIQUE_IDS};const r=evaluateOrder(ids,counts,params,true,false);out.push(r);}return out;})();`;
eval(src);
process.stdout.write(JSON.stringify(globalThis.__qcOut));
