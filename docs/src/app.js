/* Literal Lock-In — the interactive parts, without a framework.
 *
 * Everything here is enhancement: the page is complete and readable with
 * JavaScript off, so each block fails silently. Honour prefers-reduced-motion
 * by not animating at all.
 */
(function () {
  'use strict';
  var D = JSON.parse(document.getElementById('site-data').textContent);
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ── hero: Bengali ⇄ English, auto-plays until the reader touches it ── */
  var heroP = ['1.00', '0.97', '0.36'];
  function hero(bn) {
    var rows = $$('[data-hero-row]'), lars = $$('[data-hero-lar]');
    rows.forEach(function (el, i) {
      var lit = i === 0 ? true : bn;
      var dot = $('[data-hero-dot]', el), lab = $('[data-hero-label]', el);
      dot.style.left = lit ? '4%' : '96%';
      dot.style.flexDirection = lit ? 'row' : 'row-reverse';
      lab.textContent = lit ? (bn ? 'literal · p = ' + heroP[i] : 'literal') : 'recovers';
    });
    lars.forEach(function (el, i) {
      var v = bn ? D.larBn[i] : D.larEn[i];
      el.textContent = v.toFixed(3);
    });
    $$('[data-act="hero:bn"]').forEach(function (b) { press(b, bn); });
    $$('[data-act="hero:en"]').forEach(function (b) { press(b, !bn); });
  }
  function press(btn, on) {
    btn.style.background = on ? 'var(--color-accent-900)' : 'transparent';
    btn.style.color = on ? '#ffffff' : 'var(--color-text)';
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
  }
  var heroAuto = true;
  hero(true);
  if (!reduce) setInterval(function () { if (heroAuto) hero(document.body.dataset.hero !== 'bn'); },
                           3800);
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-act^="hero:"]');
    if (!b) return;
    heroAuto = false;
    var bn = b.dataset.act === 'hero:bn';
    document.body.dataset.hero = bn ? 'bn' : 'en';
    hero(bn);
  });

  /* ── pipeline stage stepper ── */
  var stages = $$('[data-stage]');
  if (stages.length && !reduce) {
    var step = 0;
    stages.forEach(function (el, i) {
      $('[data-stage-bar]', el).style.width = i === 0 ? '100%' : '0%';
      $('[data-stage-dot]', el).style.opacity = i === 0 ? 1 : 0;
    });
    setInterval(function () {
      step = (step + 1) % stages.length;
      stages.forEach(function (el, i) {
        var on = i === step;
        el.style.background = on ? 'var(--color-accent-100)'
          : (i === 1 ? 'color-mix(in srgb, var(--color-accent-100) 40%, transparent)' : 'transparent');
        $('[data-stage-dot]', el).style.opacity = on ? 1 : 0;
        $('[data-stage-bar]', el).style.width = (i <= step) ? '100%' : '0%';
      });
    }, 1600);
  }

  /* ── distractor family switch ── */
  var famBtns = $$('[data-family]'), slotBox = $('[data-slots]'), famDesc = $('[data-famdesc]');
  function family(code) {
    famBtns.forEach(function (b) {
      var on = b.dataset.family === code;
      b.style.background = on ? 'var(--color-accent-900)' : 'transparent';
      b.style.color = on ? '#ffffff' : 'var(--color-text)';
      b.style.borderColor = on ? 'var(--color-accent-900)' : 'var(--color-divider)';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    if (famDesc) famDesc.textContent = D.fam[code].d;
    if (!slotBox) return;
    var kinds = ['gold'].concat(D.fam[code].s);
    var rows = [2, 0, 3, 1].map(function (k, i) {
      var kind = kinds[k], s = D.slots[kind];
      var bd = kind === 'lit' ? 'var(--color-accent-800)'
        : kind === 'gold' ? 'var(--color-accent-400)' : 'var(--color-divider)';
      var bg = kind === 'lit' ? 'var(--color-accent-100)' : 'transparent';
      var tc = kind === 'lit' ? 'var(--color-accent-800)' : 'var(--color-neutral-700)';
      return '<div style="display:grid;grid-template-columns:28px minmax(0,1fr) auto;' +
        'align-items:center;gap:10px;padding:10px 12px;border:1px solid ' + bd + ';background:' +
        bg + ';transition:all .45s;"><span style="font-family:var(--font-mono);font-size:12px;' +
        'color:var(--color-neutral-700);">ABCD'[i] + '</span><span style="font-size:15px;">' +
        s.t + '</span><span style="font-family:var(--font-mono);font-size:11px;color:' + tc +
        ';">' + s.tag + '</span></div>';
    });
    slotBox.innerHTML = rows.join('');
  }
  famBtns.forEach(function (b) {
    b.addEventListener('click', function () { family(b.dataset.family); });
  });
  family('D-LIT');

  /* ── model × language toggle ── */
  function matrix(kind) {
    $$('[data-matrix-row]').forEach(function (row, i) {
      var bn = kind === 'lar' ? D.larBn[i] : D.accBn[i];
      var en = kind === 'lar' ? D.larEn[i] : D.accEn[i];
      $('[data-bn-bar]', row).style.width = (bn * 100).toFixed(1) + '%';
      $('[data-en-bar]', row).style.width = (en * 100).toFixed(1) + '%';
      $('[data-bn-val]', row).textContent = bn.toFixed(3);
      $('[data-en-val]', row).textContent = en.toFixed(3);
    });
    $$('[data-act="matrix:lar"]').forEach(function (b) { press(b, kind === 'lar'); });
    $$('[data-act="matrix:acc"]').forEach(function (b) { press(b, kind === 'acc'); });
  }
  $$('[data-act^="matrix:"]').forEach(function (b) {
    b.addEventListener('click', function () { matrix(b.dataset.act.split(':')[1]); });
  });

  /* ── O4 ablation: gloss ⇄ bare ordinal ── */
  var o4Opts = $$('[data-o4]');
  var o4On = false;
  function o4() {
    o4Opts.forEach(function (el, i) {
      var real = $('[data-o4-real]', el), blank = $('[data-o4-blank]', el);
      real.style.transform = 'translateY(' + (o4On ? '-100%' : '0') + ')';
      real.style.opacity = o4On ? 0 : 1;
      blank.style.transform = 'translateY(' + (o4On ? '0' : '100%') + ')';
      blank.style.opacity = o4On ? 1 : 0;
    });
  }
  if (o4Opts.length) {
    o4();
    if (!reduce) setInterval(function () { o4On = !o4On; o4(); }, 4800);
    var o4fig = o4Opts[0].closest('figure');
    if (o4fig) o4fig.addEventListener('click', function () { o4On = !o4On; o4(); });
  }

  /* ── 24 orderings ── */
  var chips = $$('[data-perm-chip]'), permN = $('[data-perm-n]'), permI = 0;
  var NAMES = ['Gold figurative', 'Literal gloss', 'Distractor 1', 'Distractor 2'];
  function perm(i) {
    var p = D.perms[D.order[i % 24]], layaPick = p[1];
    chips.forEach(function (el, g) {
      el.style.transform = 'translateY(' + (p.indexOf(g) * 52) + 'px)';
      var mk = [];
      if (layaPick === g) mk.push('●');
      if (g === 1) mk.push('■');
      if (g === 0) mk.push('▲');
      $('[data-perm-picks]', el).textContent = mk.join(' ');
    });
    if (permN) permN.textContent = (i % 24) + 1;
  }
  perm(0);
  if (chips.length && !reduce) setInterval(function () { permI++; perm(permI); }, 1600);

  /* ── copy BibTeX ── */
  var copyBtn = $('[data-act="copy-bib"]');
  if (copyBtn) copyBtn.addEventListener('click', function () {
    var done = function () {
      copyBtn.textContent = 'Copied';
      setTimeout(function () { copyBtn.textContent = 'Copy BibTeX'; }, 1800);
    };
    if (navigator.clipboard) navigator.clipboard.writeText(D.bib).then(done, done);
    else done();
  });

  /* ── reveal: grow the marks when a figure first comes into view ── */
  function grow(root) {
    $$('[data-grow]', root).forEach(function (el) {
      var w = el.dataset.w, h = el.dataset.h;
      if (w) el.style.width = w;
      if (h) el.style.height = h;
    });
    var plot = $('[data-chart]', root) || (root.hasAttribute && root.hasAttribute('data-chart') ? root : null);
    if (plot) plot.classList.add('on');
  }
  var targets = $$('[data-reveal]');
  if (!('IntersectionObserver' in window) || reduce) {
    targets.forEach(grow);
    $$('[data-chart]').forEach(grow);
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        grow(en.target);
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    targets.concat($$('[data-chart]')).forEach(function (el) { io.observe(el); });
  }
  /* SVG marks use a transform-based grow; hand them over once visible */
  if (!reduce) {
    var io2 = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('grown');
        io2.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    $$('.chart').forEach(function (el) { io2.observe(el); });
  } else {
    $$('.chart').forEach(function (el) { el.classList.add('grown'); });
  }

  /* model × language dots travel from the Bengali cell to the English one */
  if (!reduce) {
    $$('[data-dot]').forEach(function (el) {
      var to = el.dataset.dot.split(','), from = el.dataset.from.split(',');
      el.style.transition = 'none';
      el.setAttribute('cx', from[0]); el.setAttribute('cy', from[1]);
      requestAnimationFrame(function () {
        setTimeout(function () {
          el.style.transition = 'cx 1.4s cubic-bezier(.65,0,.25,1), cy 1.4s cubic-bezier(.65,0,.25,1)';
          el.setAttribute('cx', to[0]); el.setAttribute('cy', to[1]);
        }, 400);
      });
    });
  }
})();