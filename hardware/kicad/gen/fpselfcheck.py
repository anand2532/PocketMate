import re,glob,math,sys
def pads(f):
    t=open(f).read(); r=[]
    for m in re.finditer(r'\(pad "([^"]*)" (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)\s*\(size ([\d.]+) ([\d.]+)\)(?:.*?\(drill (?:oval )?([\d.]+))?.*?\(layers ([^)]*)\)',t,re.S):
        n,typ,x,y,a,w,h,dr,lay=m.groups()
        if 'Cu' not in lay and typ!='thru_hole': continue
        if typ=='np_thru_hole': continue
        x,y,w,h=map(float,(x,y,w,h))
        if a and round(float(a))%180==90: w,h=h,w
        r.append((n,x-w/2,y-h/2,x+w/2,y+h/2))
    return r
MIN=0.15; tot=0
for f in sorted(glob.glob(sys.argv[1]+'/*.kicad_mod')):
    P=pads(f); issues=[]; mg=9
    for i in range(len(P)):
        for j in range(i+1,len(P)):
            a,b=P[i],P[j]
            if a[0]==b[0] and a[0]!='': continue   # same-net pads may touch
            dx=max(b[1]-a[3],a[1]-b[3],0); dy=max(b[2]-a[4],a[2]-b[4],0)
            g=math.hypot(dx,dy) if dx>0 and dy>0 else max(dx,dy)
            ov=not(b[1]>=a[3] or a[1]>=b[3] or b[2]>=a[4] or a[2]>=b[4])
            if ov: g=-1
            mg=min(mg,g)
            if g<MIN: issues.append((a[0],b[0],round(g,3)))
    tot+=len(issues)
    print(f.split('/')[-1], 'pads',len(P),'min gap',round(mg,3),'violations',len(issues), issues[:4])
print('TOTAL violations',tot)
