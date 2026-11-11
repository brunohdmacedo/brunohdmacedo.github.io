/* Citações automáticas do portfólio (brunohdmacedo.tech)
   1) data/citacoes.json: gerado toda semana pelo GitHub Actions (.github/workflows/citacoes.yml)
      com os números do Google Acadêmico (via SerpApi, se houver chave) e do OpenAlex;
   2) OpenAlex ao vivo pelo ORCID, se o JSON não tiver dados recentes.
   Cada publicação com data-title (ou data-doi) recebe o selo "citado N×". */
(function(){
  var ORCID = '0000-0002-8152-0950', SCHOLAR = 'zl-LdTMAAAAJ';
  var RAW = 'https://raw.githubusercontent.com/brunohdmacedo/brunohdmacedo.github.io/main/data/citacoes.json';
  var box = document.getElementById('cites'); if (!box) return;
  var pubs = Array.prototype.slice.call(document.querySelectorAll('.pub[data-title], .pub[data-doi]'));
  function norm(t){ return String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/<[^>]+>/g, '').replace(/[^a-z0-9]+/g, ' ').trim(); }
  function same(a, b){ a = norm(a); b = norm(b); if (!a || !b) return false; var n = Math.min(45, a.length, b.length); return n >= 20 && (a.slice(0, n) === b.slice(0, n)); }
  function mark(works, src){
    pubs.forEach(function(p){
      var doi = (p.getAttribute('data-doi') || '').toLowerCase(), t = p.getAttribute('data-title') || '';
      var w = works.filter(function(w){ return (doi && w.doi && String(w.doi).toLowerCase().indexOf(doi) >= 0) || same(w.titulo, t); })[0];
      if (!w || !(w.citacoes > 0)) return;
      var el = p.querySelector('.cit'); if (!el){ el = document.createElement('em'); el.className = 'cit'; var sp = p.querySelector('span') || p.querySelector('b'); sp.appendChild(el); }
      el.textContent = 'citado ' + w.citacoes + '×'; el.title = 'Fonte: ' + src;
    });
  }
  function card(v, lab){ return '<div class="cb"><b>' + v + '</b><span>' + lab + '</span></div>'; }
  function fmtDate(iso){ try { return new Date(iso).toLocaleDateString('pt-BR'); } catch (e){ return iso; } }
  function render(data, liveOA){
    var h = '', src = [], g = data && data.scholar, o = liveOA || (data && data.openalex);
    if (g && g.citacoes != null){
      h += card(g.citacoes, 'citações · Google Acadêmico') + card(g.h, 'índice h') + card(g.i10, 'índice i10');
      src.push('<a href="https://scholar.google.com/citations?user=' + SCHOLAR + '" target="_blank" rel="noopener">Google Acadêmico</a> (atualizado em ' + fmtDate(data.atualizado) + ')');
      mark(g.artigos || [], 'Google Acadêmico');
    }
    if (o && o.citacoes != null){
      if (!g || g.citacoes == null) h += card(o.citacoes, 'citações · OpenAlex') + card(o.h, 'índice h (OpenAlex)');
      else h += card(o.citacoes, 'citações · OpenAlex');
      src.push('<a href="https://openalex.org/authors/orcid:' + ORCID + '" target="_blank" rel="noopener">OpenAlex</a>' + (liveOA ? ' (ao vivo)' : ' (atualizado em ' + fmtDate(data.atualizado) + ')'));
      if (!g || g.citacoes == null) mark(o.trabalhos || [], 'OpenAlex');
    }
    if (!h){ box.innerHTML = '<span class="src">Citações: veja o <a href="https://scholar.google.com/citations?user=' + SCHOLAR + '" target="_blank" rel="noopener">perfil no Google Acadêmico</a>.</span>'; return; }
    box.innerHTML = h + '<span class="src">Contagem automática de citações: ' + src.join(' · ') + '.</span>';
  }
  function getJSON(url){ return fetch(url, {cache: 'no-cache'}).then(function(r){ if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function liveOpenAlex(){
    var a = getJSON('https://api.openalex.org/authors/orcid:' + ORCID + '?mailto=brunohdmacedo@gmail.com');
    var w = getJSON('https://api.openalex.org/works?filter=author.orcid:' + ORCID + '&per-page=200&select=display_name,doi,cited_by_count,publication_year&mailto=brunohdmacedo@gmail.com');
    return Promise.all([a, w]).then(function(r){
      var s = r[0].summary_stats || {};
      return {citacoes: r[0].cited_by_count, h: s.h_index, i10: s.i10_index,
        trabalhos: (r[1].results || []).map(function(x){ return {titulo: x.display_name, doi: x.doi, citacoes: x.cited_by_count, ano: x.publication_year}; })};
    });
  }
  getJSON(RAW).catch(function(){ return getJSON('data/citacoes.json'); }).catch(function(){ return null; }).then(function(data){
    var fresh = data && data.atualizado && (Date.now() - new Date(data.atualizado).getTime()) < 10 * 864e5;
    render(data, null);
    if (!fresh || !data.openalex) liveOpenAlex().then(function(oa){ render(data, oa); }).catch(function(){});
  });
})();
