"""OLS and CR1 inference using NumPy; no proprietary statistical software required."""
import math
import numpy as np
import pandas as pd
__version__='1.0'
def _betacf(a,b,x):
    qab=a+b;qap=a+1;qam=a-1;c=1.;d=1-qab*x/qap
    tiny=1e-300
    if abs(d)<tiny:d=tiny
    d=1/d;h=d
    for m in range(1,401):
        aa=m*(b-m)*x/((qam+2*m)*(a+2*m));d=1+aa*d;c=1+aa/c
        if abs(d)<tiny:d=tiny
        if abs(c)<tiny:c=tiny
        d=1/d;h*=d*c
        aa=-(a+m)*(qab+m)*x/((a+2*m)*(qap+2*m));d=1+aa*d;c=1+aa/c
        if abs(d)<tiny:d=tiny
        if abs(c)<tiny:c=tiny
        d=1/d;delta=d*c;h*=delta
        if abs(delta-1)<3e-14:return h
    raise ArithmeticError('Incomplete beta did not converge')
def ibeta(a,b,x):
    if x<=0:return 0.
    if x>=1:return 1.
    bt=math.exp(math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x))
    if x<(a+1)/(a+b+2):return bt*_betacf(a,b,x)/a
    return 1-bt*_betacf(b,a,1-x)/b
def p_two_sided(t,df):return ibeta(df/2,.5,df/(df+float(t)**2))
def tcrit(df):
    lo=0.;hi=100.
    for _ in range(100):
        mid=(lo+hi)/2
        if p_two_sided(mid,df)>.05:lo=mid
        else:hi=mid
    return (lo+hi)/2
class OLS:
    def __init__(self,y,X):self.y=y;self.X=X
    def fit(self,cov_type='cluster',cov_kwds=None,use_t=True):
        return Result(self.y,self.X,cov_type,cov_kwds)
class Test:
    def __init__(self,b,se,df):
        self.effect=np.array([b]);self.sd=np.array([[se]]);self.pvalue=p_two_sided(b/se,df);self.bounds=np.array([[b-tcrit(df)*se,b+tcrit(df)*se]])
    def conf_int(self):return self.bounds
class Result:
    def __init__(self,ys,Xd,kind,kw):
        X=np.asarray(Xd,dtype=float);y=np.asarray(ys,dtype=float);n,k=X.shape
        pinv=np.linalg.pinv(X);b=pinv@y;e=y-X@b;bread=pinv@pinv.T
        if kind=='cluster':
            g=np.asarray(kw['groups']);ids=np.unique(g);G=len(ids)
            scores=np.array([X[g==i].T@e[g==i] for i in ids]);meat=scores.T@scores
            corr=G/(G-1)*(n-1)/(n-k);df=G-1
        elif kind=='hac-groupsum':
            t=np.asarray(kw['time']);ts=np.unique(t);T=len(ts)
            scores=np.array([X[t==i].T@e[t==i] for i in ts]);meat=scores.T@scores
            L=kw['maxlags']
            for lag in range(1,L+1):
                lagged=scores[lag:].T@scores[:-lag];meat+=(1-lag/(L+1))*(lagged+lagged.T)
            corr=T/(T-1)*(n-1)/(n-k);df=T-1
        else:raise ValueError(kind)
        self.cov=bread@meat@bread*corr
        se=np.sqrt(np.maximum(0,np.diag(self.cov)));self.params=pd.Series(b,index=Xd.columns);self.bse=pd.Series(se,index=Xd.columns)
        self.pvalues=pd.Series([p_two_sided(x/s,df) if s else np.nan for x,s in zip(b,se)],index=Xd.columns)
        self.resid=pd.Series(e,index=Xd.index);self.rsquared=1-float(e@e)/float((y-y.mean())@(y-y.mean()))
        self.df_resid_inference=df;self.df_resid=n-k
        crit=tcrit(df);self.ci=pd.DataFrame({0:b-crit*se,1:b+crit*se},index=Xd.columns)
    def conf_int(self):return self.ci
    def t_test(self,c):return Test(float(c@self.params),float(np.sqrt(c@self.cov@c)),self.df_resid_inference)

# Distribution checks against analytic Cauchy probabilities and published t quantiles.
assert abs(p_two_sided(1,1)-.5)<1e-12
assert abs(p_two_sided(2,1)-(1-2/math.pi*math.atan(2)))<1e-12
assert abs(tcrit(15)-2.13144954556)<1e-9
assert abs(tcrit(24)-2.06389856163)<1e-9
