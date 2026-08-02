from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent; SRC=ROOT/'src'; RR=SRC/'roster_recognizer'
out=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'dist'/'Holodori_Optimizer_v3.8.13.html'
template=(SRC/'template.html').read_text(encoding='utf-8'); styles=(SRC/'styles.css').read_text(encoding='utf-8'); app=(SRC/'app.js.in').read_text(encoding='utf-8'); search_worker=(SRC/'search_worker.js').read_text(encoding='utf-8'); importer=(SRC/'roster_importer.js.in').read_text(encoding='utf-8')
app=app.replace('__WORKER_TEMPLATE_JSON__',json.dumps(search_worker,separators=(',',':')))
repls={
'__ROSTER_RECOGNIZER_WORKER_JSON__':json.dumps((RR/'worker.js').read_text(encoding='utf-8'),separators=(',',':')),
'__ROSTER_CARDS_TEXT_JSON__':json.dumps((RR/'cards.json').read_text(encoding='utf-8'),separators=(',',':')),
'__ROSTER_REFERENCES_TEXT_JSON__':json.dumps((RR/'references.json').read_text(encoding='utf-8'),separators=(',',':')),
'__ROSTER_DIGITS_TEXT_JSON__':json.dumps((RR/'digit_templates.json').read_text(encoding='utf-8'),separators=(',',':')),
}
for k,v in repls.items(): importer=importer.replace(k,v)
# Initialize after the optimizer's normal bootstrap and event bindings exist.
app += '\n'+importer+'\nqueueMicrotask(initializeRosterImporter);\n'
html=template.replace('__INLINE_STYLES__',styles).replace('__APP_SCRIPT__',app)
out.parent.mkdir(parents=True,exist_ok=True); out.write_text(html,encoding='utf-8'); print(out)
