"""Read-only loader for named solids in a STEP assembly (OCP/XCAF)."""
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
def _nm(l):
    a=TDataStd_Name()
    return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),a) else None
def load_named(path):
    doc=TDocStd_Document(TCollection_ExtendedString("doc"))
    r=STEPCAFControl_Reader(); r.SetNameMode(True); r.ReadFile(path); r.Transfer(doc)
    st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    labs=TDF_LabelSequence(); st.GetFreeShapes(labs); out={}
    for i in range(1,labs.Length()+1):
        top=labs.Value(i); c=TDF_LabelSequence(); st.GetComponents_s(top,c)
        for j in range(1,c.Length()+1):
            cl=c.Value(j); rl=TDF_Label(); st.GetReferredShape_s(cl,rl)
            out[_nm(cl) or _nm(rl)]=st.GetShape_s(cl)   # located
    return out
