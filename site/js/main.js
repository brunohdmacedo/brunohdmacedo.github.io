var TH={};
function rt(){var d=document.documentElement,t=d.dataset.theme||(matchMedia('(prefers-color-scheme:light)').matches?'light':'dark'),cs=getComputedStyle(d);['cy','am','line','mut','bg'].forEach(function(k){TH[k]=cs.getPropertyValue('--'+k).trim()});TH.cr=t==='light'?'10,143,120':'79,227,193';var b=document.getElementById('tg');if(b){b.textContent=t==='light'?'☾':'☀';b.title=t==='light'?'Modo escuro':'Modo claro';b.setAttribute('aria-label',b.title)}return t}
rt();

(function(){
document.getElementById('y').textContent=new Date().getFullYear();
var hd=document.getElementById('hd');document.getElementById('bur').onclick=function(){hd.classList.toggle('o')};
document.querySelectorAll('.links a').forEach(function(a){a.onclick=function(){hd.classList.remove('o')}});
// typed
var ph=['Engenheiro Físico','Mestrando em Física Aplicada','DFT · Machine Learning · Materiais'],pi=0,ci=0,del=false,T=document.getElementById('typed');
function tp(){var s=ph[pi];T.textContent='> '+s.slice(0,ci)+'▌';if(!del&&ci<s.length){ci++;setTimeout(tp,60)}else if(!del){del=true;setTimeout(tp,1400)}else if(ci>0){ci--;setTimeout(tp,28)}else{del=false;pi=(pi+1)%ph.length;setTimeout(tp,300)}}tp();
// lattice canvas
var c=document.getElementById('cv'),x=c.getContext('2d'),W,H,pts=[],m={x:-999,y:-999},red=matchMedia('(prefers-reduced-motion:reduce)').matches;
function rs(){W=c.width=c.offsetWidth;H=c.height=c.offsetHeight;pts=[];var n=Math.min(90,Math.floor(W*H/14000));for(var i=0;i<n;i++)pts.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.35,vy:(Math.random()-.5)*.35,h:Math.random()<.25})}
rs();addEventListener('resize',rs);c.parentNode.addEventListener('mousemove',function(e){var r=c.getBoundingClientRect();m.x=e.clientX-r.left;m.y=e.clientY-r.top});
function dr(){x.clearRect(0,0,W,H);pts.forEach(function(p,i){if(!red){p.x+=p.vx;p.y+=p.vy}if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;
var dx=p.x-m.x,dy=p.y-m.y,d=Math.hypot(dx,dy);if(d<110){p.x+=dx/d*1.2;p.y+=dy/d*1.2}
for(var j=i+1;j<pts.length;j++){var q=pts[j],e=Math.hypot(p.x-q.x,p.y-q.y);if(e<130){x.strokeStyle='rgba('+TH.cr+','+(.22*(1-e/130))+')';x.beginPath();x.moveTo(p.x,p.y);x.lineTo(q.x,q.y);x.stroke()}}
x.fillStyle=p.h?TH.am:TH.cy;x.beginPath();x.arc(p.x,p.y,p.h?2:3.2,0,6.3);x.fill()});requestAnimationFrame(dr)}dr();
// counters
function cnt(el){var n=+el.dataset.n,i=0,t=setInterval(function(){i++;el.textContent=i;if(i>=n)clearInterval(t)},80)}
// reveal
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12});
document.querySelectorAll('.rv,.ti').forEach(function(e){io.observe(e)});
var so=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.querySelectorAll('[data-n]').forEach(cnt);so.disconnect()}})});so.observe(document.querySelector('.stats'));
// filter
document.querySelectorAll('#fl button').forEach(function(b){b.onclick=function(){document.querySelectorAll('#fl button').forEach(function(k){k.classList.remove('on')});b.classList.add('on');var f=b.dataset.f;document.querySelectorAll('.pub').forEach(function(p){p.classList.toggle('h',f!=='all'&&p.dataset.t!==f)})}});
// active nav
var secs=document.querySelectorAll('main section[id]'),na=document.querySelectorAll('.links a');
addEventListener('scroll',function(){var y=scrollY+120,cur='';secs.forEach(function(s){if(s.offsetTop<=y)cur=s.id});na.forEach(function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+cur)})},{passive:true});
var $=function(i){return document.getElementById(i)},act='q',lv=false,last=0,th=0,buf=[];
new IntersectionObserver(function(e){lv=e[0].isIntersecting}).observe($('lab'));
document.querySelectorAll('#tabs button').forEach(function(b){b.onclick=function(){document.querySelectorAll('#tabs button').forEach(function(k){k.classList.remove('on')});b.classList.add('on');act=b.dataset.p;document.querySelectorAll('.lp').forEach(function(p){p.classList.toggle('on',p.id===act)})}});
function psi(n,u,t){var s=Math.SQRT2*Math.sin(n*Math.PI*u),E=.9*n*n;return[s*Math.cos(E*t),-s*Math.sin(E*t)]}
function wf(u,t,n,sp){var a=psi(n,u,t);if(sp){var b=psi(n+1,u,t);return[(a[0]+b[0])/Math.SQRT2,(a[1]+b[1])/Math.SQRT2]}return a}
var qx=$('cq').getContext('2d');
function dq(t){var n=+$('qn').value,sp=$('qs').checked,L=60,w=680,N=220,i,u,p;$('qnv').textContent=n;
qx.clearRect(0,0,800,400);qx.lineWidth=1;qx.strokeStyle=TH.line;qx.beginPath();qx.moveTo(L,140);qx.lineTo(L+w,140);qx.moveTo(L,380);qx.lineTo(L+w,380);qx.stroke();
qx.strokeStyle=TH.cy;qx.lineWidth=3;qx.beginPath();qx.moveTo(L,20);qx.lineTo(L,390);qx.moveTo(L+w,20);qx.lineTo(L+w,390);qx.stroke();
qx.beginPath();qx.moveTo(L,380);for(i=0;i<=N;i++){u=i/N;p=wf(u,t,n,sp);qx.lineTo(L+u*w,380-(p[0]*p[0]+p[1]*p[1])*38)}qx.lineTo(L+w,380);qx.fillStyle='rgba(245,181,68,.25)';qx.fill();qx.strokeStyle=TH.am;qx.lineWidth=2;qx.stroke();
qx.beginPath();for(i=0;i<=N;i++){u=i/N;p=wf(u,t,n,sp);qx[i?'lineTo':'moveTo'](L+u*w,140-p[0]*60)}qx.strokeStyle=TH.cy;qx.lineWidth=2.5;qx.stroke();
qx.fillStyle=TH.mut;qx.font='13px JetBrains Mono,monospace';qx.fillText('Re ψ(x,t)',L+10,34);qx.fillText('|ψ|²  densidade de probabilidade',L+10,364);
$('qo').innerHTML='E<sub>n</sub> = n²·E₁ = '+(n*n)+'·E₁<br>nós: '+(n-1)+(sp?'<br>oscila entre n='+n+' e n='+(n+1):'<br>estado estacionário')}
function ov(d,r){if(d>=1+r)return 0;if(d<=Math.abs(1-r))return Math.PI*Math.min(1,r*r);var a=Math.acos((d*d+r*r-1)/(2*d*r)),b=Math.acos((d*d+1-r*r)/(2*d));return r*r*a+b-.5*Math.sqrt((-d+r+1)*(d+r-1)*(d-r+1)*(d+r+1))}
function gs(){return(Math.random()+Math.random()+Math.random()-1.5)*1.4}
var xx=$('cx').getContext('2d');
function dx(dt){var r=+$('xr').value,P=+$('xp').value,b=+$('xb').value,nz=+$('xn').value;
$('xrv').textContent=r.toFixed(3);$('xpv').textContent=P.toFixed(1);$('xbv').textContent=b.toFixed(2);$('xnv').textContent=nz.toFixed(2);
th+=dt*6.2832/P;var cx=400,cy=100,R=70,px=cx+300*Math.sin(th),py=cy+b*R,fr=Math.cos(th)>0,d=Math.hypot(px-cx,py-cy)/R,fl=fr?1-ov(d,r)/Math.PI:1;
buf.push(fl+gs()*.002*nz);if(buf.length>500)buf.shift();
xx.clearRect(0,0,800,400);
function star(){var g=xx.createRadialGradient(cx,cy,R*.1,cx,cy,R);g.addColorStop(0,'#FFE9A8');g.addColorStop(1,'#F5A623');xx.fillStyle=g;xx.beginPath();xx.arc(cx,cy,R,0,6.3);xx.fill()}
function pl(){xx.fillStyle=TH.bg;xx.strokeStyle=TH.cy;xx.lineWidth=2;xx.beginPath();xx.arc(px,py,Math.max(3,r*R),0,6.3);xx.fill();xx.stroke()}
xx.strokeStyle=TH.line;xx.lineWidth=1;xx.setLineDash([4,6]);xx.beginPath();xx.moveTo(60,py);xx.lineTo(740,py);xx.stroke();xx.setLineDash([]);
if(fr){star();pl()}else{pl();star()}
var y0=220,y1=380,lo=.955,hh=1.005,i,yy;xx.strokeStyle=TH.line;xx.strokeRect(60,y0,700,y1-y0);
xx.fillStyle=TH.mut;xx.font='12px JetBrains Mono,monospace';xx.fillText('fluxo relativo',66,y0+16);xx.fillText('tempo →',690,y1-8);
xx.fillStyle=TH.cy;for(i=0;i<buf.length;i++){yy=y1-(Math.min(hh,Math.max(lo,buf[i]))-lo)/(hh-lo)*(y1-y0);xx.fillRect(60+i*1.4,yy-1,2,2)}
$('xo').innerHTML='profundidade = (Rp/R★)² = '+(r*r*100).toFixed(2)+' %<br>Rp ≈ '+(r*109.1).toFixed(1)+' R⊕ (estrela solar)<br>≈ '+(r*9.73).toFixed(2)+' R♃<br>fluxo agora: '+fl.toFixed(4)}
function wl(l){var r=0,g=0,b=0,f=1;if(l<440){r=(440-l)/60;b=1}else if(l<490){g=(l-440)/50;b=1}else if(l<510){g=1;b=(510-l)/20}else if(l<580){r=(l-510)/70;g=1}else if(l<645){r=1;g=(645-l)/65}else{r=1}
if(l<420)f=.3+.7*(l-380)/40;else if(l>700)f=.3+.7*(750-l)/50;return'rgb('+[r,g,b].map(function(v){return Math.round(255*Math.pow(Math.max(0,v*f),.8))}).join(',')+')'}
var hx=$('ch').getContext('2d'),SN=['Lyman (UV)','Balmer (visível)','Paschen (IV)','Brackett (IV)'];
function dh(t){var nf=+$('hf').value,ni=+$('hi').value;if(ni<=nf){ni=nf+1;$('hi').value=ni}
$('hiv').textContent=ni;$('hfv').textContent=nf;
var E=13.606*(1/(nf*nf)-1/(ni*ni)),l=1239.84/E,vis=l>=380&&l<=750,col=vis?wl(l):(l<380?'#b8a6ff':'#ff7b7b'),ax=240,ay=200,n,k,i,rr=function(q){return 14+24*(q-1)};
hx.clearRect(0,0,800,400);
for(n=1;n<=7;n++){hx.strokeStyle=(n==ni||n==nf)?TH.cy:TH.line;hx.lineWidth=(n==ni||n==nf)?1.5:1;hx.beginPath();hx.arc(ax,ay,rr(n),0,6.3);hx.stroke()}
hx.fillStyle=TH.am;hx.beginPath();hx.arc(ax,ay,7,0,6.3);hx.fill();
var c=t%4,rad,ph=t*2.5;
if(c<1.5)rad=rr(ni);else if(c<2)rad=rr(ni)+(rr(nf)-rr(ni))*(c-1.5)/.5;else if(c<3.5)rad=rr(nf);else rad=rr(nf)+(rr(ni)-rr(nf))*(c-3.5)/.5;
hx.fillStyle=TH.cy;hx.beginPath();hx.arc(ax+rad*Math.cos(ph),ay+rad*Math.sin(ph),6,0,6.3);hx.fill();
if(c>=2&&c<3.5){var hd=440+(c-2)/1.5*340,pw=8+l/25,x2;hx.strokeStyle=col;hx.lineWidth=2.5;hx.beginPath();for(i=0;i<=120;i++){x2=hd-i;if(x2<430)break;hx.lineTo(x2,200+16*Math.sin(i*6.283/pw)*(1-i/130))}hx.stroke()}
for(k=0;k<340;k++){hx.fillStyle=wl(380+k*370/340);hx.fillRect(430+k,350,1,16)}
hx.fillStyle=TH.mut;hx.font='12px JetBrains Mono,monospace';hx.fillText('380 nm',430,342);hx.fillText('750 nm',724,342);
if(vis){hx.fillStyle='#fff';hx.fillRect(430+(l-380)/370*340-1,346,3,26)}else hx.fillText('λ fora do visível ('+(l<380?'UV':'IV')+')',480,388);
$('ho').innerHTML='n = '+ni+' → '+nf+' · série '+SN[nf-1]+'<br>ΔE = '+E.toFixed(3)+' eV<br>λ = '+l.toFixed(1)+' nm'}
function loop(ts){var dt=Math.min(.05,(ts-last)/1000);last=ts;if(lv){var t=ts/1000;if(act==='q')dq(t);else if(act==='x')dx(dt);else dh(t)}requestAnimationFrame(loop)}requestAnimationFrame(loop);

