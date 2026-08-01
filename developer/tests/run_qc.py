#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
DEVELOPER=HERE.parent
PYROOT=DEVELOPER/'python'
sys.path.insert(0,str(PYROOT))
# In a packaged release, developer/ sits below the release root; in the source tree
# used during development, built artifacts live in developer/dist.
PACKAGE_ROOT=DEVELOPER.parent
if not (PACKAGE_ROOT/'Holodori_Optimizer_v2.2.0.html').exists():
    PACKAGE_ROOT=DEVELOPER/'dist'

from holodori_optimizer.materialize import materialize_card, materialize_master
from holodori_optimizer.normalize import normalize_master
from holodori_optimizer.pack import inflate_master, pack_master
from holodori_optimizer.rawio import load_raw
from holodori_optimizer.reference import evaluate_order
from holodori_optimizer.validate import semantic_diff, validate_master


def fail(msg):
    raise AssertionError(msg)


def node_json(args):
    return json.loads(subprocess.check_output(['node',*map(str,args)],text=True))


def extract_inline_script(html_path: Path, out_path: Path):
    text=html_path.read_text(encoding='utf-8')
    start=text.index('<script>')+len('<script>'); end=text.rindex('</script>')
    out_path.write_text(text[start:end],encoding='utf-8')


def numeric_close(a,b,rel=1e-10,abs_tol=1e-9):
    return abs(float(a)-float(b)) <= max(abs_tol,abs(float(b))*rel)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',default=str(PACKAGE_ROOT/'HolodoriDB_Bundled_Normalized_Snapshot.json'))
    ap.add_argument('--html',default=str(PACKAGE_ROOT/'Holodori_Optimizer_v2.2.0.html'))
    ap.add_argument('--worker',default=str(DEVELOPER/'source'/'worker.js'))
    ap.add_argument('--raw',default=None)
    ap.add_argument('--search-regression',action='store_true')
    ap.add_argument('--large-search',action='store_true')
    args=ap.parse_args()
    snapshot_path=Path(args.snapshot); html_path=Path(args.html); worker_path=Path(args.worker)
    master=validate_master(json.loads(snapshot_path.read_text(encoding='utf-8')))
    checks=[]

    # Packed embedding round trip.
    inflated=inflate_master(pack_master(master))
    diffs=semantic_diff(master,inflated)
    if diffs: fail(f'pack/inflate round-trip drift: {diffs[:3]}')
    checks.append('Python pack/inflate round-trip: exact')

    # Asset identifiers are deliberately carried into schema v2.
    coverage=sum(bool(c.get('assetId')) for c in master['cards'])
    if coverage != len(master['cards']): fail(f'assetId coverage {coverage}/{len(master["cards"])}')
    checks.append(f'assetId coverage: {coverage}/{len(master["cards"])}')

    # Python materialization invariants.
    mat=materialize_master(master)
    if any(c['total'] != c['perf']+c['tech']+c['sense'] for c in mat): fail('materialized total mismatch')
    checks.append(f'Python max-progression materialization: {len(mat)} cards')

    node=shutil.which('node')
    if node:
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            inline=td/'inline.js'; extract_inline_script(html_path,inline)
            subprocess.check_call([node,'--check',str(inline)],stdout=subprocess.DEVNULL)
            subprocess.check_call([node,'--check',str(worker_path)],stdout=subprocess.DEVNULL)
            checks.append('JavaScript syntax: HTML inline script + worker pass node --check')

            # The packed data physically embedded in the standalone HTML must inflate to the readable snapshot.
            js_inflated=node_json([HERE/'js_inflate_harness.js',html_path])
            d=semantic_diff(master,js_inflated)
            if d: fail(f'HTML bundled packed snapshot drift: {d[:3]}')
            checks.append('Packed snapshot embedded in HTML ↔ readable normalized JSON: exact')

            # Browser JS materializer vs Python, randomized progression.
            rng=random.Random(2200)
            material_cases=[]
            for _ in range(400):
                c=rng.choice(master['cards'])
                material_cases.append({'id':c['id'],'level':rng.randint(1,c['maxLevel']),'bloom':rng.randint(0,5)})
            cases_path=td/'matcases.json'; cases_path.write_text(json.dumps(material_cases),encoding='utf-8')
            js_mat=node_json([HERE/'js_materialize_harness.js',html_path,snapshot_path,cases_path])
            for q,j in zip(material_cases,js_mat):
                c=next(c for c in master['cards'] if c['id']==q['id'])
                p=materialize_card(c,q['level'],q['bloom'])
                d=semantic_diff(p,j)
                if d: fail(f'Python/JS materialize drift {q}: {d[:3]}')
            checks.append(f'Python ↔ browser materialization: {len(material_cases)} randomized cases exact')

            # Python reference scorer vs production JS worker at varied progression/song/model settings.
            rng=random.Random(2201)
            progress={}
            for c in master['cards']:
                progress[c['id']]={'level':rng.randint(1,c['maxLevel']),'bloom':rng.randint(0,5)}
            varied=materialize_master(master,progress); by={c['id']:c for c in varied}
            score_cases=[]
            for _ in range(120):
                while True:
                    team=rng.sample(varied,5)
                    if len({c['characterId'] for c in team})==5: break
                outfit=rng.choice(varied)
                score_cases.append({'cardIds':[c['id'] for c in team],'outfitId':outfit['id'],'song':rng.choice([75,90,120,140,180,240,300]),'specialMode':rng.choice(['off','neutral','combo']),'other':rng.choice([0,2.5,7,12.25])})
            cards_path=td/'varied_cards.json'; cards_path.write_text(json.dumps(varied),encoding='utf-8')
            sc_path=td/'scorecases.json'; sc_path.write_text(json.dumps(score_cases),encoding='utf-8')
            js_results=node_json([HERE/'js_worker_reference_harness.js',worker_path,cards_path,sc_path])
            numeric_fields=['score','stat','raw','uplift','sarUplift','supported','coverage','specialBonus','totalBonus','outfitSupport']
            max_abs=0.0
            for idx,(q,j) in enumerate(zip(score_cases,js_results)):
                p=evaluate_order([by[x] for x in q['cardIds']],all_cards=varied,song=q['song'],special_mode=q['specialMode'],other=q['other'],outfit_mode='fixed',outfit_id=q['outfitId'],details=True)
                for field in numeric_fields:
                    max_abs=max(max_abs,abs(float(p[field])-float(j[field])))
                    if not numeric_close(p[field],j[field]): fail(f'Python/JS scorer drift case {idx} field {field}: {p[field]} vs {j[field]}')
                if p['cardIds'] != j['cardIds'] or p['outfitCard'] != j['outfitCard']:
                    fail(f'Python/JS identity drift case {idx}')
            checks.append(f'Python reference ↔ JS scorer: {len(score_cases)} randomized cases pass (max abs numeric drift {max_abs:.3g})')

            if args.raw:
                raw,version=load_raw(args.raw)
                py_master=validate_master(normalize_master(raw,version))
                d=semantic_diff(py_master,master)
                if d: fail(f'raw→Python snapshot differs from bundled release: {d[:3]}')
                raw_path=td/'raw.json'; raw_path.write_text(json.dumps(raw),encoding='utf-8')
                js_master=node_json([HERE/'js_normalize_harness.js',html_path,raw_path,version])
                d=semantic_diff(py_master,js_master)
                if d: fail(f'Python/browser normalization drift: {d[:3]}')
                checks.append('Raw DB → Python normalizer → bundled snapshot: exact')
                checks.append('Raw DB → browser compatibility normalizer vs Python: exact')

            if args.search_regression:
                fixture=json.loads((HERE/'expected_exact14.json').read_text(encoding='utf-8'))
                max_by={c['id']:c for c in mat}
                pool=[max_by[x] for x in fixture['poolCardIds']]
                pool_path=td/'pool14.json'; pool_path.write_text(json.dumps(pool),encoding='utf-8')
                params_path=td/'params.json'; params_path.write_text(json.dumps(fixture['params']),encoding='utf-8')
                result=node_json([HERE/'js_search_harness.js',worker_path,pool_path,params_path])
                if result.get('type')!='done': fail(f'search regression error: {result}')
                actual=result['results'][:10]
                for i,(a,e) in enumerate(zip(actual,fixture['expectedTop10'])):
                    if set(a['cardIds'])!=set(e['cardIds']) or a['outfitCard']!=e['outfitCard'] or not numeric_close(a['score'],e['score'],rel=1e-12,abs_tol=1e-8):
                        fail(f'exact14 Top 10 regression mismatch at rank {i+1}')
                checks.append(f'14-card exact baseline: Top 10/10 match v2.0.2 exhaustive baseline ({result["elapsedMs"]} ms)')

            if args.large_search:
                # The stress test validates scaling behavior, not optimality proof.
                params={'searchMode':'global','anchor':None,'cardPool':'all','searchQuality':'fast','outfitMode':'best','outfitKey':None,'song':140,'specialMode':'combo','other':0,'topN':5,'fullOrder':True,'excluded':[],'ownedOnly':False,'ownedKeys':[]}
                full_path=td/'full.json'; full_path.write_text(json.dumps(mat),encoding='utf-8')
                pp=td/'largeparams.json'; pp.write_text(json.dumps(params),encoding='utf-8')
                result=node_json([HERE/'js_search_harness.js',worker_path,full_path,pp])
                if result.get('type')!='done' or not result.get('results'): fail(f'large search failed: {result}')
                stats=result.get('searchStats',{})
                if stats.get('rawValid') != 893166556: fail(f'unexpected all-rarity raw space: {stats.get("rawValid")}')
                if stats.get('completeScreened',10**12) >= stats['rawValid']: fail('large search unexpectedly enumerated raw space')
                checks.append(f'All-rarity Fast stress: raw {stats["rawValid"]:,}, screened {stats.get("completeScreened",0):,}, partial {stats.get("partialEvaluated",0):,}, {result["elapsedMs"]/1000:.2f}s')
    else:
        checks.append('Node.js unavailable: cross-language and JS syntax tests skipped')

    # No unresolved build placeholders.
    h=html_path.read_text(encoding='utf-8')
    for marker in ('__WORKER_TEMPLATE__','__BUNDLED_PACKED__','__BUILD_INFO__'):
        if marker in h: fail(f'unresolved HTML placeholder {marker}')
    checks.append('Release HTML contains no unresolved build placeholders')

    print('QC PASS')
    for c in checks: print(' -',c)

if __name__=='__main__':
    main()
