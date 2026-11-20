/* BrUMaRe: motor de idiomas (pt, en, es, fr, it, la)
 * SPDX-License-Identifier: GPL-3.0-or-later · Copyright (C) 2025-2026 Bruno Henrique Dourado Macedo
 *
 * Traduz o que aparece na tela (textos e os atributos placeholder, title e aria-label), inclusive o que o
 * JavaScript da página desenha depois, sem mexer no código das análises:
 *   window.I18N_DICT  = { "texto em português": {en:"…", es:"…", fr:"…", it:"…", la:"…"}, … }
 *   window.I18N_RULES = [ ["^Cor de (.+)$", {en:"Color of $1", …}], … ]   (textos com partes variáveis)
 * O texto original de cada nó fica guardado, então dá para trocar de idioma quantas vezes quiser.
 * Elementos com translate="no" (como a frase do autor) nunca são traduzidos.
 */
(function () {
  'use strict';
  var LANGS = {pt: 'Português', en: 'English', es: 'Español', fr: 'Français', it: 'Italiano', la: 'Latina'};
  var HTML_LANG = {pt: 'pt-BR', en: 'en', es: 'es', fr: 'fr', it: 'it', la: 'la'};
  var KEY = 'brumare.lang';
  var D = window.I18N_DICT || {}, R = [];
  (window.I18N_RULES || []).forEach(function (r) { try { R.push([new RegExp(r[0]), r[1]]); } catch (e) {} });
  var ATTRS = ['placeholder', 'title', 'aria-label'];
  var orig = new WeakMap(), mine = new WeakMap(), busy = false;   // mine: o que o próprio motor escreveu

  function detect() {
    try { var q = new URLSearchParams(location.search).get('lang'); if (q && LANGS[q]) return q; } catch (e) {}
    try { var s = localStorage.getItem(KEY); if (s && LANGS[s]) return s; } catch (e) {}
    var n = ((navigator.languages && navigator.languages[0]) || navigator.language || 'pt').slice(0, 2).toLowerCase();
    return LANGS[n] ? n : 'pt';
  }
  var lang = detect();

  /* Páginas com uma versão por idioma (ex.: tutorial.html, tutorial.en.html): <html data-i18n-pages='{"pt":…}' data-i18n-page-lang="en"> */
  var PAGES = null, PAGE_LANG = 'pt';
  try { PAGES = JSON.parse(document.documentElement.getAttribute('data-i18n-pages') || 'null'); } catch (e) {}
  PAGE_LANG = document.documentElement.getAttribute('data-i18n-page-lang') || 'pt';
  var AVISO = {
    pt: 'Esta página ainda não está disponível em português.',
    en: 'This page is not yet available in English; showing the {X} version.',
    es: 'Esta página aún no está disponible en español; se muestra la versión en {X}.',
    fr: 'Cette page n’est pas encore disponible en français ; la version {X} est affichée.',
    it: 'Questa pagina non è ancora disponibile in italiano; viene mostrata la versione {X}.',
    la: 'Haec pagina nondum Latine praesto est; versio {X} ostenditur.'
  };
  var NOME_EM = {
    en: {en: 'English', es: 'Spanish', pt: 'Portuguese'}, es: {en: 'inglés', es: 'español', pt: 'portugués'},
    fr: {en: 'anglaise', es: 'espagnole', pt: 'portugaise'}, it: {en: 'inglese', es: 'spagnola', pt: 'portoghese'},
    la: {en: 'Anglica', es: 'Hispanica', pt: 'Lusitana'}, pt: {en: 'inglês', es: 'espanhol', pt: 'português'}
  };
  function paginaPara(l) { return PAGES ? (PAGES[l] || PAGES.en || PAGES.pt) : null; }
  function irPara(l) {                      // devolve true se vai trocar de página
    var alvo = paginaPara(l); if (!alvo) return false;
    var atual = (location.pathname.split('/').pop() || '').split('?')[0] || 'index.html';
    if (alvo === atual) return false;
    location.replace(alvo + location.search.replace(/([?&])lang=[^&]*&?/, '$1').replace(/[?&]$/, '') + location.hash);
    return true;
  }
  function aviso() {
    var old = document.getElementById('i18n-aviso'); if (old) old.remove();
    if (!PAGES || PAGES[lang] || lang === PAGE_LANG) return;
    var d = document.createElement('div'); d.id = 'i18n-aviso'; d.setAttribute('translate', 'no');
    d.textContent = (AVISO[lang] || AVISO.en).replace('{X}', (NOME_EM[lang] || NOME_EM.en)[PAGE_LANG] || PAGE_LANG);
    d.style.cssText = 'max-width:1100px;margin:76px auto -56px;padding:10px 16px;border:1px dashed var(--line,#ccc);border-radius:10px;font-size:14px;color:var(--mut,#555);text-align:center';
    var m = document.querySelector('main') || document.body; m.parentNode.insertBefore(d, m);
  }

  function tr(s) {
    if (lang === 'pt' || !s) return s;
    var m = s.match(/^(\s*)([\s\S]*?)(\s*)$/), core = m[2].replace(/\s+/g, ' ');
    if (!core) return s;
    var e = D[core];
    if (e && e[lang]) return m[1] + e[lang] + m[3];
    for (var i = 0; i < R.length; i++) {
      var r = R[i];
      if (r[0].test(core) && r[1][lang]) {
        var out = core.replace(r[0], r[1][lang]);
        out = out.replace(/\{\{([^}]+)\}\}/g, function (_, k) { var d = D[k]; return d && d[lang] ? d[lang] : k; });
        return m[1] + out + m[3];
      }
    }
    return s;
  }
  function skip(el) {
    return !el || el.closest('[translate="no"],script,style,code,pre,textarea,.mono-no-i18n') !== null;
  }
  function doText(n) {
    if (skip(n.parentElement)) return;
    if (!orig.has(n)) orig.set(n, n.nodeValue);
    var o = orig.get(n), t = tr(o);
    if (n.nodeValue !== t) n.nodeValue = t;
    mine.set(n, t);
  }
  function doAttrs(el) {
    if (skip(el)) return;
    for (var i = 0; i < ATTRS.length; i++) {
      var a = ATTRS[i], v = el.getAttribute(a);
      if (v === null) continue;
      var k = 'data-i18n-' + a;
      if (!el.hasAttribute(k)) el.setAttribute(k, v);
      var t = tr(el.getAttribute(k));
      if (v !== t) el.setAttribute(a, t);
      var ms = mine.get(el) || {}; ms[a] = t; mine.set(el, ms);
    }
  }
  function walk(root) {
    if (!root) return;
    if (root.nodeType === 3) { doText(root); return; }
    if (root.nodeType !== 1) return;
    doAttrs(root);
    var w = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT), n;
    while ((n = w.nextNode())) { if (n.nodeType === 3) doText(n); else doAttrs(n); }
  }
  function apply() { busy = true; try { walk(document.body); } finally { busy = false; } document.title = tr(window.__i18nTitle || (window.__i18nTitle = document.title)); }

  var pend = [], timer = 0;
  var mo = new MutationObserver(function (list) {
    if (busy) return;
    for (var i = 0; i < list.length; i++) {
      var r = list[i];
      if (r.type === 'childList') for (var j = 0; j < r.addedNodes.length; j++) pend.push(r.addedNodes[j]);
      else if (r.type === 'characterData') {
        if (mine.get(r.target) === r.target.nodeValue) continue;        // mudança feita pelo próprio motor
        orig.delete(r.target); pend.push(r.target);
      } else if (r.type === 'attributes' && !/^data-i18n/.test(r.attributeName)) {
        var ms = mine.get(r.target);
        if (ms && ms[r.attributeName] === r.target.getAttribute(r.attributeName)) continue;
        r.target.removeAttribute('data-i18n-' + r.attributeName); pend.push(r.target);
      }
    }
    if (!timer) timer = requestAnimationFrame(function () {
      timer = 0; busy = true;
      try { var p = pend; pend = []; for (var k = 0; k < p.length; k++) if (p[k].isConnected !== false) walk(p[k]); } finally { busy = false; }
    });
  });

  function setLang(l) {
    if (!LANGS[l]) return;
    lang = l;
    try { localStorage.setItem(KEY, l); } catch (e) {}
    if (irPara(l)) return;
    document.documentElement.lang = HTML_LANG[PAGES ? PAGE_LANG : l];
    document.querySelectorAll('select.lang-sel').forEach(function (s) { s.value = l; });
    apply(); aviso();
    try { window.dispatchEvent(new CustomEvent('brumare-lang', {detail: l})); } catch (e) {}
  }

  function selector() {
    var hosts = document.querySelectorAll('[data-lang-host]');
    if (!hosts.length) { var nr = document.querySelector('header .nr'); if (nr) hosts = [nr]; }
    Array.prototype.forEach.call(hosts, function (h) {
      if (h.querySelector('select.lang-sel')) return;
      var s = document.createElement('select');
      s.className = 'lang-sel'; s.setAttribute('aria-label', 'Idioma / Language'); s.setAttribute('translate', 'no'); s.title = 'Idioma · Language · Idioma · Langue · Lingua · Lingua';
      for (var k in LANGS) { var o = document.createElement('option'); o.value = k; o.textContent = k.toUpperCase() + ' · ' + LANGS[k]; s.appendChild(o); }
      s.value = lang;
      s.addEventListener('change', function () { setLang(s.value); });
      h.insertBefore(s, h.firstChild);
    });
  }

  function start() {
    if (irPara(lang)) return;
    selector();
    document.documentElement.lang = HTML_LANG[PAGES ? PAGE_LANG : lang];
    apply(); aviso();
    mo.observe(document.body, {subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS});
  }
  window.BrUMaReI18n = {setLang: setLang, get lang() { return lang; }, t: tr, langs: LANGS};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
