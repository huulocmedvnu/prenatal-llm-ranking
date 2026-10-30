import json
from scipy.stats import binomtest
d=json.load(open("outputs/v1_results.json"))
for tag,v in sorted(d.items()):
    pc=v["per_case"]
    for i,lab in [(2,"llm_rerank"),(3,"fusion")]:
        for t in (1,5):
            a=[r[i]<=t for r in pc]; b=[r[1]<=t for r in pc]
            g=sum(x and not y for x,y in zip(a,b)); l=sum(y and not x for x,y in zip(a,b))
            print(tag,lab,"top%d"%t,sum(a),"vs exomiser",sum(b),"gain",g,"loss",l,"p %.2g"%binomtest(g,g+l).pvalue)
