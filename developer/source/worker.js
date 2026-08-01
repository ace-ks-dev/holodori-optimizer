"use strict";
const CARDS = __CARDS__;
const CARD_BY_KEY = new Map(CARDS.map((c,i)=>[c.key,i]));
function uniqueOutfitIds(sourceIds){
  const out=[],seen=new Set();
  for(const i of sourceIds){const sig=JSON.stringify(CARDS[i].outfit?.effects||[]);if(!seen.has(sig)){seen.add(sig);out.push(i);}}
  return out;
}
const OUTFIT_UNIQUE_IDS=uniqueOutfitIds(CARDS.map((_,i)=>i));
const FIVE_STAR_CARD_IDS=CARDS.map((c,i)=>c.rarity===5?i:-1).filter(i=>i>=0);
const FIVE_STAR_OUTFIT_IDS=uniqueOutfitIds(FIVE_STAR_CARD_IDS);
const ALL_CARD_IDS=CARDS.map((_,i)=>i);
const ALL_OUTFIT_IDS=OUTFIT_UNIQUE_IDS;
const BIT_INDEX = new Int8Array(32); BIT_INDEX[1]=0; BIT_INDEX[2]=1; BIT_INDEX[4]=2; BIT_INDEX[8]=3; BIT_INDEX[16]=4;
const SUBSET_POP = new Int8Array(32); for(let s=1;s<32;s++) SUBSET_POP[s]=SUBSET_POP[s>>1]+(s&1);
const COUNTS = new Int32Array(32), INTER = new Uint32Array(32), MAPPED_COUNTS = new Int32Array(32);
const QPERF=new Float64Array(5), QTECH=new Float64Array(5), QSENSE=new Float64Array(5), QALL=new Float64Array(5), QSUPPORT=new Float64Array(5);
let MASKS=[], UPTIME=[], WORDS=0, SONG=140;

function popcount32(x){x=x-((x>>>1)&0x55555555);x=(x&0x33333333)+((x>>>2)&0x33333333);return ((((x+(x>>>4))&0x0F0F0F0F)*0x01010101)>>>24);}
function memberId(card){return card.characterId;}
function cardLabel(card){return card.displayKey||`${card.member} | ${card.skin}`;}
const ELIGIBILITY_CODES=new Map();
function eligibilityCode(id){if(!id)return -1;let code=ELIGIBILITY_CODES.get(id);if(code===undefined){code=ELIGIBILITY_CODES.size;ELIGIBILITY_CODES.set(id,code);}return code;}
function registerEligibility(x){if(x&&(x.kind==='attribute'||x.kind==='group'))eligibilityCode(x.id);}
for(const c of CARDS){eligibilityCode(c.attributeId);for(const gid of c.groupIds||[])eligibilityCode(gid);registerEligibility(c.active?.trigger);registerEligibility(c.passive?.target);registerEligibility(c.passive?.trigger);registerEligibility(c.special?.sarTrigger);for(const e of c.outfit?.effects||[])registerEligibility(e.trigger);}
const ELIGIBILITY_WORDS=Math.max(1,Math.ceil(ELIGIBILITY_CODES.size/32));
function setEligibility(words,id){const code=eligibilityCode(id);if(code>=0)words[code>>>5]|=1<<(code&31);}
for(const c of CARDS){const words=new Uint32Array(ELIGIBILITY_WORDS);setEligibility(words,c.attributeId);for(const gid of c.groupIds||[])setEligibility(words,gid);c._eligibilityWords=words;}
function annotateEligibility(x){if(x&&(x.kind==='attribute'||x.kind==='group')){const code=eligibilityCode(x.id);x._word=code>>>5;x._bit=1<<(code&31);}}
for(const c of CARDS){annotateEligibility(c.active?.trigger);annotateEligibility(c.passive?.target);annotateEligibility(c.passive?.trigger);annotateEligibility(c.special?.sarTrigger);for(const e of c.outfit?.effects||[])annotateEligibility(e.trigger);}
function targetEligible(card,target){if(!target)return false;if(target.kind==='all')return true;if(target.kind==='attribute'||target.kind==='group')return (card._eligibilityWords[target._word]&target._bit)!==0;return false;}
function triggerSatisfied(trigger,ids){
  if(!trigger)return true;
  if(trigger.kind==='attribute'||trigger.kind==='group'){let n=0;const word=trigger._word,bit=trigger._bit;for(let i=0;i<5;i++)if(CARDS[ids[i]]._eligibilityWords[word]&bit)n++;return n>=(trigger.count||1);}
  // The score model deliberately assumes gameplay-state conditions are satisfied.
  if(trigger.kind==='combo_gte'||trigger.kind==='life_gte'||trigger.kind==='life_lte'||trigger.kind==='judgement_gte')return true;
  return false;
}
function activeMagnitude(card,ids){
  const a=card.active;
  return a.conditionalMagnitude!==null&&a.conditionalMagnitude!==undefined&&triggerSatisfied(a.trigger,ids)?a.conditionalMagnitude:a.baseMagnitude;
}
function baseActiveProbability(card){return Math.max(0,Math.min(1,Number(card.active.probability)||0));}
function effectiveActiveProbability(card,sarMultiplier=1){return Math.min(1,baseActiveProbability(card)*sarMultiplier);}

