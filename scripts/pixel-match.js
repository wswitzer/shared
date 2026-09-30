const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('/Users/trust/.npm/_npx/e41f203b7505f1fb/node_modules/playwright');

const ROOT_DIR = path.resolve(__dirname, '..');
const PORT = 3456;
const REFERENCE_PATH = path.join(ROOT_DIR, 'chris-gaca/mockups/reference/living-archive-target.png');
const ITERATION = process.argv[2] || '01';
const OUT_DIR = path.join(ROOT_DIR, 'tmp');

if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
};

const server = http.createServer((req, res) => {
  let reqPath = decodeURI(req.url.split('?')[0]);
  if (reqPath === '/') reqPath = '/chris-gaca/mockups/index.html';
  const filePath = path.join(ROOT_DIR, reqPath);

  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not found');
    return;
  }

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';
  res.writeHead(200, { 'Content-Type': contentType });
  fs.createReadStream(filePath).pipe(res);
});

server.listen(PORT, async () => {
  console.log(`Static server running on http://localhost:${PORT}`);
  
  try {
    const browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--font-render-hinting=none', '--force-color-profile=srgb']
    });

    const context = await browser.newContext({
      viewport: { width: 1122, height: 1367 },
      deviceScaleFactor: 1
    });

    const page = await context.newPage();
    
    console.log('Navigating to mockup...');
    await page.goto(`http://localhost:${PORT}/chris-gaca/mockups/index.html`, { waitUntil: 'networkidle' });

    await page.evaluate(async () => {
      await document.fonts.ready;
      const images = Array.from(document.querySelectorAll('img'));
      await Promise.all(images.map(img => {
        if (img.complete) return Promise.resolve();
        return new Promise((resolve) => {
          img.onload = resolve;
          img.onerror = resolve;
        });
      }));
    });

    await page.waitForTimeout(500);

    const domBounds = await page.evaluate(() => {
      function b(sel) {
        const el = document.querySelector(sel);
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
      }
      function all(sel) {
        return Array.from(document.querySelectorAll(sel)).map(el => {
          const r = el.getBoundingClientRect();
          return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
        });
      }
      return {
        topbar: b('.topbar'),
        logo: b('.logo-img'),
        brand: b('.brand-wrap .brand'),
        nav: b('.nav'),
        search: b('.search'),
        hero: b('.hero'),
        heroH1: b('.hero h1'),
        heroP: b('.hero p'),
        heroCta: b('.cta'),
        heroStats: b('.hero-stats'),
        featuredHead: b('.section-featured .section-head'),
        featuredCards: b('.section-featured .cards-4'),
        cardImgs: all('.cards-4 .card-img-wrap img'),
        card1: b('.song-card'),
        card1Img: b('.song-card .card-img-wrap'),
        card1Eyebrow: b('.song-card .eyebrow'),
        card1H3: b('.song-card h3'),
        card1P: b('.song-card p'),
        card1Meta: b('.song-card .meta'),
        regionsHead: b('.section-regions .section-head'),
        regionsCards: b('.cards-6.regions'),
        regionImgs: all('.cards-6.regions img'),
        bottomGrid: b('.bottom-grid'),
        langHead: b('.bottom-left .section-head'),
        langGrid: b('.language-grid'),
        langIcons: all('.lang-icon'),
        collHead: b('.bottom-right .section-head'),
        collCards: b('.cards-3.collections'),
        collImgs: all('.cards-3.collections img'),
        footer: b('.footer'),
        quote: b('.quote')
      };
    });
    console.log('Mockup DOM Rects:\n', JSON.stringify(domBounds, null, 2));

    const shotPath = path.join(OUT_DIR, `chris-match-${ITERATION}.png`);
    await page.screenshot({ path: shotPath, fullPage: true });
    console.log(`Saved screenshot to ${shotPath}`);

    if (fs.existsSync(REFERENCE_PATH)) {
      const refBase64 = fs.readFileSync(REFERENCE_PATH).toString('base64');
      const shotBase64 = fs.readFileSync(shotPath).toString('base64');

      const diffResult = await page.evaluate(async ({ refB64, shotB64 }) => {
        const loadImage = (b64) => new Promise((resolve, reject) => {
          const img = new Image();
          img.onload = () => resolve(img);
          img.onerror = reject;
          img.src = 'data:image/png;base64,' + b64;
        });

        const [refImg, shotImg] = await Promise.all([loadImage(refB64), loadImage(shotB64)]);
        const width = Math.max(refImg.width, shotImg.width);
        const height = Math.max(refImg.height, shotImg.height);

        const canvasRef = document.createElement('canvas');
        canvasRef.width = width;
        canvasRef.height = height;
        const ctxRef = canvasRef.getContext('2d');
        ctxRef.drawImage(refImg, 0, 0);
        const refData = ctxRef.getImageData(0, 0, width, height).data;

        const canvasShot = document.createElement('canvas');
        canvasShot.width = width;
        canvasShot.height = height;
        const ctxShot = canvasShot.getContext('2d');
        ctxShot.drawImage(shotImg, 0, 0);
        const shotData = ctxShot.getImageData(0, 0, width, height).data;

        const canvasDiff = document.createElement('canvas');
        canvasDiff.width = width;
        canvasDiff.height = height;
        const ctxDiff = canvasDiff.getContext('2d');
        const diffImgData = ctxDiff.createImageData(width, height);
        const diffData = diffImgData.data;

        let diffPixels = 0;
        let totalDiffScore = 0;
        const totalPixels = width * height;

        for (let i = 0; i < refData.length; i += 4) {
          const r1 = refData[i], g1 = refData[i+1], b1 = refData[i+2], a1 = refData[i+3];
          const r2 = shotData[i], g2 = shotData[i+1], b2 = shotData[i+2], a2 = shotData[i+3];

          const dr = Math.abs(r1 - r2);
          const dg = Math.abs(g1 - g2);
          const db = Math.abs(b1 - b2);
          const da = Math.abs(a1 - a2);

          const pixelDiff = (dr + dg + db + da) / 4;
          totalDiffScore += pixelDiff;

          if (pixelDiff > 12) {
            diffPixels++;
            diffData[i] = 255;
            diffData[i+1] = 0;
            diffData[i+2] = 120;
            diffData[i+3] = 255;
          } else {
            diffData[i] = Math.round(r1 * 0.25);
            diffData[i+1] = Math.round(g1 * 0.25);
            diffData[i+2] = Math.round(b1 * 0.25);
            diffData[i+3] = 255;
          }
        }

        ctxDiff.putImageData(diffImgData, 0, 0);
        const diffB64 = canvasDiff.toDataURL('image/png').split(',')[1];

        return {
          width,
          height,
          refWidth: refImg.width,
          refHeight: refImg.height,
          shotWidth: shotImg.width,
          shotHeight: shotImg.height,
          totalPixels,
          diffPixels,
          diffPercent: ((diffPixels / totalPixels) * 100).toFixed(2),
          avgDiffScore: (totalDiffScore / totalPixels).toFixed(2),
          diffB64
        };
      }, { refB64: refBase64, shotB64: shotBase64 });

      const diffImgPath = path.join(OUT_DIR, `chris-diff-${ITERATION}.png`);
      fs.writeFileSync(diffImgPath, Buffer.from(diffResult.diffB64, 'base64'));

      console.log('--- Comparison Results ---');
      console.log(`Ref size:   ${diffResult.refWidth}x${diffResult.refHeight}`);
      console.log(`Shot size:  ${diffResult.shotWidth}x${diffResult.shotHeight}`);
      console.log(`Diff Pixels: ${diffResult.diffPixels} / ${diffResult.totalPixels} (${diffResult.diffPercent}%)`);
      console.log(`Avg Error:   ${diffResult.avgDiffScore} / 255`);
      console.log(`Diff Map:    ${diffImgPath}`);
    }

    await browser.close();
  } catch (err) {
    console.error('Error during pixel match run:', err);
  } finally {
    server.close();
  }
});
