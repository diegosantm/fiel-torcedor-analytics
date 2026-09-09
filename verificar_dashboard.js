const fs=require('fs');
const html=fs.readFileSync('dashboard/dashboard-fiel-torcedor.html','utf8');

// 1) regras de CSS que testes headless não pegam
const cssOk = html.includes('.modal-bg[hidden]{display:none}');
console.log('CSS .modal-bg[hidden]{display:none} presente:', cssOk);
const ordem = html.indexOf('.modal-bg{') < html.indexOf('.modal-bg[hidden]');
console.log('  e vem depois da regra display:flex:', ordem);

// 2) extrai o script da aplicacao (o ultimo <script>)
const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const app=scripts[scripts.length-1];
console.log('scripts encontrados:', scripts.length, '| tamanho do app:', app.length);

// 3) stubs de DOM e Chart
const els={};
function mkEl(id){ return els[id]||(els[id]={id, innerHTML:'', textContent:'', value:'',
  hidden:false, dataset:{}, classList:{toggle(){},add(){},remove(){}},
  querySelectorAll:()=>[], onclick:null, oninput:null, style:{}}); }
global.document={ getElementById:mkEl, querySelectorAll:()=>[], addEventListener(){} };
let destroyed=0;
global.Chart=class{ constructor(el,cfg){ this.cfg=cfg; } destroy(){destroyed++;} };

// 4) captura funcoes internas expondo-as no fim
const drills=[];
const patched = app + `
;globalThis.__t={passes,render,state,BASE,DIMS,openDrill,segmentar,curRows:()=>curRows,
  D,PL,RT,CO,PTS,M12,CAC,MOED,JOGOS,DIST,AT,MESES,CUPE,soma,media,DADOS};`;
eval(patched);
const t=globalThis.__t;

// 5) asserções
let falhas=0;
function chk(nome,cond,extra=''){ if(!cond){falhas++;console.log('  FALHOU:',nome,extra);} else console.log('  ok:',nome,extra); }

console.log('\n-- base --');
chk('18.000 sócios embarcados', t.BASE.length===18000, `(${t.BASE.length})`);
chk('carimbo de build presente', !!t.DADOS.meta.fp, t.DADOS.meta.fp);
chk('todos os casos-teste passam', t.DADOS.testes.every(x=>x.ok));

console.log('\n-- passes() e coorte --');
const coorte=t.BASE.filter(t.passes);
chk('coorte ativa filtra a base', coorte.length < t.BASE.length, `${coorte.length} de ${t.BASE.length}`);
chk('nenhum fora da coorte passa', coorte.every(r=>r[t.CO]===1));
t.state.soCoorte=false;
const tudo=t.BASE.filter(t.passes);
chk('coorte desligada libera a base inteira', tudo.length===t.BASE.length);
t.state.soCoorte=true;

console.log('\n-- filtro de dimensao --');
t.state.sel.plano=new Set([0]);
const soDigital=t.BASE.filter(t.passes);
chk('filtro por plano restringe', soDigital.every(r=>r[t.PL]===0), `${soDigital.length} sócios`);
chk('Fiel Digital tem zero ponto sempre', soDigital.every(r=>r[t.PTS]===0));
t.state.sel.plano=new Set(t.D.plano.map((_,i)=>i));

console.log('\n-- render completo --');
try{ t.render(); console.log('  ok: render() sem erro'); }catch(e){ falhas++; console.log('  FALHOU render():',e.message); }
chk('charts destruídos ao re-renderizar', (t.render(), destroyed>0), `${destroyed} destroy()`);

console.log('\n-- crosscheck Python x JS --');
const c=t.BASE.filter(r=>r[t.CO]===1);
const jsRet=(t.soma(c,t.RT)/c.length*100).toFixed(1);
const pyRet=t.DADOS.crosscheck.find(x=>x.metrica.includes('Retenção 12m da coorte')).python;
chk('retenção da coorte bate', Math.abs(+jsRet - +pyRet)<=0.1, `py=${pyRet} js=${jsRet}`);
const jsM12=t.media(c,t.M12).toFixed(2);
const pyM12=t.DADOS.crosscheck.find(x=>x.metrica.includes('Margem M12')).python;
chk('margem M12 bate', Math.abs(+jsM12 - +pyM12)<=0.1, `py=${pyM12} js=${jsM12}`);

console.log('\n-- segmentos --');
const seg=t.segmentar(t.BASE.filter(r=>r[t.AT]===1));
const somaSeg=seg.g.reduce((s,x)=>s+x.length,0);
chk('segmentos particionam a base ativa sem sobra', somaSeg===seg.total, `${somaSeg}/${seg.total}`);
chk('cada sócio cai em exatamente um segmento', seg.g.every(x=>Array.isArray(x)));

console.log('\n-- drill --');
t.openDrill('teste', coorte.slice(0,10));
chk('openDrill abre o modal', els['modal'].hidden===false);
chk('modal renderiza tabela', els['m_tabela'].innerHTML.includes('<table>'));

console.log(falhas===0 ? '\nTODAS AS VERIFICAÇÕES PASSARAM' : `\n${falhas} FALHA(S)`);
process.exit(falhas?1:0);
