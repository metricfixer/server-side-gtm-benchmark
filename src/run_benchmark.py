import argparse
import asyncio
import importlib.metadata
import platform
import sys
import json
import math
import os
import random
import statistics
import string
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from aiohttp import web
from PIL import Image
from playwright.async_api import async_playwright

from benchmark_core import sha256_file, write_json, write_medians_csv

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / 'artifacts' / 'latest'
RESULTS_PATH = OUTPUT_DIR / 'benchmark_raw.json'
SUMMARY_PATH = OUTPUT_DIR / 'benchmark_summary.json'
MEDIANS_PATH = OUTPUT_DIR / 'benchmark_medians.csv'
ENVIRONMENT_PATH = OUTPUT_DIR / 'run_environment.json'
MANIFEST_PATH = OUTPUT_DIR / 'run_manifest.json'
HERO_PATH = REPO_ROOT / 'fixtures' / 'benchmark_hero_fixture.jpg'
PORT = int(os.environ.get('SGTM_BENCHMARK_PORT', '8765'))
RUNS_PER_VARIANT = 15
SEED_BASE = 10_000
SHUFFLE = True
HEADLESS = True
BROWSER_EXECUTABLE = os.environ.get('CHROMIUM_EXECUTABLE')
VIEWPORT_WIDTH = 1365
VIEWPORT_HEIGHT = 900
NETWORK_LATENCY_MS = 150
DOWNLOAD_BPS = 1_600_000
UPLOAD_BPS = 750_000
CPU_SLOWDOWN = 4
SETTLE_MS = 2200
ALLOW_PARTIAL = False
VARIANTS = ['control', 'web_gtm', 'sgtm_proxy_only', 'sgtm_consolidated']

# Deliberately synthetic, deterministic payloads. They represent architectural
# browser cost, not any specific vendor's production bundle.
def make_padding(length: int, seed: int) -> str:
    rng = random.Random(seed)
    alphabet = string.ascii_letters + string.digits
    return ''.join(rng.choice(alphabet) for _ in range(length))

WEB_CONTAINER_PAD = make_padding(12_000, 1)
VENDOR_PAD = {
    i: make_padding(32_000, 100 + i) for i in range(1, 5)
}
DISPATCHER_PAD = make_padding(16_000, 2)

SERVER_LOG = defaultdict(lambda: {
    'browser_event_requests': 0,
    'logical_destination_deliveries': 0,
    'paths': [],
})


def ensure_hero():
    if HERO_PATH.exists():
        return
    width, height = 1280, 720
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    rng = random.Random(42)
    for y in range(height):
        for x in range(width):
            # Controlled textured gradient to avoid unrealistically tiny JPEG.
            base = int(35 + 145 * (x / width))
            noise = rng.randint(-22, 22)
            pixels[x, y] = (
                max(0, min(255, base + noise)),
                max(0, min(255, 80 + int(80 * y / height) + noise)),
                max(0, min(255, 155 + int(70 * (1 - y / height)) + noise)),
            )
    img.save(HERO_PATH, 'JPEG', quality=78, optimize=True)


