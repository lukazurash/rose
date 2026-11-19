// Rose: the order form, the bouquet builder and its sketch. system.js checks the fields; this sends them.
const $ = (s, r = document) => r.querySelector(s);
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const touch = matchMedia('(pointer: coarse)').matches;

/* ------------------------------------------------------------ sending (orders and custom requests)
   The order is saved first, then WhatsApp opens with it filled in. On a desktop a tab is opened inside the
   click (later it would be blocked as a popup) and sent to WhatsApp once the shop has the order; on a phone
   the page itself goes to WhatsApp, which hands over to the app. */
function errorLine(el) {
  const id = (el.getAttribute('aria-describedby') || '').split(/\s+/).find(x => document.getElementById(x)?.classList.contains('field__error'));
  return id && document.getElementById(id);
}

function showErrors(form, errors) {
  const bad = [];
  for (const [name, msg] of Object.entries(errors)) {
    const el = form.elements[name];
    const field = el instanceof RadioNodeList ? el[0] : el;
    if (!field) continue;
    field.setAttribute('aria-invalid', 'true');
    const line = errorLine(field);
    if (line) { line.textContent = msg; line.hidden = false; }
    bad.push(field);
  }
  if (bad.length) bad[0].focus();
  return bad.length;
}

function payload(form) {
  const data = {};
  for (const [k, v] of new FormData(form)) {
    if (k === 'colors') (data.colors ||= []).push(v); else data[k] = v;
  }
  return data;
}

async function send(form, done) {
  const status = $('[data-form-status]', form);
  const button = $('[type="submit"]', form);
  const win = touch ? null : window.open('', '_blank');
  if (win) win.opener = null;
  const wait = setTimeout(() => { status.textContent = form.dataset.sending || '…'; }, 300);
  button.disabled = true; button.setAttribute('aria-busy', 'true');
  try {
    const res = await fetch(form.action, {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload(form)),
    });
    const data = await res.json().catch(() => ({}));
    clearTimeout(wait);
    if (!data.ok) {
      win?.close();
      const n = showErrors(form, data.errors || {});
      status.textContent = n ? (form.dataset.fix || '{n}').replace('{n}', n) : (form.dataset.failed || '');
      return;
    }
    status.textContent = data.message + ' ';
    const a = document.createElement('a');
    a.href = data.url; a.rel = 'noopener'; a.target = '_blank'; a.textContent = 'WhatsApp';
    status.append(a);
    done?.();
    if (win) win.location.href = data.url; else location.href = data.url;
  } catch {
    clearTimeout(wait);
    win?.close();
    status.textContent = form.dataset.failed || '';
  } finally {
    button.disabled = false; button.removeAttribute('aria-busy');
  }
}

function sender(form, done) {
  form.addEventListener('submit', e => {
    if (!form.checkValidity()) return;   // system.js shows the reasons under the fields
    e.preventDefault();
    send(form, done);
  });
}

