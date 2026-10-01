"""Reproduce all estimates from archived WDI responses, without network access."""
from pathlib import Path
import json, hashlib, platform
ROOT=Path(__file__).resolve().parent
import numpy as np
import pandas as pd
import linear_backend as sm

RESULTS=ROOT/'results'; RESULTS.mkdir(exist_ok=True)
NAMES={'NV.IND.MANF.ZS':'mva','NE.TRD.GNFS.ZS':'trade','BX.KLT.DINV.WD.GD.ZS':'fdi','NE.GDI.TOTL.ZS':'gcf','NY.GDP.PCAP.KD':'gdppc','NV.IND.MANF.KD.ZG':'mva_growth','NE.EXP.GNFS.ZS':'exports','NE.IMP.GNFS.ZS':'imports'}
SA=['AFG','BGD','BTN','IND','MDV','NPL','PAK','LKA']
SEA=['BRN','KHM','IDN','LAO','MYS','MMR','PHL','SGP','THA','TLS','VNM']
COUNTRIES=SA+SEA
records=[]; country_names={}; meta={}
for code,name in NAMES.items():
    raw=(ROOT/'raw'/(code+'.csv')).read_bytes()
    frame=pd.read_csv(ROOT/'raw'/(code+'.csv'),low_memory=False)
    sub=frame.loc[frame.REF_AREA.isin(COUNTRIES)&pd.to_numeric(frame.TIME_PERIOD,errors='coerce').between(2000,2024)].copy()
    assert (sub.FREQ=='A').all()
    meta[code]={'sha256':hashlib.sha256(raw).hexdigest(),'unit':sorted(sub.UNIT_MEASURE_LABEL.dropna().unique().tolist()),'indicator':sorted(sub.INDICATOR_LABEL.unique().tolist())}
    for x in sub.to_dict('records'):
        iso=x['REF_AREA']; country_names[iso]=x['REF_AREA_LABEL']
        records.append({'iso3':iso,'year':int(x['TIME_PERIOD']),'variable':name,'value':x['OBS_VALUE']})
long=pd.DataFrame(records)
assert not long.duplicated(['iso3','year','variable']).any()
grid=pd.MultiIndex.from_product([COUNTRIES,range(2000,2025)],names=['iso3','year'])
d=long.pivot(index=['iso3','year'],columns='variable',values='value').reindex(grid).reset_index().sort_values(['iso3','year']).reset_index(drop=True)
assert len(d)==19*25
assert (d.loc[d.gdppc.notna(),'gdppc']>0).all()
d['lnincome']=np.log(d.gdppc);d['lnincome2']=d.lnincome**2
d['lntrade']=np.log(d.trade.where(d.trade>0)); d['india_trade']=d.trade*(d.iso3=='IND')
basevars=['mva','trade','fdi','gcf','lnincome']
for col in basevars:
    d['L_'+col]=d.groupby('iso3')[col].shift(1)
    d['D_'+col]=d[col]-d['L_'+col]
d['region']=np.where(d.iso3.isin(SA),'South Asia','Southeast Asia')
d['country']=d.iso3.map(country_names)
d.to_csv(ROOT/'panel_all_countries.csv',index=False)
base=d.dropna(subset=basevars).copy()
base.to_csv(ROOT/'baseline_sample.csv',index=False)
coverage=[]
for iso in COUNTRIES:
    b=base.loc[base.iso3==iso]; missing=sorted(set(range(2000,2025))-set(b.year))
    coverage.append({'iso3':iso,'country':country_names.get(iso,iso),'n':len(b),'first':int(b.year.min()) if len(b) else None,'last':int(b.year.max()) if len(b) else None,'missing_years':missing})
pd.DataFrame(coverage).to_csv(RESULTS/'coverage.csv',index=False)
d.groupby('iso3')[list(NAMES.values())].count().to_csv(RESULTS/'nonmissing_by_indicator.csv')
base[['mva','trade','fdi','gcf','gdppc']].describe(percentiles=[.25,.5,.75]).T.to_csv(RESULTS/'descriptives.csv')

MODELS={}; OBJECTS={}
def design(frame,xcols,fe=True,trends=False):
    parts=[pd.DataFrame({'const':np.ones(len(frame))},index=frame.index),frame[xcols].astype(float)]
    if fe: parts.append(pd.get_dummies(frame.iso3,prefix='country',drop_first=True,dtype=float))
    parts.append(pd.get_dummies(frame.year.astype(str),prefix='year',drop_first=True,dtype=float))
    if trends:
        # Exclude one economy trend because a common linear trend is spanned by year effects.
        td=pd.get_dummies(frame.iso3,prefix='trend',drop_first=True,dtype=float).mul(frame.year-2000,axis=0)
        parts.append(td)
    X=pd.concat(parts,axis=1)
    assert np.linalg.matrix_rank(X.to_numpy())==X.shape[1], 'Rank deficient design'
    return X
