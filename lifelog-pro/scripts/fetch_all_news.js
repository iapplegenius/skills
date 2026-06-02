#!/usr/bin/env node
/**
 * LifeLog Pro v2 - Phase 4 一键新闻抓取
 * 适配 Windows + bundled Node.js，无需 Python
 * 已验证源（2026-06-01）：6/6 通过
 * 
 * 用法：node fetch_all_news.js [--json] [--cat tech|tech_cn|health]
 * 输出：JSON 到 stdout，进度到 stderr
 */
const https=require('https'),http=require('http'),fs=require('fs'),path=require('path');

function fetch(url,max=3,timeout=5000){
  return new Promise(r=>{
    const mod=url.startsWith('https')?https:http;
    const req=mod.get(url,{headers:{
      'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      'Accept':'application/rss+xml,application/xml,text/xml,text/html'
    },timeout},res=>{
      if(res.statusCode>=300&&res.statusCode<400&&res.headers.location){
        return fetch(res.headers.location,max,timeout).then(r);
      }
      let d='';res.on('data',c=>{d+=c;if(d.length>80000){res.destroy();r(parse(d,max));}});
      res.on('end',()=>r(parse(d,max)));
    });
    req.on('error',e=>r({status:'error',error:e.message,items:[]}));
    req.on('timeout',()=>{req.destroy();r({status:'error',error:'timeout',items:[]});});
  });
}

function parse(xml,max){
  const items=[];const re=/<title><!\[CDATA\[(.*?)\]\]>|<title>(.*?)<\/title>/g;
  let m;while((m=re.exec(xml))!==null){const s=(m[1]||m[2]||'').trim();if(s&&items.indexOf(s)===-1)items.push(s);if(items.length>=max+1)break;}
  return {status:items.length>0?'ok':'empty',items:items.slice(0,max)};
}

// 2026-06-01 实测通过的源
const SOURCES={
  tech:[
    {url:'https://www.technologyreview.com/feed/',name:'MIT Tech Review',max:3},
    {url:'https://hnrss.org/frontpage?count=3',name:'HackerNews',max:3},
    {url:'https://www.nature.com/nature.rss',name:'Nature',max:2},
  ],
  tech_cn:[
    {url:'https://36kr.com/feed',name:'36氪',max:3},
    {url:'https://sspai.com/feed',name:'少数派',max:3},
    {url:'https://www.ithome.com/rss/',name:'IT之家',max:3},
    {url:'https://www.ifanr.com/feed',name:'爱范儿',max:3},
  ],
  health:[
    {url:'https://feeds.bbci.co.uk/news/health/rss.xml',name:'BBC Health',max:2},
  ],
};

async function tryCategory(cat,sources){
  for(const s of sources){
    process.stderr.write('  '+s.name+'...');
    const r=await fetch(s.url,s.max);
    if(r.status==='ok'&&r.items.length>0){
      process.stderr.write(' OK ('+r.items.length+')\n');
      return {category:cat,status:'ok',source:s.name,items:r.items.map(function(t){return {title:t,source:s.name};})};
    }
    process.stderr.write(' '+r.status+'\n');
  }
  return {category:cat,status:'all_failed',items:[]};
}

(async()=>{
  const args=process.argv.slice(2);
  const jsonMode=args.indexOf('--json')>=0;
  const ci=args.indexOf('--cat');
  const catFilter=ci>=0?(args[ci+1]||''):'';

  const ts=new Date().toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'});
  process.stderr.write('=== LifeLog Pro Phase 4 ('+ts+') ===\n\n');

  const categories=catFilter?[catFilter]:Object.keys(SOURCES);
  const results={};
  let ok=0;

  for(const cat of categories){
    const sources=SOURCES[cat];
    if(!sources){process.stderr.write('Unknown category: '+cat+'\n');continue;}
    process.stderr.write('['+cat+']\n');
    results[cat]=await tryCategory(cat,sources);
    if(results[cat].status==='ok')ok++;
    process.stderr.write('\n');
  }

  var outDir=process.platform==='win32'
    ?path.join(process.env.TEMP||'C:\\Temp','lifelog-collect')
    :'/tmp/lifelog-collect';
  try{fs.mkdirSync(outDir,{recursive:true});}catch(e){}
  var outPath=path.join(outDir,'news_data.json');
  fs.writeFileSync(outPath,JSON.stringify(results,null,2),'utf8');

  process.stderr.write('=== '+ok+'/'+categories.length+' categories OK ===\n');
  process.stderr.write('Saved: '+outPath+'\n');

  console.log(JSON.stringify(results,null,2));
})();