// tema claro/escuro
document.getElementById('tg').onclick=function(){var n=rt()==='light'?'dark':'light';document.documentElement.dataset.theme=n;try{localStorage.setItem('theme',n)}catch(e){}rt()};
matchMedia('(prefers-color-scheme:light)').addEventListener('change',rt);
// fotos da timeline + lightbox
var lb=document.getElementById('lb'),li=lb.querySelector('img');
document.querySelectorAll('.tp').forEach(function(f){var im=f.querySelector('img');if(!im)return;
function fb(){f.classList.add('tpf');f.textContent=f.dataset.s||'';f.onclick=null}
im.onerror=fb;if(im.complete&&im.naturalWidth===0)fb();
f.onclick=function(){li.src=im.src;lb.classList.add('o')}});
lb.onclick=function(){lb.classList.remove('o')};addEventListener('keydown',function(e){if(e.key==='Escape')lb.classList.remove('o')});
// spotlight nos cards e barra de progresso
document.querySelectorAll('.card').forEach(function(c){c.addEventListener('mousemove',function(e){var r=c.getBoundingClientRect();c.style.setProperty('--mx',e.clientX-r.left+'px');c.style.setProperty('--my',e.clientY-r.top+'px')})});
var pg=document.getElementById('pg');addEventListener('scroll',function(){pg.style.width=scrollY/Math.max(1,document.documentElement.scrollHeight-innerHeight)*100+'%'},{passive:true});
})();
