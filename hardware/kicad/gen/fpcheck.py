import re,glob,os,sys
K='/workspace/pocketmate/hardware/kicad'
libs={}
for l in re.findall(r'\(name "([^"]+)"\)\s*\(type "KiCad"\)\s*\(uri "([^"]+)"',open(K+'/fp-lib-table').read()):
    libs[l[0]]=l[1].replace('${KIPRJMOD}',K)
for d in glob.glob('/usr/share/kicad/footprints/*.pretty'): libs.setdefault(os.path.basename(d)[:-7],d)
bad=0;n=0
for f in glob.glob(K+'/*.kicad_sch'):
    for fp in re.findall(r'\(property "Footprint" "([^"]*)"',open(f).read()):
        if not fp: continue
        n+=1; lib,_,name=fp.partition(':')
        if lib not in libs or not os.path.exists(f'{libs[lib]}/{name}.kicad_mod'): bad+=1; print('BAD',os.path.basename(f),fp)
print(f'checked {n} footprint fields, {bad} unresolved')