PAGE_TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Metricfixer sGTM benchmark fixture</title>
<style>
:root { font-family: Arial, Helvetica, sans-serif; color: #111827; background: #f8fafc; }
* { box-sizing: border-box; }
body { margin: 0; }
header { min-height: 72px; display:flex; align-items:center; padding:0 6vw; background:#fff; border-bottom:1px solid #dbe3ed; }
.brand { font-size:20px; font-weight:700; }
main { width:min(1120px, 88vw); margin:34px auto 80px; }
.hero { position:relative; min-height:430px; border-radius:22px; overflow:hidden; background:#102a43; box-shadow:0 20px 50px rgba(15,23,42,.12); }
.hero img { width:100%; height:430px; object-fit:cover; display:block; }
.hero-copy { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:flex-end; padding:44px; color:#fff; background:linear-gradient(180deg, transparent 25%, rgba(0,0,0,.70)); }
.hero h1 { max-width:760px; margin:0 0 14px; font-size:48px; line-height:1.02; }
.hero p { max-width:680px; margin:0; font-size:20px; line-height:1.45; }
.cards { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:24px; }
.card { background:#fff; border:1px solid #dbe3ed; border-radius:16px; padding:24px; min-height:170px; }
.card h2 { font-size:20px; margin:0 0 10px; }
.card p { margin:0; line-height:1.55; color:#475569; }
button { margin-top:24px; padding:13px 20px; border:0; border-radius:10px; font-weight:700; background:#1558B1; color:#fff; }
@media (max-width:760px){ .cards{grid-template-columns:1fr}.hero h1{font-size:36px}.hero-copy{padding:28px} }
</style>
<script>
window.__mfPerf = { lcp: 0, cls: 0, longTasks: [], errors: [] };
try {
  new PerformanceObserver((list) => {
    const entries = list.getEntries();
    if (entries.length) window.__mfPerf.lcp = entries[entries.length - 1].startTime;
  }).observe({type:'largest-contentful-paint', buffered:true});
} catch(e) {}
try {
  new PerformanceObserver((list) => {
    for (const e of list.getEntries()) window.__mfPerf.longTasks.push({start:e.startTime, duration:e.duration});
  }).observe({type:'longtask', buffered:true});
} catch(e) {}
try {
  new PerformanceObserver((list) => {
    for (const e of list.getEntries()) if (!e.hadRecentInput) window.__mfPerf.cls += e.value;
  }).observe({type:'layout-shift', buffered:true});
} catch(e) {}
window.addEventListener('error', (e) => window.__mfPerf.errors.push(String(e.message || e.error || 'error')));
</script>
__TAG_BOOTSTRAP__
</head>
<body>
<header><div class="brand">metricfixer benchmark fixture</div></header>
<main>
<section class="hero">
  <img src="/assets/hero.jpg?rid=__RID__" width="1280" height="720" alt="Abstract analytics data flow illustration">
  <div class="hero-copy">
    <h1>Client-side tags versus a consolidated server-side event stream</h1>
    <p>The page content is identical in every run. Only the measurement architecture changes.</p>
  </div>
</section>
<section class="cards">
  <article class="card"><h2>Performance</h2><p>Network requests, JavaScript bytes, long tasks, load timing and LCP.</p></article>
  <article class="card"><h2>Delivery</h2><p>Browser requests and logical downstream destination deliveries.</p></article>
  <article class="card"><h2>Resilience</h2><p>What happens when the first hop, proxy, consent gate or browser script fails.</p></article>
</section>
<button id="cta">Test interaction</button>
</main>
<script>
window.__mfInteraction = { delay: null };
const b = document.getElementById('cta');
b.addEventListener('click', (e) => {
  const eventTime = e.timeStamp;
  requestAnimationFrame(() => { window.__mfInteraction.delay = performance.now() - eventTime; });
});
</script>
</body>
</html>'''


def js_response(text: str):
    return web.Response(text=text, content_type='application/javascript', headers={
        'Cache-Control': 'no-store',
        'Timing-Allow-Origin': '*',
    })


async def page_handler(request: web.Request):
    variant = request.query.get('variant', 'control')
    rid = request.query.get('rid', 'unknown')
    if variant == 'control':
        bootstrap = ''
    elif variant in ('web_gtm', 'sgtm_proxy_only'):
        mode = 'direct' if variant == 'web_gtm' else 'proxy'
        bootstrap = f'<script async src="/assets/web-container.js?rid={rid}&amp;mode={mode}"></script>'
    elif variant == 'sgtm_consolidated':
        bootstrap = f'<script async src="/assets/dispatcher.js?rid={rid}"></script>'
    else:
        raise web.HTTPBadRequest(text='Unknown variant')
    html = PAGE_TEMPLATE.replace('__TAG_BOOTSTRAP__', bootstrap).replace('__RID__', rid)
    return web.Response(text=html, content_type='text/html', headers={'Cache-Control': 'no-store'})


async def hero_handler(request: web.Request):
    # Small server delay simulates an origin/static-asset fetch.
    await asyncio.sleep(0.035)
    return web.FileResponse(HERO_PATH, headers={'Cache-Control': 'no-store', 'Timing-Allow-Origin': '*'})


async def web_container_handler(request: web.Request):
    rid = request.query.get('rid', '')
    mode = request.query.get('mode', 'direct')
    code = f'''const __containerPad="{WEB_CONTAINER_PAD}";
(function(){{
  let z=0; for(let i=0;i<650000;i++){{ z += Math.sqrt((i%997)+1); }}
  for(let vendor=1; vendor<=4; vendor++){{
    const s=document.createElement('script');
    s.async=true;
    s.src='/assets/vendor.js?rid={rid}&mode={mode}&vendor='+vendor;
    document.head.appendChild(s);
  }}
  window.__mfContainerChecksum=z+__containerPad.length;
}})();'''
    await asyncio.sleep(0.025)
    return js_response(code)


async def vendor_handler(request: web.Request):
    rid = request.query.get('rid', '')
    mode = request.query.get('mode', 'direct')
    vendor = int(request.query.get('vendor', '1'))
    endpoint = '/third-party/collect' if mode == 'direct' else '/collect/proxy'
    pad = VENDOR_PAD.get(vendor, VENDOR_PAD[1])
    code = f'''const __vendorPad{vendor}="{pad}";
(function(){{
  let z=0; for(let i=0;i<1650000;i++){{ z += Math.sin((i%360)*0.0174533) * Math.cos((i%180)*0.0174533); }}
  const payload=JSON.stringify({{event:'benchmark_view',vendor:{vendor},rid:'{rid}',checksum:z+__vendorPad{vendor}.length}});
  if(navigator.sendBeacon){{ navigator.sendBeacon('{endpoint}?rid={rid}&vendor={vendor}', payload); }}
  else {{ fetch('{endpoint}?rid={rid}&vendor={vendor}', {{method:'POST',body:payload,keepalive:true,headers:{{'Content-Type':'text/plain'}}}}); }}
}})();'''
    await asyncio.sleep(0.03 + vendor * 0.004)
    return js_response(code)


async def dispatcher_handler(request: web.Request):
    rid = request.query.get('rid', '')
    code = f'''const __dispatcherPad="{DISPATCHER_PAD}";
(function(){{
  let z=0; for(let i=0;i<850000;i++){{ z += Math.sqrt((i%1237)+1); }}
  const payload=JSON.stringify({{event:'benchmark_view',rid:'{rid}',destinations:['analytics','ads','crm','affiliate'],checksum:z+__dispatcherPad.length}});
  if(navigator.sendBeacon){{ navigator.sendBeacon('/collect/sgtm?rid={rid}', payload); }}
  else {{ fetch('/collect/sgtm?rid={rid}', {{method:'POST',body:payload,keepalive:true,headers:{{'Content-Type':'text/plain'}}}}); }}
}})();'''
    await asyncio.sleep(0.025)
    return js_response(code)


async def collect_handler(request: web.Request):
    rid = request.query.get('rid', 'unknown')
    path = request.path
    await request.read()
    SERVER_LOG[rid]['browser_event_requests'] += 1
    SERVER_LOG[rid]['paths'].append(path)
    if path == '/collect/sgtm':
        SERVER_LOG[rid]['logical_destination_deliveries'] += 4
        # Server-side fan-out is intentionally off the browser critical path.
        await asyncio.sleep(0.025)
    else:
        SERVER_LOG[rid]['logical_destination_deliveries'] += 1
        await asyncio.sleep(0.018)
    return web.Response(status=204, headers={'Cache-Control': 'no-store'})


async def health_handler(request: web.Request):
    return web.json_response({'ok': True})


def build_app():
    app = web.Application()
    app.router.add_get('/health', health_handler)
    app.router.add_get('/page', page_handler)
    app.router.add_get('/assets/hero.jpg', hero_handler)
    app.router.add_get('/assets/web-container.js', web_container_handler)
    app.router.add_get('/assets/vendor.js', vendor_handler)
    app.router.add_get('/assets/dispatcher.js', dispatcher_handler)
    app.router.add_post('/third-party/collect', collect_handler)
    app.router.add_post('/collect/proxy', collect_handler)
    app.router.add_post('/collect/sgtm', collect_handler)
    return app


async def run_once(browser, variant: str, iteration: int):
    rid = f'{variant}-{iteration}-{uuid.uuid4().hex[:8]}'
    context = await browser.new_context(
        viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
        device_scale_factor=1,
        ignore_https_errors=True,
    )
    page = await context.new_page()
    cdp = await context.new_cdp_session(page)
    await cdp.send('Network.enable')
    await cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    await cdp.send('Network.emulateNetworkConditions', {
        'offline': False,
        'latency': NETWORK_LATENCY_MS,
        'downloadThroughput': DOWNLOAD_BPS / 8,
        'uploadThroughput': UPLOAD_BPS / 8,
        'connectionType': 'cellular3g',
    })
    await cdp.send('Emulation.setCPUThrottlingRate', {'rate': CPU_SLOWDOWN})

    reqs = {}
    failed = []

    def on_request(params):
        reqs[params['requestId']] = {
            'url': params['request']['url'],
            'method': params['request']['method'],
            'type': params.get('type', ''),
            'encoded': 0,
            'failed': False,
        }

    def on_finished(params):
        if params['requestId'] in reqs:
            reqs[params['requestId']]['encoded'] = params.get('encodedDataLength', 0)

    def on_failed(params):
        if params['requestId'] in reqs:
            reqs[params['requestId']]['failed'] = True
        failed.append(params)

    cdp.on('Network.requestWillBeSent', on_request)
    cdp.on('Network.loadingFinished', on_finished)
    cdp.on('Network.loadingFailed', on_failed)

    url = f'http://127.0.0.1:{PORT}/page?variant={variant}&rid={rid}&nonce={uuid.uuid4().hex}'
    started = time.monotonic()
    await page.goto(url, wait_until='load', timeout=45_000)
    # Allow async tags, beacons, LCP finalization and long-task observation to settle.
    await page.wait_for_timeout(SETTLE_MS)
    # Trigger one interaction after tags have executed. This is mainly a sanity check.
    await page.click('#cta')
    await page.wait_for_timeout(150)
    wall_ms = (time.monotonic() - started) * 1000

    perf = await page.evaluate('''() => {
      const n = performance.getEntriesByType('navigation')[0];
      const lt = window.__mfPerf.longTasks || [];
      return {
        dcl: n ? n.domContentLoadedEventEnd : null,
        load: n ? n.loadEventEnd : null,
        responseEnd: n ? n.responseEnd : null,
        lcp: window.__mfPerf.lcp || null,
        cls: window.__mfPerf.cls || 0,
        longTaskCount: lt.length,
        longTaskDuration: lt.reduce((a,b) => a+b.duration, 0),
        tbt: lt.reduce((a,b) => a+Math.max(0,b.duration-50), 0),
        interactionDelay: window.__mfInteraction.delay,
        errors: window.__mfPerf.errors || [],
        resourceEntries: performance.getEntriesByType('resource').map(r => ({name:r.name, transferSize:r.transferSize, encodedBodySize:r.encodedBodySize, duration:r.duration, initiatorType:r.initiatorType}))
      };
    }''')

    local_reqs = [r for r in reqs.values() if r['url'].startswith(f'http://127.0.0.1:{PORT}/')]
    js_reqs = [r for r in local_reqs if '/assets/' in r['url'] and '.js' in r['url']]
    event_reqs = [r for r in local_reqs if any(p in r['url'] for p in ['/third-party/collect', '/collect/proxy', '/collect/sgtm'])]

    # Beacons can finish just after JS settles; give server log a brief chance to catch up.
    for _ in range(20):
        expected = 0 if variant == 'control' else (1 if variant == 'sgtm_consolidated' else 4)
        if SERVER_LOG[rid]['browser_event_requests'] >= expected:
            break
        await asyncio.sleep(0.025)

    result = {
        'variant': variant,
        'iteration': iteration,
        'rid': rid,
        'wall_ms': wall_ms,
        **perf,
        'request_count': len(local_reqs),
        'failed_request_count': sum(1 for r in local_reqs if r['failed']),
        'transfer_bytes': sum(r['encoded'] for r in local_reqs),
        'js_request_count': len(js_reqs),
        'js_transfer_bytes': sum(r['encoded'] for r in js_reqs),
        'browser_event_request_count_cdp': len(event_reqs),
        'server_browser_event_requests': SERVER_LOG[rid]['browser_event_requests'],
        'logical_destination_deliveries': SERVER_LOG[rid]['logical_destination_deliveries'],
        'server_event_paths': SERVER_LOG[rid]['paths'],
    }
    await context.close()
    return result


def percentile(values, p):
    if not values:
        return None
    s = sorted(values)
    k = (len(s) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c-k) + s[c] * (k-f)


def summarize(results):
    numeric_fields = [
        'dcl', 'load', 'responseEnd', 'lcp', 'cls', 'longTaskCount',
        'longTaskDuration', 'tbt', 'interactionDelay', 'wall_ms',
        'request_count', 'transfer_bytes', 'js_request_count',
        'js_transfer_bytes', 'server_browser_event_requests',
        'logical_destination_deliveries',
    ]
    out = {'runs_per_variant': RUNS_PER_VARIANT, 'variants': {}}
    for variant in VARIANTS:
        rows = [r for r in results if r['variant'] == variant]
        v = {'n': len(rows)}
        for field in numeric_fields:
            vals = [float(r[field]) for r in rows if r.get(field) is not None]
            v[field] = {
                'median': statistics.median(vals) if vals else None,
                'p75': percentile(vals, .75) if vals else None,
                'min': min(vals) if vals else None,
                'max': max(vals) if vals else None,
            }
        v['errors'] = sum(len(r.get('errors', [])) for r in rows)
        v['failed_requests'] = sum(r.get('failed_request_count', 0) for r in rows)
        out['variants'][variant] = v

    # Relative medians make the architectural conclusion explicit.
    base = out['variants']['web_gtm']
    cons = out['variants']['sgtm_consolidated']
    proxy = out['variants']['sgtm_proxy_only']
    comparisons = {}
    for field in ['request_count', 'js_transfer_bytes', 'lcp', 'load', 'longTaskDuration', 'tbt']:
        b = base[field]['median']
        c = cons[field]['median']
        p = proxy[field]['median']
        comparisons[field] = {
            'consolidated_vs_web_pct': ((c - b) / b * 100) if b else None,
            'proxy_vs_web_pct': ((p - b) / b * 100) if b else None,
        }
    out['comparisons'] = comparisons
    return out


async def main(args):
    global OUTPUT_DIR, RESULTS_PATH, SUMMARY_PATH, MEDIANS_PATH, ENVIRONMENT_PATH, MANIFEST_PATH
    global HERO_PATH, PORT, RUNS_PER_VARIANT, SEED_BASE, SHUFFLE, HEADLESS
    global BROWSER_EXECUTABLE, VIEWPORT_WIDTH, VIEWPORT_HEIGHT
    global NETWORK_LATENCY_MS, DOWNLOAD_BPS, UPLOAD_BPS, CPU_SLOWDOWN, SETTLE_MS, ALLOW_PARTIAL

    OUTPUT_DIR = args.output_dir.resolve()
    RESULTS_PATH = OUTPUT_DIR / 'benchmark_raw.json'
    SUMMARY_PATH = OUTPUT_DIR / 'benchmark_summary.json'
    MEDIANS_PATH = OUTPUT_DIR / 'benchmark_medians.csv'
    ENVIRONMENT_PATH = OUTPUT_DIR / 'run_environment.json'
    MANIFEST_PATH = OUTPUT_DIR / 'run_manifest.json'
    HERO_PATH = args.fixture.resolve()
    PORT = args.port
    RUNS_PER_VARIANT = args.runs_per_variant
    SEED_BASE = args.seed_base
    SHUFFLE = not args.no_shuffle
    HEADLESS = not args.headed
    BROWSER_EXECUTABLE = args.browser_executable
    VIEWPORT_WIDTH = args.viewport_width
    VIEWPORT_HEIGHT = args.viewport_height
    NETWORK_LATENCY_MS = args.network_latency_ms
    DOWNLOAD_BPS = args.download_bps
    UPLOAD_BPS = args.upload_bps
    CPU_SLOWDOWN = args.cpu_slowdown
    SETTLE_MS = args.settle_ms
    ALLOW_PARTIAL = args.allow_partial

    if RUNS_PER_VARIANT < 1:
        raise ValueError('runs-per-variant must be at least 1')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_hero()
    runner = web.AppRunner(build_app())
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', PORT)
    await site.start()

    results = []
    run_errors = []
    order = []
    for i in range(1, RUNS_PER_VARIANT + 1):
        round_variants = VARIANTS.copy()
        if SHUFFLE:
            random.Random(SEED_BASE + i).shuffle(round_variants)
        for variant in round_variants:
            order.append((variant, i))

    started_at = datetime.now(timezone.utc)
    browser_version = None
    async with async_playwright() as p:
        launch_options = {
            'headless': HEADLESS,
            'args': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-sync',
                '--metrics-recording-only',
                '--mute-audio',
            ],
        }
        if BROWSER_EXECUTABLE:
            launch_options['executable_path'] = BROWSER_EXECUTABLE
        browser = await p.chromium.launch(**launch_options)
        browser_version = browser.version
        for idx, (variant, iteration) in enumerate(order, start=1):
            try:
                result = await run_once(browser, variant, iteration)
                results.append(result)
                print(f'[{idx:02d}/{len(order)}] {variant} run {iteration}: LCP={result["lcp"]:.0f}ms, load={result["load"]:.0f}ms, requests={result["request_count"]}, JS={result["js_transfer_bytes"]/1024:.1f}KB, TBT={result["tbt"]:.0f}ms, deliveries={result["logical_destination_deliveries"]}', flush=True)
            except Exception as exc:
                run_errors.append({'variant': variant, 'iteration': iteration, 'error': repr(exc)})
                print(f'ERROR {variant} run {iteration}: {exc!r}', flush=True)
        await browser.close()

    await runner.cleanup()
    if run_errors:
        write_json(OUTPUT_DIR / 'benchmark_errors.json', run_errors)
        if not ALLOW_PARTIAL:
            raise RuntimeError(f'{len(run_errors)} of {len(order)} benchmark runs failed; see benchmark_errors.json')
    write_json(RESULTS_PATH, results)
    summary = summarize(results)
    write_json(SUMMARY_PATH, summary)
    write_medians_csv(MEDIANS_PATH, summary)

    finished_at = datetime.now(timezone.utc)
    def package_version(name):
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            return None

    environment = {
        'recorded_at': finished_at.isoformat(),
        'python': sys.version,
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'packages': {
            'aiohttp': package_version('aiohttp'),
            'Pillow': package_version('Pillow'),
            'playwright': package_version('playwright'),
        },
        'browser': {
            'engine': 'Chromium',
            'version': browser_version,
            'custom_executable': BROWSER_EXECUTABLE,
        },
    }
    write_json(ENVIRONMENT_PATH, environment)

    manifest = {
        'schema_version': '1.0',
        'benchmark_id': 'metricfixer-web-gtm-vs-sgtm',
        'runner_version': '1.0.0',
        'started_at': started_at.isoformat(),
        'finished_at': finished_at.isoformat(),
        'runs_per_variant': RUNS_PER_VARIANT,
        'total_attempted_runs': len(order),
        'total_successful_runs': len(results),
        'variants': VARIANTS,
        'randomization': {'enabled': SHUFFLE, 'seed_base': SEED_BASE},
        'viewport': {'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT, 'device_scale_factor': 1},
        'network': {
            'latency_ms': NETWORK_LATENCY_MS,
            'download_bps': DOWNLOAD_BPS,
            'upload_bps': UPLOAD_BPS,
        },
        'cpu_slowdown': CPU_SLOWDOWN,
        'cache_disabled': True,
        'synthetic_payloads': True,
        'live_vendor_endpoints': False,
        'fixture': {
            'path': str(HERO_PATH),
            'sha256': sha256_file(HERO_PATH),
        },
        'outputs': {
            RESULTS_PATH.name: sha256_file(RESULTS_PATH),
            SUMMARY_PATH.name: sha256_file(SUMMARY_PATH),
            MEDIANS_PATH.name: sha256_file(MEDIANS_PATH),
            ENVIRONMENT_PATH.name: sha256_file(ENVIRONMENT_PATH),
        },
    }
    write_json(MANIFEST_PATH, manifest)
    print('\nSUMMARY')
    print(json.dumps(summary, indent=2))


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run the Metricfixer synthetic web GTM vs server-side GTM benchmark.'
    )
    parser.add_argument('--output-dir', type=Path, default=REPO_ROOT / 'artifacts' / 'latest')
    parser.add_argument('--fixture', type=Path, default=REPO_ROOT / 'fixtures' / 'benchmark_hero_fixture.jpg')
    parser.add_argument('--runs-per-variant', type=int, default=15)
    parser.add_argument('--port', type=int, default=int(os.environ.get('SGTM_BENCHMARK_PORT', '8765')))
    parser.add_argument('--seed-base', type=int, default=10_000)
    parser.add_argument('--no-shuffle', action='store_true')
    parser.add_argument('--headed', action='store_true')
    parser.add_argument('--browser-executable', default=os.environ.get('CHROMIUM_EXECUTABLE'))
    parser.add_argument('--viewport-width', type=int, default=1365)
    parser.add_argument('--viewport-height', type=int, default=900)
    parser.add_argument('--network-latency-ms', type=int, default=150)
    parser.add_argument('--download-bps', type=int, default=1_600_000)
    parser.add_argument('--upload-bps', type=int, default=750_000)
    parser.add_argument('--cpu-slowdown', type=int, default=4)
    parser.add_argument('--settle-ms', type=int, default=2200)
    parser.add_argument('--allow-partial', action='store_true', help='Write partial output instead of failing when a run errors.')
    return parser.parse_args()


if __name__ == '__main__':
    asyncio.run(main(parse_args()))