def fit(key,frame,ycol,xcols,fe=True,trends=False):
    f=frame.dropna(subset=[ycol]+xcols).copy()
    X=design(f,xcols,fe,trends); groups=pd.factorize(f.iso3)[0]
    model=sm.OLS(f[ycol].astype(float),X).fit(cov_type='cluster',cov_kwds={'groups':groups,'use_correction':True,'df_correction':True},use_t=True)
    assert int(model.df_resid_inference)==f.iso3.nunique()-1
    ci=model.conf_int(); out={'n':len(f),'g':f.iso3.nunique(),'k':X.shape[1],'r2_overall':float(model.rsquared),'df_inference':int(model.df_resid_inference),'terms':{}}
    for col in xcols:
        out['terms'][col]={'b':float(model.params[col]),'se':float(model.bse[col]),'p':float(model.pvalues[col]),'lo':float(ci.loc[col,0]),'hi':float(ci.loc[col,1])}
    # Partial R2 of all substantive regressors conditional on FE/year/trend nuisance.
    Z=X.drop(columns=xcols).to_numpy(); yy=f[ycol].to_numpy(); yr=yy-Z@np.linalg.lstsq(Z,yy,rcond=None)[0]
    out['r2_partial']=float(1-np.dot(model.resid,model.resid)/np.dot(yr,yr))
    f[['iso3','year']].to_csv(RESULTS/(key+'_sample.csv'),index=False)
    MODELS[key]=out;OBJECTS[key]=(model,X,f,groups,ycol)
    return model

xs=['trade','fdi','gcf','lnincome']
fit('baseline',d,'mva',xs)
fit('lagged',d,'mva',['L_'+x for x in xs])
fit('differences',d,'D_mva',['D_'+x for x in xs],fe=False)
fit('core',d.loc[~d.iso3.isin(['BRN','MDV','SGP'])],'mva',xs)
fit('trends',d,'mva',xs,trends=True)
fit('logtrade',d,'mva',['lntrade','fdi','gcf','lnincome'])
fit('india',d,'mva',xs+['india_trade'])
fit('income_squared',d,'mva',xs+['lnincome2'])
fit('no_pandemic',d.loc[~d.year.isin([2020,2021])],'mva',xs)
fit('fewer_controls_same_sample',base,'mva',['trade','lnincome'])
fit('growth_outcome',base,'mva_growth',xs)
fit('export_import',base,'mva',['exports','imports','fdi','gcf','lnincome'])
fit('original_frame',d.loc[~d.iso3.isin(['AFG','TLS'])],'mva',xs)
fit('original_frame_differences',d.loc[~d.iso3.isin(['AFG','TLS'])],'D_mva',['D_'+x for x in xs],fe=False)

india=OBJECTS['india'][0]
contrast=np.zeros(len(india.params));contrast[india.params.index.get_loc('trade')]=1;contrast[india.params.index.get_loc('india_trade')]=1
it=india.t_test(contrast)
MODELS['india']['combined']={'b':float(np.asarray(it.effect).item()),'se':float(np.asarray(it.sd).item()),'p':float(np.asarray(it.pvalue).item()),'lo':float(it.conf_int()[0,0]),'hi':float(it.conf_int()[0,1])}

def wild_test(key,term,B=4999,seed=20261001):
    """Null-imposed Rademacher wild-cluster bootstrap-t; CR1 studentization."""
    model,Xdf,f,groups,ycol=OBJECTS[key]
    X=Xdf.to_numpy(); y=f[ycol].to_numpy(); n,k=X.shape; G=int(groups.max()+1); j=Xdf.columns.get_loc(term)
    A=np.linalg.solve(X.T@X,X.T)
    # Check OLS computation against statsmodels' SVD implementation.
    assert np.allclose(A@y,model.params.to_numpy(),rtol=1e-6,atol=1e-7)
    Z=np.delete(X,j,axis=1); restricted=Z@np.linalg.lstsq(Z,y,rcond=None)[0]; u0=y-restricted
    corr=G/(G-1)*(n-1)/(n-k)
    infl=np.zeros((G,n))
    for g in range(G): infl[g,groups==g]=A[j,groups==g]
    se=np.sqrt(corr*np.sum((infl@np.asarray(model.resid))**2))
    assert np.isclose(se,model.bse[term],rtol=1e-6)
    observed=abs(model.params[term]/se); rng=np.random.default_rng(seed); count=0
    for start in range(0,B,250):
        nb=min(250,B-start); signs=rng.choice([-1.,1.],size=(G,nb)); Y=restricted[:,None]+u0[:,None]*signs[groups]
        betas=A@Y; residual=Y-X@betas; scores=infl@residual
        ses=np.sqrt(corr*np.sum(scores*scores,axis=0)); ts=np.abs(betas[j]/ses)
        count+=int(np.count_nonzero(ts>=observed))
    return {'p':(count+1)/(B+1),'replications':B,'seed':seed,'weights':'Rademacher','null_imposed':True}
