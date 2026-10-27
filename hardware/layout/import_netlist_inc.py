# Incremental netlist import (re-link by reference): updates values, paths, DNP and pad nets of existing footprints; adds new ones.
import pcbnew as P, re, sys
K='/workspace/pocketmate/hardware/kicad'; SYS='/usr/share/kicad/footprints'
B=P.LoadBoard(K+'/PocketMate.kicad_pcb'); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
s=open(K+'/PocketMate.net').read()
comps=[]
for m in re.finditer(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)(.*?)\(sheetpath \(names "([^"]*)"\) \(tstamps "([^"]*)"\)\)\s*\(tstamps "([^"]*)"\)',s,re.S):
    ref,val,body,sh,tp,u=m.groups(); fp=re.search(r'\(footprint "([^"]*)"\)',body).group(1)
    if ref=='SW1' and sh=='/Audio/': ref='SW5'
    comps.append((ref,val,fp,sh,tp+u,bool(re.search(r'\(property \(name "dnp"\)',body))))
nets={}
for m in re.finditer(r'\(net \(code "?(\d+)"?\) \(name "([^"]*)"\)(.*?)\)\s*\)\s*(?=\(net |\)\s*\)\s*$)',s,re.S):
    for r,p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"',m.group(3)):
        nets.setdefault(r,{})[p]=m.group(2)
# SW1 duplicate handling: netlist node refs for audio SW1 cannot be distinguished here; keep existing SW5 nets
ex={f.GetReference():f for f in B.GetFootprints()}
added=[];changed=[]
for ref,val,fpid,sh,path,dnp in comps:
    if sh=='/SideFlex/': continue
    if ref in ex: f=ex[ref]
    else:
        lib,name=fpid.split(':'); f=P.FootprintLoad(f'{SYS}/{lib}.pretty',name); f.SetFPID(P.LIB_ID(lib,name)); f.SetReference(ref); B.Add(f); added.append(ref)
        f.SetPosition(V(9,-7.5))
    f.SetValue(val); f.SetPath(P.KIID_PATH(path)); f.SetDNP(dnp)
    if ref=='J14': f.SetExcludedFromBOM(False); f.SetExcludedFromPosFiles(False)
    if ref=='SW5': continue
    for pad in f.Pads():
        n=nets.get(ref,{}).get(pad.GetNumber())
        if not n: continue
        if pad.GetNetname()!=n:
            ni=B.FindNet(n)
            if ni is None: ni=P.NETINFO_ITEM(B,n); B.Add(ni)
            changed.append((ref,pad.GetNumber(),pad.GetNetname(),n)); pad.SetNet(ni)
P.SaveBoard(K+'/PocketMate.kicad_pcb',B)
print('added',added); print('changed',len(changed)); [print(' ',c) for c in changed]
