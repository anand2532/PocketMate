export PYTHONHASHSEED=0; cd /workspace/pocketmate/hardware/layout && cp ../kicad/PocketMate.kicad_pcb.pre_netlist_v2.bak ../kicad/PocketMate.kicad_pcb && timeout 600 python3 import_netlist_v2.py && python3 outline_v4_22b.py && python3 place_j11_group.py && python3 route_usb.py 2>&1|tail -1 && python3 place_passives.py && cd ../kicad && kicad-cli pcb drc --schematic-parity --output /tmp/drc.txt PocketMate.kicad_pcb | tail -3; grep -oE '^\[[a-z_]+\]' /tmp/drc.txt | sort | uniq -c; python3 - <<'P'
import re
t=open('/tmp/drc.txt').read()
for b in re.split(r'\n(?=\[)',t):
    k=re.match(r'\[([a-z_]+)\]',b)
    if k and k.group(1) in('clearance','copper_edge_clearance','shorting_items','courtyards_overlap','items_not_allowed','skew_out_of_range','missing_footprint','hole_clearance','solder_mask_bridge'):
        print(k.group(1),sorted(set(re.findall(r'(?:of|Footprint) ([A-Z_]+[0-9]*)',b))),re.findall(r"area '([^']+)'",b)[:1], re.findall(r'@\(([-0-9.]+ mm, [-0-9.]+ mm)',b)[:1])
P
