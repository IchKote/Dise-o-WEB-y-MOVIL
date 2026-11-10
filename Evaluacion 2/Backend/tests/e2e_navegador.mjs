import fs from 'node:fs';
import { chromium } from 'playwright';

const B = 'http://127.0.0.1:8080';
// Por defecto no se guarda ninguna imagen: las capturas solo se toman si se pide con CAPTURAS=1
const OUT = process.env.OUT || 'docs/evidencias/capturas';
const CAPTURAR = process.env.CAPTURAS === '1';
if (CAPTURAR) fs.mkdirSync(OUT, { recursive: true });
const captura = async (page, archivo, opciones) => {
  if (CAPTURAR) await page.screenshot({ path: OUT + '/' + archivo, ...opciones });
};
const navegador = await chromium.launch({ args: ['--no-sandbox'] });
const page = await navegador.newPage();

// El sandbox no llega al CDN: se sirve la misma versión desde npm
await page.route(/cdn\.jsdelivr\.net\/npm\/(bootstrap|bootstrap-icons)@[^/]+\/(.+)/, route => {
  const m = route.request().url().match(/npm\/(bootstrap|bootstrap-icons)@[^/]+\/(.+)/);
  const f = `${process.env.CDN_LOCAL || 'node_modules'}/${m[1]}/${m[2]}`;
  if (fs.existsSync(f)) return route.fulfill({ body: fs.readFileSync(f), contentType: f.endsWith('.css') ? 'text/css' : 'application/javascript' });
  return route.fulfill({ status: 404, body: '' });
});
const dialogos = [];
const errores = []; const urls = [];
page.on('dialog', async d => { dialogos.push(d.message()); await d.accept(); });
page.on('response', r => { if (r.status() >= 400) urls.push(r.status() + ' ' + r.url()); });
page.on('pageerror', e => errores.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errores.push('console: ' + m.text()); });

const fallos = [];
const check = (n, c) => { console.log((c ? 'OK    ' : 'FALLA ') + n); if (!c) fallos.push(n); };
const correo = `nav${Date.now() % 100000}@correo.cl`;

// 1. XSS en el nombre
await page.goto(B + '/index.php');
await page.click('#navAuthItem button');
await page.click('text=¡Regístrate aquí!');
await page.fill('#authNombre', '<img src=x onerror=alert(1)>');
await page.fill('#authEmail', 'xss@correo.cl');
await page.fill('#authPass', 'clave12345');
await page.click('#btnAuthSubmit');
await page.waitForTimeout(800);
check('nombre con HTML rechazado por el servidor', dialogos.some(m => m.includes('nombre')));

// 2. Registro real
await page.fill('#authNombre', 'Cliente Navegador');
await page.fill('#authEmail', correo);
await page.fill('#authPass', 'clave12345');
await page.click('#btnAuthSubmit');
await page.waitForSelector('#navAuthItem .dropdown-toggle');
check('registro y sesión en navbar', (await page.textContent('#navAuthItem')).includes('Cliente Navegador'));
check('token en sessionStorage, no en localStorage', await page.evaluate(() => !!sessionStorage.getItem('usuario_sesion') && !localStorage.getItem('usuario_sesion')));

// 3. Carta -> carrito
await page.goto(B + '/carta.php');
await page.click('text=Chicken Tikka Masala');
await page.waitForSelector('#modalPersonalizar.show');
await page.evaluate(() => { cambiarCantidadModal('naanExtra', 1); document.getElementById('observaciones').value = 'Sin picante'; });
await page.evaluate(() => agregarAlCarroPersonalizado());
await page.waitForTimeout(300);

await page.goto(B + '/carrito.php');
await page.check('#delivery');
await page.fill('#direccion', 'Av. Providencia 123');
await page.fill('#codigoDescuento', 'MASALA20');
await page.click('text=Aplicar');
const totalLocal = await page.textContent('#lbl-total');
console.log('total mostrado en carrito:', totalLocal);

