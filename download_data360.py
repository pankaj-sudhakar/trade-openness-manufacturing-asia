"""Archive original WDI indicator CSVs from the World Bank Data360 file service."""
from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
import hashlib,json
ROOT=Path(__file__).resolve().parent;RAW=ROOT/'raw';RAW.mkdir(exist_ok=True)
CODES=['NV.IND.MANF.ZS','NE.TRD.GNFS.ZS','BX.KLT.DINV.WD.GD.ZS','NE.GDI.TOTL.ZS','NY.GDP.PCAP.KD','NV.IND.MANF.KD.ZG','NE.EXP.GNFS.ZS','NE.IMP.GNFS.ZS']
def fetch(code):
    url='https://data360files.worldbank.org/data360-data/data/WB_WDI/WB_WDI_'+code.replace('.','_')+'.csv'
    path=RAW/(code+'.csv')
    req=Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urlopen(req,timeout=60) as r:
        headers=dict(r.headers);raw=r.read()
    assert raw.startswith(b'STRUCTURE,'),raw[:100]
    path.write_bytes(raw)
    result={'indicator':code,'url':url,'retrieval_date':'2026-10-01','timezone':'Asia/Calcutta','http_last_modified':headers.get('Last-Modified'),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'file':path.name}
    print(code,len(raw),flush=True)
    return result
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(fetch,CODES))
    (ROOT/'data360_manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('All original indicator files archived',flush=True)
