// Renders report/report.html to a PDF with the pre-installed Chromium. Usage: node render_pdf.js <html> <pdf>
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + require('path').resolve(process.argv[2]));
  await p.pdf({ path: process.argv[3], preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