dialogos.length = 0;
await Promise.all([page.waitForURL('**/pedidos.php'), page.click('#btnPagar')]);
check('alerta de pedido confirmado', dialogos.some(m => m.includes('confirmado')));
await page.waitForSelector('#lista-pedidos .card');
const texto = await page.textContent('#lista-pedidos');
check('pedido PAGADO en Mis pedidos', texto.includes('PAGADO') && texto.includes('Chicken Tikka Masala') && texto.includes('Pan Naan Extra'));
check('pedidos.php muestra el comprobante unido por GraphQL', texto.includes('Pago APROBADO') && texto.includes('ref. pay_'));
await captura(page, 'pedidos-cliente.png', { fullPage: true });
check('total del servidor = (9.500 + 2.000) - 20% + envío 2.000 = 11.200', texto.includes('Total$11.200'));
console.log('pedido:', texto.replace(/\s+/g, ' ').slice(0, 230));
check('carrito vaciado', await page.evaluate(() => !localStorage.getItem('carrito_restaurante') || JSON.parse(localStorage.getItem('carrito_restaurante')).length === 0));

// 4. Pago rechazado conserva el carrito
await page.goto(B + '/carta.php');
await page.click('text=Samosas Vegetales');
await page.waitForSelector('#modalPersonalizar.show');
await page.evaluate(() => agregarAlCarroPersonalizado());
await page.goto(B + '/carrito.php');
await page.check('#simularRechazo');
dialogos.length = 0;
await page.click('#btnPagar');
await page.waitForTimeout(1500);
check('pago rechazado avisa y conserva carrito', dialogos.some(m => m.includes('rechazado')) && await page.evaluate(() => JSON.parse(localStorage.getItem('carrito_restaurante')).length === 1));

// 5. Cliente no entra al panel admin
await page.goto(B + '/admin.php');
await page.waitForTimeout(500);
check('cliente ve aviso de permisos', (await page.textContent('#aviso-admin')).includes('permisos'));

// 6. Admin
await page.evaluate(() => sessionStorage.clear());
await page.goto(B + '/index.php');
await page.click('#navAuthItem button');
await page.fill('#authEmail', 'admin@masala.cl');
await page.fill('#authPass', 'admin123');
await page.click('#btnAuthSubmit');
await page.waitForSelector('#navAuthItem .badge');
await page.goto(B + '/admin.php');
await page.waitForSelector('#lista-pedidos-admin .card');
const adminTxt = await page.textContent('#lista-pedidos-admin');
check('admin ve pedidos', adminTxt.includes('Chicken Tikka Masala'));
check('admin ve el cliente (campo restringido por GraphQL)', adminTxt.includes('Cliente Navegador'));
await captura(page, 'admin-pedidos.png', { fullPage: false });
await page.click('#lista-pedidos-admin >> text=Pasar a EN_PREPARACION');
await page.waitForTimeout(600);
check('admin avanza estado', (await page.textContent('#lista-pedidos-admin')).includes('EN_PREPARACION'));
await page.click('button:has-text("Productos e inventario")');
await page.waitForSelector('#tabla-productos tr');
check('admin ve inventario con stock', (await page.textContent('#tabla-productos')).includes('Pan Naan Extra'));

// 7. La carta refleja precio y disponibilidad del servidor
const tokenAdmin = await page.evaluate(() => JSON.parse(sessionStorage.getItem('usuario_sesion')).token);
const patch = (cuerpo) => page.request.patch('http://localhost:8000/api/products/pan-naan-ajo', { headers: { Authorization: 'Bearer ' + tokenAdmin }, data: cuerpo });
await patch({ precio: 2700, stock: 0 });
await page.goto(B + '/carta.php');
await page.waitForSelector('text=Agotado');
const cartaTxt = await page.textContent('body');
check('carta muestra precio del servidor ($2.700) y Agotado', cartaTxt.includes('$2.700') && cartaTxt.includes('Agotado'));
await patch({ precio: 2500, stock: 60 });
await page.goto(B + '/carta.php');
await page.waitForTimeout(800);
check('al reponer, la carta vuelve a permitir pedirlo', !(await page.textContent('body')).includes('Agotado'));

console.log('HTTP>=400:', [...new Set(urls)]);
console.log('\nerrores de consola:', errores.length ? errores : 'ninguno');
await navegador.close();
console.log(fallos.length ? 'FALLAS: ' + fallos.join(' | ') : 'TODO OK');
process.exit(fallos.length ? 1 : 0);