const COMBO_SPECIAL_WEIGHTS=[0.92,0.96,1.00,1.04,1.08];
const NEUTRAL_SPECIAL_WEIGHTS=[1,1,1,1,1];
function specialData(card,ids){
  const s=card.special||{magnitude:0,duration:0,sarPct:0,sarTrigger:null,text:'Not modeled'};
  const sarPct=s.sarPct>0&&triggerSatisfied(s.sarTrigger,ids)?s.sarPct:0;
  return {magnitude:Number(s.magnitude)||0,duration:Number(s.duration)||0,hasSar:sarPct>0,sarPct,text:String(s.text||'')};
}
function specialForOrder(ids,params){
  if(params.specialMode==='off')return {bonus:0,values:[],sarWindows:[],sarCount:0};
  const weights=params.specialMode==='neutral'?NEUTRAL_SPECIAL_WEIGHTS:COMBO_SPECIAL_WEIGHTS;
  let bonus=0;const values=[],sarWindows=[];
  for(let i=0;i<5;i++){
    const card=CARDS[ids[i]],s=specialData(card,ids),exposure=Math.min(s.duration,SONG)/SONG;
    const direct=s.magnitude*s.duration/SONG,weighted=direct*weights[i];
    bonus+=weighted;
    const value={position:i+1,member:card.member,magnitude:s.magnitude,duration:s.duration,weight:weights[i],bonus:weighted,hasSar:s.hasSar,sarPct:s.sarPct,text:s.text};
    values.push(value);
    if(s.sarPct>0&&s.duration>0)sarWindows.push({...value,exposure,multiplier:1+s.sarPct});
  }
  return {bonus,values,sarWindows,sarCount:sarWindows.length};
}
function quickSpecialItems(ids,params){
  if(params.specialMode==='off')return ids.map(id=>({id,direct:0,sarPct:0,duration:0}));
  return ids.map(id=>{const s=specialData(CARDS[id],ids);return{id,direct:s.magnitude*s.duration/SONG,sarPct:s.sarPct,duration:s.duration};});
}
function buildMasks(song){SONG=song;WORDS=Math.ceil(song/32);UPTIME=new Int32Array(CARDS.length);MASKS=CARDS.map((c,ci)=>{const a=new Uint32Array(WORDS);const d=c.active.duration,iv=c.active.interval;let up=0;if(d>0&&iv>0){for(let t=1;t<=song;t++){if(t>=iv && (t%iv)<d){const z=t-1;a[z>>>5]|=(1<<(z&31));up++;}}}UPTIME[ci]=up;return a;});}
function calcCounts(ids,out=COUNTS){out.fill(0);for(let w=0;w<WORDS;w++){INTER[0]=0xFFFFFFFF;for(let s=1;s<32;s++){const bit=s&-s,idx=BIT_INDEX[bit];INTER[s]=INTER[s^bit]&MASKS[ids[idx]][w];out[s]+=popcount32(INTER[s]);}}return out;}
function mapCounts(base,perm,out=MAPPED_COUNTS){out[0]=0;for(let s=1;s<32;s++){let m=0;for(let p=0;p<5;p++)if(s&(1<<p))m|=1<<perm[p];out[s]=base[m];}return out;}
function permutations(arr){const out=[];function rec(a,l){if(l===a.length){out.push(a.slice());return;}for(let i=l;i<a.length;i++){[a[l],a[i]]=[a[i],a[l]];rec(a,l+1);[a[l],a[i]]=[a[i],a[l]];}}rec(arr.slice(),0);return out;}
const PERM4=permutations([1,2,3,4]).map(p=>[0,...p]);
const PERM5=permutations([0,1,2,3,4]);
class MinHeap{constructor(limit){this.a=[];this.limit=limit;}push(x){const a=this.a;if(a.length<this.limit){a.push(x);this.up(a.length-1);}else if(x.score>a[0].score){a[0]=x;this.down(0);}}up(i){const a=this.a;while(i){const p=(i-1)>>1;if(a[p].score<=a[i].score)break;[a[p],a[i]]=[a[i],a[p]];i=p;}}down(i){const a=this.a,n=a.length;for(;;){let l=i*2+1,r=l+1,m=i;if(l<n&&a[l].score<a[m].score)m=l;if(r<n&&a[r].score<a[m].score)m=r;if(m===i)break;[a[m],a[i]]=[a[i],a[m]];i=m;}}sorted(){return this.a.sort((x,y)=>y.score-x.score);}}

