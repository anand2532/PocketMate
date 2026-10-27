import json
d=json.load(open('work/check.json'))
L=['# Release v5.1 – interference check output (auto-generated: check_release_v5.py -> make_interference_md.py)','',
f"Parts: {d['n_parts']} enclosure parts/volumes + {d['n_board']} carrier solids from the KiCad export of PocketMate.kicad_pcb (md5 126f5c6c…, read-only copy). Estimated-height boxes for parts without 3D models: {', '.join(d['est'])}.",'',
'Threshold: common volume > 0.01 mm³. CLASH = real; other classes are intended / variant / envelope pairs.','','| A | B | common mm³ | class | overlap bbox (X0,X1,Y0,Y1,Z0,Z1) |','|---|---|---|---|---|']
for r in sorted(d['clashes'],key=lambda r:(r['cls']!='CLASH',r['cls'])):
    L.append(f"| {r['a']} | {r['b']} | {r['vol']} | {r['cls']} | {r['bbox']} |")
L+=['','## Clearances < 1.0 mm','','| A | B | gap mm |','|---|---|---|']
seen=set()
for g in sorted(d['gaps'],key=lambda g:g['gap']):
    k=frozenset((g['a'],g['b']))
    if k in seen: continue
    seen.add(k); L.append(f"| {g['a']} | {g['b']} | {g['gap']} |")
open('INTERFERENCE_CHECK_release_v5.md','w').write('\n'.join(L)+'\n'); print(len(L), sum(r['cls']=='CLASH' for r in d['clashes']),'CLASH rows')