for key,term in [('baseline','trade'),('core','trade'),('trends','trade'),('differences','D_trade'),('lagged','L_trade')]:
    MODELS[key]['wild_bootstrap']=wild_test(key,term)

loo=[]
for iso in sorted(base.iso3.unique()):
    key='leaveout_'+iso;fit(key,base.loc[base.iso3!=iso],'mva',xs)
    t=MODELS.pop(key)['terms']['trade'];loo.append({'excluded':iso,**t})
pd.DataFrame(loo).to_csv(RESULTS/'leave_one_out.csv',index=False)

# Cross-section dependence is described, not assigned an unjustified asymptotic p-value.
model,X,f,groups,ycol=OBJECTS['baseline']
# Independent Frisch-Waugh-Lovell calculation of the baseline trade slope.
Z=X.drop(columns=['trade']).to_numpy(); xx=f.trade.to_numpy(); yy=f.mva.to_numpy()
xr=xx-Z@np.linalg.lstsq(Z,xx,rcond=None)[0];yr=yy-Z@np.linalg.lstsq(Z,yy,rcond=None)[0]
assert np.isclose(float(xr@yr/(xr@xr)),model.params['trade'],atol=1e-10)
er=f[['iso3','year']].copy();er['residual']=model.resid
wide=er.pivot(index='year',columns='iso3',values='residual'); pairs=[]
for i,a in enumerate(wide.columns):
    for b in wide.columns[i+1:]:
        pair=wide[[a,b]].dropna()
        if len(pair)>=5:pairs.append({'a':a,'b':b,'T':len(pair),'r':float(pair.corr().iloc[0,1])})
pd.DataFrame(pairs).to_csv(RESULTS/'residual_cross_country_correlations.csv',index=False)
serial=[]
for iso in er.iso3.unique():
    s=er.loc[er.iso3==iso].set_index('year').residual.reindex(range(2000,2025));pair=pd.concat([s,s.shift()],axis=1).dropna()
    if len(pair)>3:serial.append({'iso3':iso,'pairs':len(pair),'r':float(pair.corr().iloc[0,1])})
pd.DataFrame(serial).to_csv(RESULTS/'residual_serial_correlations.csv',index=False)
# Driscoll-Kraay style HAC of time-aggregated scores; short T limits reliability.
dk=sm.OLS(f[ycol],X).fit(cov_type='hac-groupsum',cov_kwds={'time':pd.factorize(f.year,sort=True)[0],'maxlags':2,'use_correction':'cluster','df_correction':True},use_t=True)
MODELS['baseline']['time_hac_lag2']={'se':float(dk.bse['trade']),'p':float(dk.pvalues['trade']),'df':float(dk.df_resid_inference)}

# Verify direct annual differences by explicit self-merge, independently of group shift.
prev=d[['iso3','year']+basevars].copy();prev.year+=1
merged=d.merge(prev,on=['iso3','year'],suffixes=('','_prev'),how='left')
mask=merged[[v for x in basevars for v in [x,x+'_prev']]].notna().all(axis=1)
assert int(mask.sum())==MODELS['differences']['n']
for col in basevars:
    np.testing.assert_allclose(merged.loc[mask,'D_'+col],merged.loc[mask,col]-merged.loc[mask,col+'_prev'])
naive=len(base)-base.iso3.nunique()
audit={'baseline_n':len(base),'naive_previous_row_difference_n':naive,'valid_annual_difference_n':MODELS['differences']['n'],'gap_difference':naive-MODELS['differences']['n'],'coverage':coverage,'leaveout_range':[min(x['b'] for x in loo),max(x['b'] for x in loo)],'mean_abs_residual_cross_country_r':float(np.mean([abs(x['r']) for x in pairs])),'median_residual_serial_r':float(np.median([x['r'] for x in serial]))}
(RESULTS/'audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
(RESULTS/'models.json').write_text(json.dumps(MODELS,indent=2),encoding='utf-8')
(RESULTS/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'estimation':'NumPy OLS with explicit CR1 covariance; local linear_backend.py','raw_data':meta},indent=2),encoding='utf-8')

# Descriptive panels use countries with complete mva AND trade for the entire period.
eligible=d.groupby('iso3')[['mva','trade']].count().min(axis=1); stable=eligible[eligible==25].index.tolist()
sd=d.loc[d.iso3.isin(stable)]; regional=sd.groupby(['region','year'])[['mva','trade']].mean().reset_index()
regional.to_csv(RESULTS/'balanced_regional_means.csv',index=False)
counts={r:sd.loc[sd.region==r,'iso3'].nunique() for r in ['South Asia','Southeast Asia']}
audit['balanced_figure_countries']=stable;audit['balanced_figure_counts']=counts
(RESULTS/'audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps({'audit':audit,'models':MODELS},indent=2))
