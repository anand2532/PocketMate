import sys,os,json;sys.path.insert(0,'.')
import cadquery as cq
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
from stepio import load_named
idx=json.load(open('work/index.json'))
def rd(n):
    s=TopoDS_Shape(); BRepTools.Read_s(s,'work/'+n+'.brep',BRep_Builder()); return cq.Shape.cast(s)
P={n:rd(n) for n in idx['names']}
for k,s in load_named('ref/carrier_kicad_export_126f5c6c.step').items():
    P['PCB:'+(k if not k.startswith('=>') else 'CarrierBoard')]=cq.Shape.cast(s).translate(cq.Vector(0,0,9.94))
col=cq.Solid.makeBox(9,13.5,30,cq.Vector(-7.5,-13.25,-5))
for n,s in P.items():
    bb=s.BoundingBox()
    if bb.xmax<-7.5 or bb.xmin>1.5 or bb.ymax<-13.25 or bb.ymin>0.25: continue
    try:
        c=s.intersect(col); 
        if c.Volume()<1e-6: continue
        b=c.BoundingBox(); print(f"{n:35s} X{b.xmin:7.2f}..{b.xmax:6.2f} Y{b.ymin:7.2f}..{b.ymax:6.2f} Z{b.zmin:6.2f}..{b.zmax:6.2f}")
    except Exception as e: print(n,'err',e)
