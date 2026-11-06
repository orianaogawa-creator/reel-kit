// node cap.js <outdir> [frame,frame,...]  -> transparent PNG per frame of ov/index.html
const { chromium } = require('/opt/node-tools/node_modules/playwright-core');
const fs = require('fs');
(async () => {
  const out = process.argv[2]; fs.mkdirSync(out, { recursive: true });
  const list = process.argv[3] ? process.argv[3].split(',').map(Number) : [...Array(require(require('path').resolve(process.env.PROJ || '.', 'proj/edl.json')).reduce((a, p) => a + p.frames, 0)).keys()];
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + require('path').resolve(process.env.PROJ || '.', 'ov/index.html') + (process.env.LAYER ? '?layer=' + process.env.LAYER : ''));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  for (const n of list) {
    await p.evaluate(t => render(t), n / 30);
    await p.screenshot({ path: `${out}/${String(n).padStart(4, '0')}.png`, omitBackground: true });
  }
  await b.close();
})();