/* ------------------------------------------------------------ the order form */
const order = $('#orderForm');
if (order) {
  const pick = $('#o-bouquet'), zone = $('#o-zone'), pic = $('#o-pic');
  const freeFrom = Number(order.dataset.freeFrom) || Infinity;
  const total = () => {
    const price = Number(pick.selectedOptions[0]?.dataset.price) || 0;
    const fee = price >= freeFrom ? 0 : Number(zone.selectedOptions[0]?.dataset.fee) || 0;
    $('#o-total').textContent = `${price + fee} ₾`;
    $('#o-fee').textContent = `(${price} ₾ + ${order.dataset.feeWord} ${fee ? `${fee} ₾` : order.dataset.free})`;
  };
  const showPhoto = () => {
    const o = pick.selectedOptions[0];
    if (!o || !pic || pic.getAttribute('srcset') === o.dataset.srcset) return;
    const swap = () => { pic.srcset = o.dataset.srcset; pic.alt = o.dataset.alt; pic.classList.remove('is-swapping'); };
    if (reduced) return swap();
    pic.classList.add('is-swapping');
    const next = new Image();
    next.sizes = pic.sizes; next.srcset = o.dataset.srcset;
    next.decode().catch(() => {}).then(swap);   // the new photograph shows only once it is ready: no blank frame
  };
  pick.addEventListener('change', () => { total(); showPhoto(); });
  zone.addEventListener('change', total);
  total();

  // a bouquet tile (or a nav card) on this page fills the form instead of reloading the page
  document.addEventListener('click', e => {
    const card = e.target.closest('[data-order]');
    if (!card || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    e.preventDefault();
    pick.value = card.dataset.order;
    pick.dispatchEvent(new Event('change'));
    history.replaceState(null, '', '#order');
    $('#order').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    pick.focus({ preventScroll: true });
  });

  sender(order, () => {
    const keep = pick.value;
    order.reset();
    pick.value = keep;
    total();
  });
}

/* ------------------------------------------------------------ the bouquet builder and its sketch */
const builder = $('#customForm');
if (builder) {
  const range = $('#c-budget'), out = $('#c-budget-out');
  const SVGNS = 'http://www.w3.org/2000/svg';
  // fill and darker heart per colour (violet is left out on purpose: blue stands in)
  const TONES = { pink: ['#f1a7b5', '#c75d77'], red: ['#c0283e', '#7c1424'], white: ['#f7f3ec', '#d9cdb8'],
                  peach: ['#f6c29b', '#d07f4a'], yellow: ['#f2cf4a', '#b8911a'], blue: ['#8fb4dc', '#4e77a8'] };
  const rnd = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const f = n => n.toFixed(1);

  // three drawn flowers: a rose (scalloped cup and a spiral), a ranunculus (layered rings), a daisy
  function flower(kind, r, rand) {
    const rot = rand() * Math.PI;
    if (kind === 0) {
      let d = '';
      for (let k = 0; k <= 5; k++) {
        const a = rot + k * Math.PI * 2 / 5, b = a - Math.PI / 5;
        const [x, y] = [Math.cos(a) * r * .86, Math.sin(a) * r * .86], [cx, cy] = [Math.cos(b) * r * 1.22, Math.sin(b) * r * 1.22];
        d += k ? ` Q${f(cx)} ${f(cy)} ${f(x)} ${f(y)}` : `M${f(x)} ${f(y)}`;
      }
      let s = '';
      for (let i = 0; i <= 26; i++) {
        const th = rot + i * .42, rr = r * .62 * (1 - i / 30);
        s += `${i ? 'L' : 'M'}${f(Math.cos(th) * rr)} ${f(Math.sin(th) * rr)}`;
      }
      return `<path class="petal" d="${d}Z"/><path class="inner" d="${s}"/>`;
    }
    if (kind === 1) {
      const ring = (rr, n, cls) => {
        let d = '';
        for (let k = 0; k <= n; k++) {
          const a = rot + k * Math.PI * 2 / n, b = a - Math.PI / n;
          d += k ? ` Q${f(Math.cos(b) * rr * 1.16)} ${f(Math.sin(b) * rr * 1.16)} ${f(Math.cos(a) * rr)} ${f(Math.sin(a) * rr)}`
                 : `M${f(Math.cos(a) * rr)} ${f(Math.sin(a) * rr)}`;
        }
        return `<path class="${cls}" d="${d}Z"/>`;
      };
      return ring(r, 8, 'petal') + ring(r * .66, 7, 'petal') + ring(r * .36, 6, 'heart');
    }
    let p = '';
    for (let k = 0; k < 11; k++) {
      const a = rot + k * Math.PI * 2 / 11;
      p += `<ellipse class="petal" cx="${f(Math.cos(a) * r * .55)}" cy="${f(Math.sin(a) * r * .55)}" rx="${f(r * .5)}" ry="${f(r * .2)}" transform="rotate(${f(a * 180 / Math.PI)} ${f(Math.cos(a) * r * .55)} ${f(Math.sin(a) * r * .55)})"/>`;
    }
    return p + `<circle class="heart" r="${f(r * .3)}"/>`;
  }

  const blooms = [], stems = $('#skStems'), leaves = $('#skLeaves'), layer = $('#skBlooms');
  const TIE = [200, 330];

  // eight leaves round the dome, shown as the bouquet grows
  for (let k = 0; k < 8; k++) {
    const a = Math.PI * (1.02 + k * .137), x = 200 + Math.cos(a) * 150, y = 222 + Math.sin(a) * 92;
    const flip = x < 200 ? 180 : 0;
    const g = document.createElementNS(SVGNS, 'g');
    g.setAttribute('transform', `translate(${f(x)} ${f(y)}) rotate(${f(a * 180 / Math.PI + 180 + flip / 6)})`);
    g.innerHTML = '<path d="M0 0 Q20 -15 46 0 Q20 15 0 0Z"/><path class="vein" d="M3 0 L42 0"/>';
    g.style.transition = reduced ? '' : 'opacity 400ms ease';
    leaves.append(g);
  }

  function place(i, n) {
    const spread = .62 + .38 * Math.min(1, (n - 5) / 18);
    const rr = Math.sqrt((i + .5) / n), th = i * 2.39996 + .6;
    return [200 + rr * 142 * spread * Math.cos(th), 170 + rr * 104 * spread * Math.sin(th) - (1 - rr) * 14];
  }

  let first = true, frame = 0;
  function draw() {
    frame = 0;
    const budget = Number(range.value);
    out.textContent = `${budget} ₾`;
    const picked = [...builder.querySelectorAll('input[name="colors"]:checked')].map(x => x.value);
    const cols = picked.length ? picked : ['pink', 'white', 'peach'];
    const n = Math.round(5 + (budget - 50) / 450 * 18);
    const size = 40 - (n - 5) * .7;
    let stemD = '';
    for (let i = 0; i < Math.max(n, blooms.length); i++) {
      if (i >= n) {   // the bouquet got smaller: these fold away
        const b = blooms[i];
        if (b && !b.leaving) {
          b.leaving = true;
          b.el.classList.add('is-new');
          setTimeout(() => { if (b.leaving) b.el.remove(); }, reduced ? 0 : 520);
        }
        continue;
      }
      let b = blooms[i];
      if (!b || b.leaving) {
        if (b) b.el.remove();
        const rand = rnd(i * 97 + 13);
        const el = document.createElementNS(SVGNS, 'g');
        el.setAttribute('class', 'sk-bloom' + (first || reduced ? '' : ' is-new'));
        const inner = document.createElementNS(SVGNS, 'g');
        el.append(inner);
        layer.prepend(el);   // the outer blooms sit behind the middle ones, as in a domed bouquet
        b = blooms[i] = { el, inner, kind: [0, 1, 0, 2, 1][i % 5], rand, j: .88 + rand() * .24 };
        if (!first && !reduced) requestAnimationFrame(() => requestAnimationFrame(() => el.classList.remove('is-new')));
      }
      const [x, y] = place(i, n);
      const r = size * b.j;
      if (b.r !== Math.round(r)) { b.r = Math.round(r); b.inner.innerHTML = flower(b.kind, r, rnd(i * 31 + 7)); }
      b.el.style.transform = `translate(${f(x)}px, ${f(y)}px)`;
      const [c, d] = TONES[cols[i % cols.length]];
      b.el.style.setProperty('--c', c); b.el.style.setProperty('--d', d);
      stemD += `M${f(x)} ${f(y)} Q${f((x + TIE[0]) / 2)} ${f((y + TIE[1]) / 2 + 12)} ${TIE[0]} ${TIE[1]} L${f(TIE[0] + (i % 5 - 2) * 5)} 446 `;
    }
    stems.innerHTML = `<path d="${stemD}"/>`;
    const shown = Math.min(8, 3 + Math.floor(n / 4));
    [...leaves.children].forEach((g, k) => { g.style.opacity = k < shown ? 1 : 0; });
    first = false;
  }
  const soon = () => { if (!frame) frame = requestAnimationFrame(draw); };
  range.addEventListener('input', soon);
  builder.addEventListener('change', soon);
  draw();

  sender(builder, () => { $('#c-note').value = ''; });
}
