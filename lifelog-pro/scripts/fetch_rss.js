const https=require('https'),http=require('http');
function fetch(url,max=3,timeout=5000){
  return new Promise(r=>{
    const mod=url.startsWith('https')?https:http;
    const req=mod.get(url,{headers:{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)','Accept':'application/rss+xml,application/xml,text/xml,text/html'},timeout},res=>{
      if(res.statusCode>=300&&res.statusCode<400&&res.headers.location){
        return fetch(res.headers.location,max,timeout).then(r);
      }
      let d='';res.on('data',c=>{d+=c;if(d.length>50000){res.destroy();const t=[];const re=/<title><!\[CDATA\[(.*?)\]\]>|<title>(.*?)<\/title>/g;let m;while((m=re.exec(d))!==null){const s=(m[1]||m[2]||'').trim();if(s&&!t.includes(s))t.push(s);if(t.length>=max+1)break;}r(t.slice(1));}});
      res.on('end',()=>{const t=[];const re=/<title><!\[CDATA\[(.*?)\]\]>|<title>(.*?)<\/title>/g;let m;while((m=re.exec(d))!==null){const s=(m[1]||m[2]||'').trim();if(s&&!t.includes(s))t.push(s);if(t.length>=max+1)break;}r(t.slice(1));});
    });
    req.on('error',e=>r(['error:'+e.message]));
    req.on('timeout',()=>{req.destroy();r(['timeout']);});
  });
}

// 2026-06-01 验证通过的新闻源
const sources=[
  // 科技 (国际)
  ['https://www.technologyreview.com/feed/','MIT Tech Review','tech'],
  ['https://www.nature.com/nature.rss','Nature','science'],
  // 科技 (国内)
  ['https://36kr.com/feed','36氪','tech_cn'],
  ['https://sspai.com/feed','少数派','tech_cn'],
  ['https://www.ithome.com/rss/','IT之家','tech_cn'],
  ['https://www.ifanr.com/feed','爱范儿','tech_cn'],
];

(async()=>{
  const ts=new Date().toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'});
  console.log('=== RSS Feed ('+ts+') ===\n');
  const results={};
  let ok=0,fail=0;
  for(const [u,n,cat] of sources){
    process.stdout.write(n+'...');
    const t=await fetch(u,3);
    const has=t.length>0&&!t[0].startsWith('error')&&!t[0].startsWith('timeout');
    if(has){ok++;results[cat]=(results[cat]||[]).concat(t.map(x=>({source:n,title:x})));}
    else fail++;
    console.log(has?' OK':' FAIL');
    if(has)t.slice(0,2).forEach(x=>console.log('  '+x.substring(0,80)));
  }
  console.log('\n=== '+ok+'/'+sources.length+' sources OK ===');
  console.log('\nJSON_OUTPUT:'+JSON.stringify(results));
})();