const TP=new Float64Array(5),TRANK=new Int8Array(5),TMAG=new Float64Array(5),TPRIORITY=new Int8Array([0,1,2,3,4]);
function timing(ids,counts,support,params,sarMultiplier=1,withDetails=false){
  const p=TP,rank=TRANK,magnitudes=TMAG,priority=TPRIORITY;for(let i=0;i<5;i++)priority[i]=i;
  for(let i=0;i<5;i++){p[i]=effectiveActiveProbability(CARDS[ids[i]],sarMultiplier);magnitudes[i]=activeMagnitude(CARDS[ids[i]],ids);}
  priority.sort((a,b)=>magnitudes[b]-magnitudes[a] || a-b);
  for(let r=0;r<5;r++)rank[priority[r]]=r;
  let raw=0,supported=0;
  for(let i=0;i<5;i++){
    let higher=0;for(let j=0;j<5;j++)if(rank[j]<rank[i])higher|=1<<j;
    let factor=0,sub=higher;
    for(;;){let prod=1;for(let j=0;j<5;j++)if(sub&(1<<j))prod*=p[j];factor+=(SUBSET_POP[sub]&1?-1:1)*prod*counts[(1<<i)|sub];if(sub===0)break;sub=(sub-1)&higher;}
    const contribution=magnitudes[i]*p[i]*factor/SONG;raw+=contribution;supported+=contribution*(1+support[i]);
  }
  let coverage=0;for(let s=1;s<32;s++){let prod=1;for(let j=0;j<5;j++)if(s&(1<<j))prod*=p[j];coverage+=(SUBSET_POP[s]&1?1:-1)*prod*counts[s]/SONG;}
  const out={raw,supported,coverage};if(withDetails){out.probabilities=Array.from(p);out.magnitudes=Array.from(magnitudes);}return out;
}
function sarForOrder(ids,counts,support,params,sp,baseTiming,withDetails=false){
  if(params.specialMode==='off'||!sp.sarWindows.length)return {rawUplift:0,passiveUplift:0,coverage:baseTiming.coverage,coverageUplift:0,values:[]};
  let rawUplift=0,passiveUplift=0,coverageUplift=0;const values=withDetails?[]:null;
  for(const window of sp.sarWindows){
    const boosted=timing(ids,counts,support,params,window.multiplier,withDetails);
    const rawDelta=(boosted.raw-baseTiming.raw)*window.exposure*window.weight;
    const passiveDelta=(boosted.supported-baseTiming.supported)*window.exposure*window.weight;
    const coverageDelta=(boosted.coverage-baseTiming.coverage)*window.exposure;
    rawUplift+=rawDelta;passiveUplift+=passiveDelta;coverageUplift+=coverageDelta;
    if(withDetails)values.push({...window,rawUplift:rawDelta,passiveUplift:passiveDelta,coverageUplift:coverageDelta,boostedProbabilities:boosted.probabilities});
  }
  return {rawUplift,passiveUplift,coverage:Math.min(1,baseTiming.coverage+coverageUplift),coverageUplift,values:values||[]};
}
function outfitBonuses(ids,outfitId,withDetails=false){
  const out=CARDS[outfitId].outfit||{effects:[]};
  let perf=0,tech=0,sense=0,all=0,support=0,triggeredCount=0;const details=withDetails?[]:null;
  for(const effect of out.effects||[]){
    const triggered=triggerSatisfied(effect.trigger,ids);if(withDetails)details.push({kind:effect.kind,pct:effect.pct,triggered});
    if(!triggered)continue;triggeredCount++;
    if(effect.kind==='perf')perf+=effect.pct;else if(effect.kind==='tech')tech+=effect.pct;else if(effect.kind==='sense')sense+=effect.pct;else if(effect.kind==='all')all+=effect.pct;else if(effect.kind==='support')support+=effect.pct;
  }
  return {perf,tech,sense,all,support,triggeredCount,details:details||[]};
}
function outfitOutcome(ids,outfitId,baseStat,sumPerf,sumTech,sumSense,tm,sp,sar,params,withDetails=false){
  const owner=CARDS[outfitId],bon=outfitBonuses(ids,outfitId,withDetails);
  const stat=baseStat+sumPerf*(bon.perf+bon.all)+sumTech*(bon.tech+bon.all)+sumSense*(bon.sense+bon.all);
  const baselineAdjusted=tm.supported+bon.support*tm.raw;
  const sarUplift=sar.passiveUplift+bon.support*sar.rawUplift;
  const adjusted=baselineAdjusted+sarUplift;
  const supportUplift=baselineAdjusted-tm.raw;
  const totalBonus=adjusted+sp.bonus+params.other;
  const index=stat*(1+totalBonus/100);
  return {score:index,stat,raw:tm.raw,uplift:supportUplift,sarUplift,supported:adjusted,coverage:sar.coverage,specialBonus:sp.bonus,totalBonus,
    outfitCard:owner.id,outfitKey:owner.key,outfitOwner:owner.member,outfitText:owner.outfit.text,outfitTriggered:bon.triggeredCount>0||!(owner.outfit.effects||[]).length,outfitSupport:bon.support,outfitExternal:!ids.includes(outfitId),outfitEffectDetails:bon.details};
}
const RECIPIENT_BUF=new Int8Array(5);
function passiveRecipients(ids,sourceIndex,pa,out=RECIPIENT_BUF){
  if(!triggerSatisfied(pa.trigger,ids))return 0;
  if(pa.target.kind==='self'){out[0]=sourceIndex;return 1;}
  let n=0;for(let i=0;i<5;i++)if(targetEligible(CARDS[ids[i]],pa.target))out[n++]=i;
  const count=pa.target.count||n;if(n<count)return 0;
  for(let i=1;i<n;i++){const v=out[i],vt=CARDS[ids[v]].total;let j=i-1;while(j>=0){const u=out[j],ut=CARDS[ids[u]].total;if(ut>vt||(ut===vt&&u<v))break;out[j+1]=u;j--;}out[j+1]=v;}
  return count;
}
function evaluateOrder(ids,counts,params,withDetails=false,compareOutfits=false){
  const perf=new Float64Array(5),tech=new Float64Array(5),sense=new Float64Array(5),all=new Float64Array(5),support=new Float64Array(5);
  const passiveDetails=[];
  for(let s=0;s<5;s++){
    const src=CARDS[ids[s]],pa=src.passive,nRecipients=passiveRecipients(ids,s,pa);if(!nRecipients)continue;
    for(let q=0;q<nRecipients;q++){const i=RECIPIENT_BUF[q];if(pa.kind==='support')support[i]+=pa.pct;else if(pa.kind==='perf')perf[i]+=pa.pct;else if(pa.kind==='tech')tech[i]+=pa.pct;else if(pa.kind==='sense')sense[i]+=pa.pct;else if(pa.kind==='all')all[i]+=pa.pct;}
    if(withDetails){const names=[];for(let q=0;q<nRecipients;q++)names.push(CARDS[ids[RECIPIENT_BUF[q]]].member);passiveDetails.push(`${src.member}: ${pa.text} → ${names.join(', ')}`);}
  }
  let baseStat=0,sumPerf=0,sumTech=0,sumSense=0;
  for(let i=0;i<5;i++){const c=CARDS[ids[i]];sumPerf+=c.perf;sumTech+=c.tech;sumSense+=c.sense;baseStat+=c.perf*(1+perf[i]+all[i])+c.tech*(1+tech[i]+all[i])+c.sense*(1+sense[i]+all[i]);}
  const sp=specialForOrder(ids,params),tm=timing(ids,counts,support,params,1,withDetails),sar=sarForOrder(ids,counts,support,params,sp,tm,withDetails);
  let bestTeam=null;
  for(let o=0;o<5;o++){const x=outfitOutcome(ids,ids[o],baseStat,sumPerf,sumTech,sumSense,tm,sp,sar,params,withDetails);if(!bestTeam||x.score>bestTeam.score)bestTeam=x;}
  let bestAny=bestTeam;
  if(params.outfitMode==='any'||(params.outfitMode==='fixed'&&compareOutfits)){
    for(const outfitId of params.ownedOutfitIds){const x=outfitOutcome(ids,outfitId,baseStat,sumPerf,sumTech,sumSense,tm,sp,sar,params,withDetails);if(!bestAny||x.score>bestAny.score)bestAny=x;}
  }
  let used=bestTeam,comparison=bestTeam;
  if(params.outfitMode==='any'){used=bestAny;comparison=bestAny;}
  else if(params.outfitMode==='fixed'){
    const fixed=CARD_BY_KEY.get(params.outfitKey);if(fixed===undefined)return null;
    used=outfitOutcome(ids,fixed,baseStat,sumPerf,sumTech,sumSense,tm,sp,sar,params,withDetails);comparison=compareOutfits?bestAny:used;
  }
  const result={...used,bestAvailableScore:comparison.score,bestAvailableOutfitCard:comparison.outfitCard,bestAvailableOutfitKey:comparison.outfitKey,bestAvailableOutfitOwner:comparison.outfitOwner,bestAvailableOutfitText:comparison.outfitText,bestAvailableOutfitTriggered:comparison.outfitTriggered,bestAvailableOutfitExternal:comparison.outfitExternal};
  if(withDetails){result.activeProbabilities=tm.probabilities;result.activeMagnitudes=tm.magnitudes;result.ids=ids.slice();result.cards=ids.map(i=>cardLabel(CARDS[i]));result.cardIds=ids.map(i=>CARDS[i].id);result.cardKeys=ids.map(i=>CARDS[i].key);result.cardProgress=ids.map(i=>({level:CARDS[i].level,bloom:CARDS[i].bloom,rarity:CARDS[i].rarity}));result.members=ids.map(i=>CARDS[i].member);result.passiveDetails=passiveDetails;result.support=Array.from(support);result.specialDetails=sp.values;result.sarDetails=sar.values;result.sarCount=sp.sarCount;result.coverageUplift=sar.coverageUplift;}
  return result;
}
function quickEvaluate(ids,params){
  QPERF.fill(0);QTECH.fill(0);QSENSE.fill(0);QALL.fill(0);QSUPPORT.fill(0);
  for(let s=0;s<5;s++){
    const src=CARDS[ids[s]],pa=src.passive,nRecipients=passiveRecipients(ids,s,pa);
    for(let q=0;q<nRecipients;q++){const i=RECIPIENT_BUF[q];if(pa.kind==='support')QSUPPORT[i]+=pa.pct;else if(pa.kind==='perf')QPERF[i]+=pa.pct;else if(pa.kind==='tech')QTECH[i]+=pa.pct;else if(pa.kind==='sense')QSENSE[i]+=pa.pct;else if(pa.kind==='all')QALL[i]+=pa.pct;}
  }
  let baseStat=0,sumPerf=0,sumTech=0,sumSense=0,raw=0,supported=0;
  for(let i=0;i<5;i++){
    const c=CARDS[ids[i]];sumPerf+=c.perf;sumTech+=c.tech;sumSense+=c.sense;baseStat+=c.perf*(1+QPERF[i]+QALL[i])+c.tech*(1+QTECH[i]+QALL[i])+c.sense*(1+QSENSE[i]+QALL[i]);
    const p=baseActiveProbability(c),contribution=activeMagnitude(c,ids)*p*UPTIME[ids[i]]/SONG;raw+=contribution;supported+=contribution*(1+QSUPPORT[i]);
  }
  let items=quickSpecialItems(ids,params).map(item=>{
    let rawSar=0,passiveSar=0;
    if(item.sarPct>0&&item.duration>0){let boostedRaw=0,boostedSupported=0;for(let i=0;i<5;i++){const c=CARDS[ids[i]],p=effectiveActiveProbability(c,1+item.sarPct),contribution=activeMagnitude(c,ids)*p*UPTIME[ids[i]]/SONG;boostedRaw+=contribution;boostedSupported+=contribution*(1+QSUPPORT[i]);}const exposure=Math.min(item.duration,SONG)/SONG;rawSar=(boostedRaw-raw)*exposure;passiveSar=(boostedSupported-supported)*exposure;}
    return {...item,rawSar,passiveSar};
  });
  if(params.specialMode==='combo')items.sort((a,b)=>(a.direct+a.passiveSar)-(b.direct+b.passiveSar));
  const weights=params.specialMode==='combo'?COMBO_SPECIAL_WEIGHTS:NEUTRAL_SPECIAL_WEIGHTS;let special=0,rawSar=0,passiveSar=0;
  for(let i=0;i<5;i++){special+=items[i].direct*weights[i];rawSar+=items[i].rawSar*weights[i];passiveSar+=items[i].passiveSar*weights[i];}
  function scoreWithOutfit(outfitId){const bon=outfitBonuses(ids,outfitId);const stat=baseStat+sumPerf*(bon.perf+bon.all)+sumTech*(bon.tech+bon.all)+sumSense*(bon.sense+bon.all);const adjusted=supported+passiveSar+bon.support*(raw+rawSar);return stat*(1+(adjusted+special+params.other)/100);}
  if(params.outfitMode==='fixed'){const fixed=CARD_BY_KEY.get(params.outfitKey);return fixed===undefined?-Infinity:scoreWithOutfit(fixed);}
  let best=-Infinity;const sources=params.outfitMode==='any'?(params._screening&&params.screenOutfitIds?params.screenOutfitIds:params.ownedOutfitIds):ids;for(const outfitId of sources){const score=scoreWithOutfit(outfitId);if(score>best)best=score;}return best;
}
function chooseK(n,k){if(k<0||n<k)return 0;if(k===0)return 1;k=Math.min(k,n-k);let v=1;for(let i=1;i<=k;i++)v=v*(n-k+i)/i;return Math.round(v);}
function enumerateK(arr,k,visit){const chosen=new Array(k);function rec(start,depth){if(depth===k){visit(chosen.slice());return;}const remaining=k-depth;for(let i=start;i<=arr.length-remaining;i++){chosen[depth]=arr[i];rec(i+1,depth+1);}}if(k===0)visit([]);else rec(0,0);}
function validateComparisonTeam(keys,label){if(!Array.isArray(keys)||keys.length!==5)throw new Error(`${label} must contain exactly five ordered cards.`);const ids=keys.map(key=>CARD_BY_KEY.get(key));if(ids.some(id=>id===undefined))throw new Error(`${label} contains a card that is not in the current database.`);const members=new Set();for(const id of ids){const member=memberId(CARDS[id]);if(members.has(member))throw new Error(`${label} cannot contain two cards of the same holomem.`);members.add(member);}return ids;}
function hashSeed(value){const text=JSON.stringify(value);let h=2166136261>>>0;for(let i=0;i<text.length;i++){h^=text.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
function seededRandom(seed){let a=seed>>>0;return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function percentileSorted(sorted,q){if(!sorted.length)return 0;const pos=(sorted.length-1)*q,lo=Math.floor(pos),hi=Math.ceil(pos),f=pos-lo;return sorted[lo]*(1-f)+sorted[hi]*f;}
function meanAndSd(values){let sum=0;for(const v of values)sum+=v;const mean=sum/values.length;let ss=0;for(const v of values){const d=v-mean;ss+=d*d;}return {mean,sd:Math.sqrt(ss/Math.max(1,values.length-1))};}
function simulateTeamScores(ids,result,params,draws,rng){
  const magnitudes=ids.map(id=>activeMagnitude(CARDS[id],ids)),priorities=[0,1,2,3,4].sort((a,b)=>magnitudes[b]-magnitudes[a]||a-b);
  const passiveSupport=result.support||[0,0,0,0,0],outfitSupport=result.outfitSupport||0,scores=new Float64Array(draws),activeUntil=new Int32Array(5),probabilities=ids.map(id=>baseActiveProbability(CARDS[id]));
  const fixedBonus=(result.sarUplift||0)+(result.specialBonus||0)+(params.other||0);
  for(let run=0;run<draws;run++){
    activeUntil.fill(0);let activeTotal=0;
    for(let t=1;t<=SONG;t++){
      for(let i=0;i<5;i++){const active=CARDS[ids[i]].active,iv=active.interval;if(iv>0&&t>=iv&&t%iv===0&&rng()<probabilities[i])activeUntil[i]=t+Math.max(0,active.duration)-1;}
      for(const i of priorities){if(activeUntil[i]>=t){activeTotal+=magnitudes[i]*(1+passiveSupport[i]+outfitSupport);break;}}
    }
    const activeAverage=activeTotal/SONG;scores[run]=result.stat*(1+(activeAverage+fixedBonus)/100);
  }
  const stats=meanAndSd(scores),shift=result.score-stats.mean;if(Math.abs(shift)>1e-12)for(let i=0;i<scores.length;i++)scores[i]+=shift;return scores;
}
function compareSummary(values){const sorted=Array.from(values).sort((a,b)=>a-b),stats=meanAndSd(sorted);return {mean:stats.mean,sd:stats.sd,p05:percentileSorted(sorted,0.05),median:percentileSorted(sorted,0.5),p95:percentileSorted(sorted,0.95)};}
function comparisonInterpretation(advantage){if(advantage<0.02)return 'Practical near-tie: normal Active proc luck can readily reverse the expected order.';if(advantage<0.05)return 'Small expected advantage: meaningful over repeated runs, but often reversible in a single run.';if(advantage<0.10)return 'Meaningful expected advantage: the stronger team should win most comparisons, though unlucky sets can still lose.';return 'Proc-robust expected advantage under this model: ordinary Active luck should overturn it only occasionally.';}
function compareTeams(params){
  const idsA=validateComparisonTeam(params.teamA,'Team A'),idsB=validateComparisonTeam(params.teamB,'Team B');const outfitA=CARD_BY_KEY.get(params.outfitA),outfitB=CARD_BY_KEY.get(params.outfitB);if(outfitA===undefined||outfitB===undefined)throw new Error('Select a valid Outfit card for both teams.');
  const song=Number(params.song),runs=Math.max(1,Math.round(Number(params.runsPerAverage)||1));if(!Number.isFinite(song)||song<30||song>600)throw new Error('Song length must be between 30 and 600 seconds.');if(![1,3,5,10,20].includes(runs))throw new Error('Choose 1, 3, 5, 10, or 20 runs per average.');
  const modelParams={song,specialMode:params.specialMode||'combo',other:Number(params.other)||0,outfitMode:'fixed',ownedOutfitIds:OUTFIT_UNIQUE_IDS};buildMasks(song);
  calcCounts(idsA,COUNTS);const countsA=new Int32Array(COUNTS);modelParams.outfitKey=CARDS[outfitA].key;const resultA=evaluateOrder(idsA,countsA,modelParams,true,false);
  calcCounts(idsB,COUNTS);const countsB=new Int32Array(COUNTS);modelParams.outfitKey=CARDS[outfitB].key;const resultB=evaluateOrder(idsB,countsB,modelParams,true,false);if(!resultA||!resultB)throw new Error('The selected teams could not be evaluated.');
  const individualDraws=25000,comparisonDraws=20000,seed=hashSeed({teamA:params.teamA,outfitA:params.outfitA,teamB:params.teamB,outfitB:params.outfitB,song,runs,specialMode:modelParams.specialMode,other:modelParams.other});const rng=seededRandom(seed);
  self.postMessage({type:'compareProgress',phase:'Simulating Team A',progress:0.1});const scoresA=simulateTeamScores(idsA,resultA,modelParams,individualDraws,rng);
  self.postMessage({type:'compareProgress',phase:'Simulating Team B',progress:0.45});const scoresB=simulateTeamScores(idsB,resultB,modelParams,individualDraws,rng);
  self.postMessage({type:'compareProgress',phase:`Comparing ${runs}-run averages`,progress:0.78});const avgA=new Float64Array(comparisonDraws),avgB=new Float64Array(comparisonDraws);let winsA=0,winsB=0,ties=0;
  for(let d=0;d<comparisonDraws;d++){let totalA=0,totalB=0;for(let r=0;r<runs;r++){totalA+=scoresA[Math.floor(rng()*scoresA.length)];totalB+=scoresB[Math.floor(rng()*scoresB.length)];}const a=totalA/runs,b=totalB/runs;avgA[d]=a;avgB[d]=b;if(a>b)winsA++;else if(b>a)winsB++;else ties++;}
  const expectedRatio=resultB.score?resultA.score/resultB.score:Infinity,expectedDiff=expectedRatio-1,winner=resultA.score>=resultB.score?'A':'B',stronger=Math.max(resultA.score,resultB.score),weaker=Math.min(resultA.score,resultB.score),advantage=weaker?stronger/weaker-1:Infinity;
  return {teamA:resultA,teamB:resultB,runsPerAverage:runs,individualDraws,comparisonDraws,expectedDiff,advantage,winner,winProbabilityA:winsA/comparisonDraws,winProbabilityB:winsB/comparisonDraws,tieProbability:ties/comparisonDraws,rangeA:compareSummary(avgA),rangeB:compareSummary(avgB),individualA:compareSummary(scoresA),individualB:compareSummary(scoresB),interpretation:comparisonInterpretation(advantage),seed};
}

const SEARCH_PROFILES={
  fast:{beam:6000,global:5000,rescue:1000,featureQuota:55,finalScreen:8000,polishSeeds:60,polishRounds:1,refine:2500,exactFinalists:250,extensionTop:36,featureExtensions:8,spreadExtensions:8},
  balanced:{beam:18000,global:15000,rescue:3000,featureQuota:160,finalScreen:24000,polishSeeds:180,polishRounds:1,refine:6000,exactFinalists:600,extensionTop:64,featureExtensions:14,spreadExtensions:12},
  thorough:{beam:50000,global:42000,rescue:8000,featureQuota:430,finalScreen:65000,polishSeeds:450,polishRounds:2,refine:12000,exactFinalists:1500,extensionTop:110,featureExtensions:24,spreadExtensions:18}
};
class BeamHeap{
  constructor(limit){this.a=[];this.limit=Math.max(1,limit|0);}
  consider(score,ids,lastPos){if(!Number.isFinite(score))return;const a=this.a;if(a.length<this.limit){const x={score,ids:ids.slice(),lastPos};a.push(x);this.up(a.length-1);}else if(score>a[0].score){a[0]={score,ids:ids.slice(),lastPos};this.down(0);}}
  considerNode(node){this.consider(node.score,node.ids,node.lastPos);}
  up(i){const a=this.a;while(i){const p=(i-1)>>1;if(a[p].score<=a[i].score)break;[a[p],a[i]]=[a[i],a[p]];i=p;}}
  down(i){const a=this.a,n=a.length;for(;;){let l=i*2+1,r=l+1,m=i;if(l<n&&a[l].score<a[m].score)m=l;if(r<n&&a[r].score<a[m].score)m=r;if(m===i)break;[a[m],a[i]]=[a[i],a[m]];i=m;}}
  sorted(){return this.a.sort((x,y)=>y.score-x.score);}
}
function teamPoolAllows(card,cardPool){return cardPool==='all'||card.rarity===5;}
function countValidCompositions(candidateIds,k){
  if(k<0)return 0;if(k===0)return 1;
  const multiplicity=new Map();for(const id of candidateIds){const m=memberId(CARDS[id]);multiplicity.set(m,(multiplicity.get(m)||0)+1);}
  const dp=new Float64Array(k+1);dp[0]=1;
  for(const m of multiplicity.values())for(let j=k;j>=1;j--)dp[j]+=dp[j-1]*m;
  return Math.round(dp[k]);
}
function searchStaticPotential(id){
  const c=CARDS[id],a=c.active||{},s=c.special||{},pa=c.passive||{},p=baseActiveProbability(c),mag=Math.max(Number(a.baseMagnitude)||0,Number(a.conditionalMagnitude)||0),active=mag*p*(UPTIME[id]||0)/Math.max(1,SONG),special=(Number(s.magnitude)||0)*(Number(s.duration)||0)/Math.max(1,SONG),sar=(Number(s.sarPct)||0)*(Number(s.duration)||0)/Math.max(1,SONG),passive=(Number(pa.pct)||0)*(pa.target?.count||1);
  return c.total*(1+(active+special)/100)+c.total*passive*0.22+c.total*sar*0.12;
}
function screeningOutfits(sourceIds){
  const bestByBucket=new Map(),overall=[];
  for(const id of sourceIds){const effects=CARDS[id].outfit?.effects||[];let strength=0;for(const e of effects){const kind=e.kind||'x',tr=e.trigger,ts=tr&&(tr.kind==='attribute'||tr.kind==='group')?`${tr.kind}:${tr.id}:${tr.count||1}`:'none';const weight=kind==='support'?1.15:1;const val=(Number(e.pct)||0)*weight;strength+=val;const key=`${ts}|${kind}`;const prev=bestByBucket.get(key);if(!prev||val>prev.val)bestByBucket.set(key,{id,val});}overall.push({id,strength});}
  overall.sort((a,b)=>b.strength-a.strength);const out=[],seen=new Set();const add=id=>{if(id!==undefined&&!seen.has(id)){seen.add(id);out.push(id);}};for(let i=0;i<Math.min(12,overall.length);i++)add(overall[i].id);for(const x of bestByBucket.values())add(x.id);return out.slice(0,32);
}
function teamHasMember(ids,charId){for(const id of ids)if(memberId(CARDS[id])===charId)return true;return false;}
function greedyComplete(partial,staticOrder){
  const out=partial.slice();if(out.length>=5)return out;
  const members=new Set(out.map(id=>memberId(CARDS[id]))),chosen=new Set(out);
  for(const id of staticOrder){if(out.length>=5)break;if(chosen.has(id))continue;const m=memberId(CARDS[id]);if(members.has(m))continue;members.add(m);chosen.add(id);out.push(id);}
  return out.length===5?out:null;
}
function partialFeatureCount(ids,trigger){if(!trigger||(trigger.kind!=='attribute'&&trigger.kind!=='group'))return 0;let n=0;const word=trigger._word,bit=trigger._bit;for(const id of ids)if(CARDS[id]._eligibilityWords[word]&bit)n++;return n;}
function openConditionBonus(partial,slotsRemaining,projected,projectedStat){
  if(slotsRemaining<=0)return 0;let bonus=0;
  const maybe=(trigger)=>{if(!trigger||(trigger.kind!=='attribute'&&trigger.kind!=='group'))return 0;const need=trigger.count||1,have=partialFeatureCount(partial,trigger);if(have>=need||have+slotsRemaining<need||triggerSatisfied(trigger,projected))return 0;return Math.min(1,have/Math.max(1,need));};
  for(const id of partial){const c=CARDS[id],a=c.active||{},pa=c.passive||{};let f=maybe(a.trigger);if(f&&a.conditionalMagnitude!==null&&a.conditionalMagnitude!==undefined){const delta=Math.max(0,Number(a.conditionalMagnitude)-Number(a.baseMagnitude||0))*baseActiveProbability(c)*(UPTIME[id]||0)/Math.max(1,SONG);bonus+=projectedStat*(delta/100)*0.50*f;}
    f=maybe(pa.trigger);if(f){const pct=Number(pa.pct)||0,count=pa.target?.count||1;if(pa.kind==='support')bonus+=projectedStat*pct*0.025*count*f;else bonus+=projectedStat*pct*0.10*count*f;}
    if(c.outfit?.effects)for(const e of c.outfit.effects){f=maybe(e.trigger);if(f){const pct=Number(e.pct)||0;bonus+=projectedStat*pct*(e.kind==='support'?0.025:0.10)*f;}}
  }
  return bonus;
}
function screenPartial(partial,staticOrder,params){
  const projected=greedyComplete(partial,staticOrder);if(!projected)return -Infinity;const prior=params._screening;params._screening=true;const base=quickEvaluate(projected,params);params._screening=prior;let projectedStat=0;for(const id of projected)projectedStat+=CARDS[id].total;return base+openConditionBonus(partial,5-partial.length,projected,projectedStat);
}
function searchFeatureCodes(){
  const set=new Set();const add=x=>{if(x&&(x.kind==='attribute'||x.kind==='group'))set.add(eligibilityCode(x.id));};
  for(const c of CARDS){add(c.active?.trigger);add(c.passive?.trigger);add(c.passive?.target);add(c.special?.sarTrigger);for(const e of c.outfit?.effects||[])add(e.trigger);}return [...set];
}
const SEARCH_FEATURE_CODES=searchFeatureCodes();
for(const c of CARDS){const a=[];for(const code of SEARCH_FEATURE_CODES){const word=code>>>5,bit=1<<(code&31);if(c._eligibilityWords[word]&bit)a.push(code);}c._searchFeatureCodes=a;}
function featureCodesForTeam(ids,outSet){outSet.clear();for(const id of ids)for(const code of CARDS[id]._searchFeatureCodes||[])outSet.add(code);return outSet;}
function desiredFeatureCodes(ids,outSet){
  outSet.clear();const add=x=>{if(x&&(x.kind==='attribute'||x.kind==='group'))outSet.add(eligibilityCode(x.id));};
  for(const id of ids){const c=CARDS[id];for(const code of c._searchFeatureCodes||[])outSet.add(code);add(c.active?.trigger);add(c.passive?.trigger);add(c.passive?.target);add(c.special?.sarTrigger);for(const e of c.outfit?.effects||[])add(e.trigger);}return outSet;
}
function buildFeatureCandidateLists(staticOrder){const out=new Map(SEARCH_FEATURE_CODES.map(code=>[code,[]]));for(const id of staticOrder)for(const code of CARDS[id]._searchFeatureCodes||[])out.get(code)?.push(id);return out;}
function extensionPositions(parent,staticOrder,positionById,featureLists,profile,desiredScratch){
  const start=parent.lastPos+1,n=staticOrder.length;if(parent.ids.length<2){const all=[];for(let p=start;p<n;p++)all.push(p);return all;}
  const set=new Set();let added=0;for(let p=start;p<n&&added<profile.extensionTop;p++){set.add(p);added++;}
  desiredFeatureCodes(parent.ids,desiredScratch);for(const code of desiredScratch){const list=featureLists.get(code)||[];let take=0;for(const id of list){const p=positionById.get(id);if(p===undefined||p<start)continue;set.add(p);if(++take>=profile.featureExtensions)break;}}
  const remain=n-start;if(remain>0&&profile.spreadExtensions>0){for(let j=1;j<=profile.spreadExtensions;j++){const p=start+Math.floor(j*remain/(profile.spreadExtensions+1));if(p>=start&&p<n)set.add(p);}}
  return [...set].sort((a,b)=>a-b);
}
function mergeBeam(globalHeap,featureHeaps,profile){
  const global=globalHeap.sorted(),seen=new Set(global.map(n=>n.ids.join(','))),rescues=[];
  for(const h of featureHeaps.values())for(const n of h.sorted()){const key=n.ids.join(',');if(!seen.has(key)){seen.add(key);rescues.push(n);}}
  rescues.sort((a,b)=>b.score-a.score);return global.concat(rescues.slice(0,profile.rescue)).sort((a,b)=>b.score-a.score).slice(0,profile.beam);
}
function canonicalComposition(ids,requiredId,positionById){if(requiredId===null)return ids.slice().sort((a,b)=>(positionById.get(a)??1e9)-(positionById.get(b)??1e9));const rest=ids.filter(id=>id!==requiredId).sort((a,b)=>(positionById.get(a)??1e9)-(positionById.get(b)??1e9));return [requiredId,...rest];}
function polishCompositions(initial,candidates,requiredId,staticOrder,positionById,params,profile,counters){
  let current=initial.slice();const locked=requiredId===null?-1:0;
  for(let round=0;round<profile.polishRounds;round++){
    const seedCount=Math.min(profile.polishSeeds,current.length),heap=new BeamHeap(profile.finalScreen),seen=new Set();for(const x of current){heap.consider(x.score,x.ids,x.lastPos??-1);seen.add(x.ids.join(','));}
    for(let s=0;s<seedCount;s++){const seed=current[s].ids;for(let pos=0;pos<5;pos++){if(pos===locked)continue;for(const cid of candidates){if(seed[pos]===cid)continue;const cm=memberId(CARDS[cid]);let bad=false;for(let j=0;j<5;j++)if(j!==pos&&memberId(CARDS[seed[j]])===cm){bad=true;break;}if(bad)continue;const trial=seed.slice();trial[pos]=cid;const canon=canonicalComposition(trial,requiredId,positionById),key=canon.join(',');if(seen.has(key))continue;seen.add(key);params._screening=true;const score=quickEvaluate(canon,params);params._screening=false;counters.polishEvaluated++;heap.consider(score,canon,positionById.get(canon[canon.length-1])??-1);}}
      if((s+1)%20===0)self.postMessage({type:'progress',phase:`Polishing candidate neighborhoods (round ${round+1})`,done:s+1,total:seedCount,valid:counters.completeScreened,best:heap.a.length?Math.max(...heap.a.map(x=>x.score)):0});}
    current=heap.sorted();
  }
  return current;
}
function representativePerms(canon,params){
  const seeds=[[0,1,2,3,4],[1,2,3,4,0],[2,3,4,0,1],[3,4,0,1,2],[4,0,1,2,3],[4,3,2,1,0]],idx=[0,1,2,3,4];
  const specialValue=i=>{const s=CARDS[canon[i]].special||{};return (Number(s.magnitude)||0)*(Number(s.duration)||0)+(Number(s.sarPct)||0)*1000;};
  const activeValue=i=>Math.max(Number(CARDS[canon[i]].active?.baseMagnitude)||0,Number(CARDS[canon[i]].active?.conditionalMagnitude)||0)*baseActiveProbability(CARDS[canon[i]]);
  seeds.push(idx.slice().sort((a,b)=>specialValue(a)-specialValue(b)||a-b));
  seeds.push(idx.slice().sort((a,b)=>specialValue(b)-specialValue(a)||a-b));
  seeds.push(idx.slice().sort((a,b)=>activeValue(b)-activeValue(a)||a-b));
  seeds.push(idx.slice().sort((a,b)=>activeValue(a)-activeValue(b)||a-b));
  seeds.push(idx.slice().sort((a,b)=>CARDS[canon[b]].total-CARDS[canon[a]].total||a-b));
  seeds.push(idx.slice().sort((a,b)=>CARDS[canon[a]].total-CARDS[canon[b]].total||a-b));
  const out=[],seen=new Set();for(const p of seeds){const k=p.join('');if(!seen.has(k)){seen.add(k);out.push(p);}}return out;
}
function optimize(params){
  params.cardPool=params.cardPool==='all'?'all':'five';params.searchQuality=SEARCH_PROFILES[params.searchQuality]?params.searchQuality:'balanced';const profile=SEARCH_PROFILES[params.searchQuality];
  let anchor=null;if(params.searchMode==='anchor'){anchor=CARD_BY_KEY.get(params.anchor);if(anchor===undefined)throw new Error('Select a valid oshi card.');if(!teamPoolAllows(CARDS[anchor],params.cardPool))throw new Error('The selected oshi card is outside the chosen team-card pool.');}
  let fixedOutfit=null;if(params.outfitMode==='fixed'){fixedOutfit=CARD_BY_KEY.get(params.outfitKey);if(fixedOutfit===undefined)throw new Error('Select a valid specific outfit.');}
  const ownedKeys=params.ownedOnly?new Set(params.ownedKeys||[]):null,ownedIds=params.ownedOnly?new Set():null;
  if(params.ownedOnly){for(const key of ownedKeys){const id=CARD_BY_KEY.get(key);if(id!==undefined)ownedIds.add(id);}const eligibleOwned=Array.from(ownedIds).filter(i=>teamPoolAllows(CARDS[i],params.cardPool));if(eligibleOwned.length<5)throw new Error('Select at least five owned cards in the chosen team-card pool.');const distinctOwned=new Set(eligibleOwned.map(i=>memberId(CARDS[i])));if(distinctOwned.size<5)throw new Error('Your owned selection must contain at least five different holomems in the chosen team-card pool.');if(anchor!==null&&!ownedIds.has(anchor))throw new Error('The selected oshi card is not marked as owned.');if(fixedOutfit!==null&&!ownedIds.has(fixedOutfit))throw new Error('The selected specific Outfit Skill belongs to a card that is not marked as owned.');}
  params.ownedIdSet=ownedIds;params.ownedOutfitIds=params.ownedOnly?uniqueOutfitIds(Array.from(ownedIds)):ALL_OUTFIT_IDS;params.screenOutfitIds=screeningOutfits(params.ownedOutfitIds);buildMasks(params.song);
  const excludedMembers=new Set(),excludedCards=new Set();for(const value of params.excluded||[]){if(value.startsWith('member:'))excludedMembers.add(value.slice(7));else if(value.startsWith('card:'))excludedCards.add(value.slice(5));}
  const required=[];if(anchor!==null)required.push(anchor);for(const x of required){if(excludedMembers.has(memberId(CARDS[x]))||excludedCards.has(CARDS[x].id))throw new Error('The required oshi card is also selected under Exclude units.');}
  const requiredMembers=new Set(required.map(i=>memberId(CARDS[i]))),candidates=[];
  for(let i=0;i<CARDS.length;i++){if(!teamPoolAllows(CARDS[i],params.cardPool))continue;if(params.ownedOnly&&!ownedIds.has(i))continue;if(required.includes(i)||requiredMembers.has(memberId(CARDS[i])))continue;if(excludedMembers.has(memberId(CARDS[i]))||excludedCards.has(CARDS[i].id))continue;candidates.push(i);}
  const need=5-required.length;if(need<0||candidates.length<need)throw new Error('Not enough eligible cards remain to form a five-member team.');const rawValid=countValidCompositions(candidates,need);if(!rawValid)throw new Error('No valid five-member teams remain after the current filters.');
  const staticOrder=candidates.slice().sort((a,b)=>searchStaticPotential(b)-searchStaticPotential(a)||CARDS[a].id.localeCompare(CARDS[b].id)),positionById=new Map(staticOrder.map((id,i)=>[id,i])),featureCandidateLists=buildFeatureCandidateLists(staticOrder);
  const counters={partialEvaluated:0,completeScreened:0,polishEvaluated:0};let beam=[{score:0,ids:required.slice(),lastPos:-1}],depth=required.length;const featureScratch=new Set(),desiredScratch=new Set();
  while(depth<5){const nextDepth=depth+1,globalHeap=new BeamHeap(profile.global),featureHeaps=new Map(SEARCH_FEATURE_CODES.map(code=>[code,new BeamHeap(profile.featureQuota)]));let parentDone=0;
    for(const parent of beam){const extensionList=extensionPositions(parent,staticOrder,positionById,featureCandidateLists,profile,desiredScratch);for(const pos of extensionList){const cid=staticOrder[pos],cm=memberId(CARDS[cid]);if(teamHasMember(parent.ids,cm))continue;const ids=parent.ids.concat(cid);counters.partialEvaluated++;const score=screenPartial(ids,staticOrder,params);if(nextDepth===5)counters.completeScreened++;globalHeap.consider(score,ids,pos);featureCodesForTeam(ids,featureScratch);for(const code of featureScratch)featureHeaps.get(code)?.consider(score,ids,pos);}
      parentDone++;if(parentDone%Math.max(1,Math.floor(beam.length/40))===0||parentDone===beam.length)self.postMessage({type:'progress',phase:`Building ${nextDepth}-card candidates`,done:parentDone,total:beam.length,valid:counters.completeScreened,best:globalHeap.a.length?Math.max(...globalHeap.a.map(x=>x.score)):0});}
    beam=mergeBeam(globalHeap,featureHeaps,profile);depth=nextDepth;if(!beam.length)throw new Error('Search beam became empty; loosen exclusions or change the team-card pool.');
  }
  beam=beam.slice(0,profile.finalScreen);self.postMessage({type:'progress',phase:'Local neighborhood polish',done:0,total:Math.min(profile.polishSeeds,beam.length),valid:counters.completeScreened,best:beam[0]?.score||0});beam=polishCompositions(beam,candidates,anchor,staticOrder,positionById,params,profile,counters);
  const refineLimit=Math.min(profile.refine,Math.max(1500,params.topN*180)),refinedHeap=new MinHeap(refineLimit);params._screening=false;
  self.postMessage({type:'progress',phase:'Refining scalable-search finalists',done:0,total:beam.length,valid:counters.completeScreened,best:beam[0]?.score||0});
  for(let q=0;q<beam.length;q++){const canon=beam[q].ids;calcCounts(canon,COUNTS);const baseCounts=new Int32Array(COUNTS);let best=-Infinity;for(const perm of representativePerms(canon,params)){const ids=perm.map(i=>canon[i]);mapCounts(baseCounts,perm,MAPPED_COUNTS);const ev=evaluateOrder(ids,MAPPED_COUNTS,params,false);if(ev&&ev.score>best)best=ev.score;}if(best>-Infinity)refinedHeap.push({score:best,ids:canon.slice()});if(q%100===0||q===beam.length-1)self.postMessage({type:'progress',phase:'Refining scalable-search finalists',done:q+1,total:beam.length,valid:counters.completeScreened,best:refinedHeap.a.length?Math.max(...refinedHeap.a.map(x=>x.score)):0});}
  const shortlist=refinedHeap.sorted(),exactCount=Math.min(shortlist.length,Math.max(profile.exactFinalists,params.topN*10)),exactShortlist=shortlist.slice(0,exactCount);self.postMessage({type:'progress',phase:'Exhaustive order verification',done:0,total:exactShortlist.length,valid:counters.completeScreened,best:exactShortlist[0]?.score||0});const finalHeap=new MinHeap(params.topN),perms=(anchor===null||params.fullOrder)?PERM5:PERM4;
  for(let q=0;q<exactShortlist.length;q++){const canon=exactShortlist[q].ids;calcCounts(canon,COUNTS);const baseCounts=new Int32Array(COUNTS);let bestCombo=null,bestIds=null,bestFree=null,bestFreeIds=null;for(const perm of perms){const ids=perm.map(i=>canon[i]);mapCounts(baseCounts,perm,MAPPED_COUNTS);const ev=evaluateOrder(ids,MAPPED_COUNTS,params,false,params.outfitMode==='fixed');if(!ev)continue;if(!bestCombo||ev.score>bestCombo.score){bestCombo=ev;bestIds=ids.slice();}if(!bestFree||ev.bestAvailableScore>bestFree.bestAvailableScore){bestFree=ev;bestFreeIds=ids.slice();}}if(!bestCombo)continue;const posMap=bestIds.map(x=>canon.indexOf(x));mapCounts(baseCounts,posMap,MAPPED_COUNTS);const detailed=evaluateOrder(bestIds,MAPPED_COUNTS,params,true,params.outfitMode==='fixed');detailed.bestAvailableScore=bestFree.bestAvailableScore;detailed.bestAvailableOutfitCard=bestFree.bestAvailableOutfitCard;detailed.bestAvailableOutfitKey=bestFree.bestAvailableOutfitKey;detailed.bestAvailableOutfitOwner=bestFree.bestAvailableOutfitOwner;detailed.bestAvailableOutfitText=bestFree.bestAvailableOutfitText;detailed.bestAvailableOutfitTriggered=bestFree.bestAvailableOutfitTriggered;detailed.bestAvailableOutfitExternal=bestFree.bestAvailableOutfitExternal;detailed.bestAvailableOrder=bestFreeIds.map(i=>cardLabel(CARDS[i]));detailed.outfitPenalty=bestFree.bestAvailableScore?Math.max(0,(bestFree.bestAvailableScore-detailed.score)/bestFree.bestAvailableScore):0;finalHeap.push(detailed);if(q%25===0||q===exactShortlist.length-1)self.postMessage({type:'progress',phase:'Exhaustive order verification',done:q+1,total:exactShortlist.length,valid:counters.completeScreened,best:finalHeap.a.length?Math.max(...finalHeap.a.map(x=>x.score)):0});}
  const results=finalHeap.sorted(),best=results[0]?.score||1;for(const r of results)r.gap=(best-r.score)/best;return {results,tested:counters.partialEvaluated,valid:counters.completeScreened,shortlisted:exactShortlist.length,rawValid,anchor:anchor===null?null:CARDS[anchor].id,searchMode:params.searchMode,outfitMode:params.outfitMode,outfitKey:params.outfitKey,searchStats:{strategy:'v2.2 bounded beam + diversity rescue + local polish',quality:params.searchQuality,cardPool:params.cardPool,rawValid,partialEvaluated:counters.partialEvaluated,completeScreened:counters.completeScreened,polishEvaluated:counters.polishEvaluated,beamWidth:profile.beam,refined:shortlist.length,exactOrderFinalists:exactShortlist.length,screenOutfits:params.screenOutfitIds.length}};
}
self.onmessage=e=>{try{if(e.data&&e.data.action==='compare'){const out=compareTeams(e.data);self.postMessage({type:'compareDone',...out});}else{const out=optimize(e.data);self.postMessage({type:'done',...out});}}catch(err){self.postMessage({type:'error',message:err.message,stack:err.stack});}};
