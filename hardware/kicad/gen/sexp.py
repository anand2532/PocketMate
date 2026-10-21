import re
def parse(s):
    toks=re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',s)
    st=[[]]
    for t in toks:
        if t=='(':st.append([])
        elif t==')':x=st.pop();st[-1].append(x)
        else:st[-1].append(t)
    return st[0]
def dump(x):
    if isinstance(x,list): return '('+' '.join(dump(i) for i in x)+')'
    return x
LIB='/usr/share/kicad/symbols/'
_c={}
def lib(name):
    if name not in _c: _c[name]=parse(open(LIB+name+'.kicad_sym').read())[0]
    return _c[name]
def find(libn,sym):
    for e in lib(libn)[1:]:
        if isinstance(e,list) and e[0]=='symbol' and e[1].strip('"')==sym: return e
    raise KeyError(libn+':'+sym)
def resolved(libn,sym):
    e=find(libn,sym)
    ext=[x for x in e if isinstance(x,list) and x[0]=='extends']
    if not ext: return e
    base=resolved(libn,ext[0][1].strip('"'))
    base=[*base]; base[1]='"%s"'%sym
    props={x[1]:x for x in e if isinstance(x,list) and x[0]=='property'}
    out=[]
    for x in base:
        if isinstance(x,list) and x[0]=='property' and x[1] in props: out.append(props.pop(x[1]))
        elif isinstance(x,list) and x[0]=='symbol':
            y=list(x); y[1]=y[1].replace(base_name(x[1]),sym) ; out.append(y)
        else: out.append(x)
    return out
def base_name(n):
    n=n.strip('"'); return re.sub(r'_\d+_\d+$','',n)
def pins(libn,sym):
    e=resolved(libn,sym); r=[]
    def walk(x,unit):
        for y in x:
            if isinstance(y,list):
                if y[0]=='symbol':
                    u=int(y[1].strip('"').split('_')[-2]); walk(y,u)
                elif y[0]=='pin':
                    at=[z for z in y if isinstance(z,list) and z[0]=='at'][0]
                    nm=[z for z in y if isinstance(z,list) and z[0]=='name'][0][1].strip('"')
                    num=[z for z in y if isinstance(z,list) and z[0]=='number'][0][1].strip('"')
                    r.append(dict(num=num,name=nm,type=y[1],x=float(at[1]),y=float(at[2]),unit=unit))
    walk(e,0); return r
