import sys,os,json;sys.path.insert(0,'.')
import cadquery as cq
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
idx=json.load(open('work/index.json'))
def rd(n):
    s=TopoDS_Shape(); BRepTools.Read_s(s,'work/'+n+'.brep',BRep_Builder()); return cq.Shape.cast(s)
P={n:rd(n) for n in idx['names']}
X0,X1,Y0,Y1,Z0,Z1=[float(v) for v in sys.argv[1:7]]
col=cq.Solid.makeBox(X1-X0,Y1-Y0,Z1-Z0,cq.Vector(X0,Y0,Z0))
for n,s in P.items():
    bb=s.BoundingBox()
    if bb.xmax<X0 or bb.xmin>X1 or bb.ymax<Y0 or bb.ymin>Y1 or bb.zmax<Z0 or bb.zmin>Z1: continue
    try:
        c=s.intersect(col)
        if c.Volume()<1e-6: continue
        print(f"{n:32s}",end='')
        for so in (c.Solids() or [c]):
            b=so.BoundingBox(); print(f" [X{b.xmin:.2f}..{b.xmax:.2f} Y{b.ymin:.2f}..{b.ymax:.2f} Z{b.zmin:.2f}..{b.zmax:.2f}]",end='')
        print()
    except Exception as e: print(n,'err',e)
