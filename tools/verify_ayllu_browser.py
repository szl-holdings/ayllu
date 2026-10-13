#!/usr/bin/env python3
"""Qualify three served AYLLU sources without starting the operational app.

All discovery responses are explicit local UNAVAILABLE fixtures. Operational
failure paints are checked with an in-memory helper stub; no action is sent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WIDTHS = (320, 390, 768, 1280, 1920)
ICON_SHA = "6e2b7d72a3af3d9602b79de41df0194ede6496a9661f057108ec224c0efc92e6"
UNAVAILABLE = {"ok": False, "error": "UNAVAILABLE: local presentation fixture; no operational app started"}


def run(output: Path) -> int:
    output.mkdir(parents=True, exist_ok=False)
    files = {route: (ROOT / f"ayllu/static/{name}.html").read_bytes()
             for route, name in (("/", "chamber"), ("/counsel", "counsel"), ("/psyche", "psyche"))}
    requests, writes, outside, errors = [], [], [], []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            requests.append(path)
            if path in files:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                body = files[path]
            else:
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                body = json.dumps(UNAVAILABLE).encode()
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            writes.append(self.path)
            self.send_error(405)

        do_PUT = do_POST
        do_PATCH = do_POST
        do_DELETE = do_POST

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    report = {"observed_at": datetime.now(timezone.utc).isoformat(),
              "scope": "LOCAL_SOURCE_PRESENTATION_ONLY_NO_OPERATIONAL_APP",
              "source_hashes": {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}, "cases": []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.environ.get("CHROME_PATH"),
                                    args=["--disable-dev-shm-usage", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for route, name in (("/", "chamber"), ("/counsel", "counsel"), ("/psyche", "psyche")):
            context = browser.new_context(reduced_motion="reduce")

            def intercept(request):
                if request.request.method != "GET":
                    writes.append(request.request.url)
                    request.abort()
                elif request.request.url.startswith(origin + "/"):
                    request.continue_()
                else:
                    outside.append(request.request.url)
                    request.abort()

            context.route("**/*", intercept)
            page = context.new_page()
            page.set_default_timeout(20000)
            page.on("pageerror", lambda e: errors.append(str(e)))
            rows = []
            for width in WIDTHS:
                page.set_viewport_size({"width": width, "height": 1000})
                page.goto(origin + route, wait_until="domcontentloaded")
                if name in ('chamber', 'counsel'):
                    page.wait_for_function("document.querySelector('#mode').textContent==='UNAVAILABLE'")
                else:
                    page.wait_for_function("document.querySelector('#graphmeta').textContent.startsWith('UNAVAILABLE')")
                page.keyboard.press('Tab')
                first = page.evaluate("document.activeElement.matches('.skip-link')")
                page.keyboard.press('Enter')
                skip = page.evaluate("document.activeElement.id==='main-content'")
                layout = page.evaluate("""() => {
                    const shown=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
                    const targets=[...document.querySelectorAll('button,select,textarea,summary,.links a,footer a,label.lock')].filter(shown);
                    return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
                      small:targets.filter(e=>e.getBoundingClientRect().height<43.5).map(e=>({id:e.id,tag:e.tagName,height:e.getBoundingClientRect().height})),
                      unlabeled:[...document.querySelectorAll('textarea')].filter(e=>!e.labels.length).map(e=>e.id),
                      panel:getComputedStyle(document.querySelector('.left,.card')).backgroundImage,
                      iconCount:document.querySelectorAll('header svg').length,
                      overflow:[...document.querySelectorAll('main,header,aside,.card,.brand,.links,.kpi,textarea,select,footer')].filter(e=>shown(e)&&e.getBoundingClientRect().right>innerWidth+1).map(e=>({tag:e.tagName,id:e.id,className:e.className,right:e.getBoundingClientRect().right})).slice(0,8)};
                }""")
                rows.append({'width': width, 'skip_first': first, 'skip_focus': skip, 'layout': layout})
                if width in (320, 1280):
                    page.evaluate('scrollTo(0,0)')
                    page.screenshot(path=str(output / f'{name}-{width}.png'), full_page=False)
            # Malformed source text must stay text, including quote/protocol cases.
            sink = page.evaluate("""name => {
                const text='<img src=x onerror="window.__injected=true"> & \\" <b>fixture</b>';
                if(name==='counsel'){
                  renderDocket({ok:true,federal_count:2,court_count:0,federal:[
                    {title:text,url:'javascript:window.__injected=true',agency:text},
                    {title:'safe fixture',url:'https://example.invalid/\\" onmouseover=\\"window.__injected=true',agency:'fixture'}]});
                  renderLeaders([{id:text,status:text,function:text}]);
                }else if(name==='chamber'){
                  renderEstate({consolidated:[{name:text,urls:['javascript:window.__injected=true']},{name:'safe fixture',urls:['https://example.invalid/\\" onmouseover=\\"window.__injected=true']}]},true);
                  renderOrgans({organs:[{id:'local',name:text,role:text,space:'javascript:window.__injected=true'}]},true);
                  renderTurns({rounds:[{persona:text,answer:text,stub:true}]},true);
                }else{renderHits({ranked:[{text,source:text,honesty:text,weight:1}]})}
                const areas=name==='counsel'?['docket','leaders']:name==='chamber'?['estate','organs','out']:['hits'];
                return {injected:!!window.__injected,
                  markup:areas.flatMap(id=>[...document.getElementById(id).querySelectorAll('img,script,[onerror],[onmouseover],a[href^="javascript:"]')]).length,
                  literal:areas.some(id=>document.getElementById(id).textContent.includes('<img')),
                  rejectedLink:name==='psyche'||document.querySelectorAll('.invalid-link').length>0,
                  safeLinks:areas.flatMap(id=>[...document.getElementById(id).querySelectorAll('a')]).every(a=>a.protocol==='https:'||a.protocol==='http:')};
            }""", name)
            extra = {}
            if name == 'chamber':
                page.evaluate("renderRoster([{name:'Alpha',quechua:'fixture',archetype:'layout'},{name:'Beta',quechua:'fixture',archetype:'layout'}],{mode:'software'})")
                page.locator('.seat').nth(1).focus()
                page.keyboard.press('Space')
                extra['seat_space_selects'] = page.evaluate("document.querySelector('#who').value==='Beta' && document.querySelectorAll('.seat[aria-pressed=true]').length===1")
                before = page.evaluate('rot')
                page.wait_for_timeout(150)
                extra['reduced_motion_stable'] = page.evaluate('rot') == before
            if name == 'psyche':
                page.locator('.metric-details summary').focus()
                page.keyboard.press('Space')
                extra['metrics_space_opens'] = page.locator('.metric-details').evaluate('e=>e.open')
                # Failure paints are invoked through an in-memory helper stub;
                # no fetch, POST, local effect or live action executes.
                extra['failed_actions'] = page.evaluate("""async () => {
                    const original=j; const out=[];
                    j=async()=>({ok:false,status:'network',data:{error:'LOCAL RESPONSE FIXTURE'}});
                    try{
                      for(const [id,target] of [['lockbtn','writeout'],['imprint','writeout'],['replay','writeout'],['recall','hits'],['compose','composeout'],['pulse','beatout'],['sense','beatout'],['graft','writeout']]){
                        await document.getElementById(id).onclick();
                        out.push({id,text:document.getElementById(target).textContent});
                      }
                      return out;
                    }finally{j=original}
                }""")
                extra['unobserved_counts'] = page.evaluate("document.querySelector('#k-occ').textContent==='—' && document.querySelector('#k-stored').textContent==='—'")
            deadline = page.evaluate("""async () => {
                const oldFetch=fetch,oldTimer=setTimeout;let aborted=false,delay=null;
                window.setTimeout=(fn,ms,...args)=>{delay=ms;return oldTimer(fn,ms===10000?1:ms,...args)};
                window.fetch=(_url,options)=>new Promise((_resolve,reject)=>{
                    options.signal.addEventListener('abort',()=>{aborted=true;reject(new DOMException('Local deadline fixture','AbortError'))},{once:true});
                });
                try{const result=await j('/api/local-layout-fixture');return {aborted,delay,ok:result.ok,status:result.status}}
                finally{window.fetch=oldFetch;window.setTimeout=oldTimer}
            }""")
            page.emulate_media(forced_colors='active')
            page.keyboard.press('Tab')
            page.locator('.skip-link').focus()
            forced = page.evaluate("""() => ({outline:getComputedStyle(document.activeElement).outlineWidth,
                image:getComputedStyle(document.querySelector('.left,.card')).backgroundImage,
                panel:getComputedStyle(document.querySelector('.left,.card')).backgroundColor})""")
            icon = re.search(rb'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600".*?</svg>', files[route], re.S)
            passed = icon is not None and hashlib.sha256(icon.group(0)+b'\n').hexdigest()==ICON_SHA
            passed = passed and all(r['skip_first'] and r['skip_focus'] and not r['layout']['small'] and not r['layout']['unlabeled'] and not r['layout']['overflow'] and r['layout']['scrollWidth']<=r['width']+1 and r['layout']['iconCount']==1 for r in rows)
            passed = passed and not sink['injected'] and sink['markup']==0 and sink['literal'] and sink['rejectedLink'] and sink['safeLinks']
            passed = passed and deadline['aborted'] and deadline['delay']==10000 and not deadline['ok'] and deadline['status']=='timeout' and forced['outline']=='3px' and forced['image']=='none'
            if name == 'chamber':
                passed = passed and extra['seat_space_selects'] and extra['reduced_motion_stable']
            if name == 'psyche':
                passed = passed and extra['metrics_space_opens'] and extra['unobserved_counts'] and all(r['text'].startswith('UNAVAILABLE') for r in extra['failed_actions'])
            report['cases'].append({'name':name,'passed':bool(passed),'widths':rows,'sink':sink,'deadline':deadline,'extra':extra,'forced_colors':forced})
            print(json.dumps({'name':name,'passed':bool(passed),'overflow':[r for r in rows if r['layout']['overflow'] or r['layout']['small']]}),flush=True)
            context.close()
        browser.close()
    server.shutdown()
    server.server_close()
    thread.join()
    report.update(page_errors=errors,attempted_writes=writes,blocked_external_requests=outside,requested_paths=sorted(set(requests)))
    report['passed']=all(r['passed'] for r in report['cases']) and not errors and not writes and not outside
    (output/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(run(parser.parse_args().output))
