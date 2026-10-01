from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=ROOT/'results';m=json.loads((R/'models.json').read_text());a=json.loads((R/'audit.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10})
regional=pd.read_csv(R/'balanced_regional_means.csv');counts=a['balanced_figure_counts']
fig,ax=plt.subplots(1,2,figsize=(10,3.5),layout='constrained')
for region,color,ls in [('South Asia','#223f65','-'),('Southeast Asia','#aa5218','--')]:
 q=regional[regional.region==region]
 for axis,col,title in [(ax[0],'trade','Trade openness'),(ax[1],'mva','Manufacturing share')]:
  axis.plot(q.year,q[col],label=f'{region} (n={counts[region]})',color=color,linestyle=ls)
  axis.set_title(title);axis.set_xlabel('Year');axis.set_ylabel('Percent of GDP');axis.grid(alpha=.2)
ax[0].legend(fontsize=8)
fig.savefig(R/'figure1.png',dpi=220);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.7),layout='constrained');labels=[];bs=[];lo=[];hi=[]
for key,term,label in [('baseline','trade','Baseline'),('lagged','L_trade','Calendar-year lags'),('differences','D_trade','Annual differences'),('core','trade','Restricted sample'),('trends','trade','Country trends')]:
 t=m[key]['terms'][term];labels.append(label);bs.append(t['b']*10);lo.append((t['b']-t['lo'])*10);hi.append((t['hi']-t['b'])*10)
ax.errorbar(bs,range(len(bs)),xerr=[lo,hi],fmt='o',color='#223f65',capsize=3);ax.set_yticks(range(len(bs)),labels);ax.invert_yaxis();ax.axvline(0,color='gray',linewidth=1)
ax.set_xlabel('Manufacturing percentage points per 10-point openness contrast');ax.grid(axis='x',alpha=.2)
fig.savefig(R/'figure2.png',dpi=220);plt.close(fig)
print('Two figures regenerated from verified model output')
