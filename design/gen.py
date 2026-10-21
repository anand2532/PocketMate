# PocketMate wireframe generator: python3 gen.py -> svg/, png/, overview.png
import cairosvg
from PIL import Image, ImageDraw, ImageFont
THEMES={
 "dark":dict(BG="#0F1115",SURF="#1A1D23",SURF2="#252932",TX="#E8EAED",TX2="#A8AEB4",ACC="#4C8DFF",ON="#FFFFFF",LIS="#2ECC71",PROC="#F5A623",ERR="#FF5A5F",CHROME="#000000",LINE="#3A3F48"),
 "light":dict(BG="#FFFFFF",SURF="#F1F3F5",SURF2="#E2E6EA",TX="#0B0D10",TX2="#3C434B",ACC="#0B57D0",ON="#FFFFFF",LIS="#0A7A3B",PROC="#9A5B00",ERR="#C5221F",CHROME="#E2E6EA",LINE="#6B737C"),
}
C={}
def esc(s):return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def T(x,y,s,sz=20,c=None,w="400",a="start"):return f'<text x="{x}" y="{y}" font-family="{"Noto Sans Devanagari" if any("\u0900"<=ch<="\u097f" for ch in s) else "DejaVu Sans"}" font-size="{sz}" fill="{c or C["TX"]}" font-weight="{w}" text-anchor="{a}">{esc(s)}</text>'
def R(x,y,w,h,f=None,r=12,st=None):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{f or C["SURF"]}"'+(f' stroke="{st}" stroke-width="2"' if st else '')+'/>'
def btn(x,y,w,s,f=None,c=None,h=56):return R(x,y,w,h,f or C["SURF2"])+T(x+w/2,y+h/2+7,s,20,c,"600","middle")
def pri(x,y,w,s,h=56):return btn(x,y,w,s,C["ACC"],C["ON"],h)
def dng(x,y,w,s,h=56):return btn(x,y,w,s,C["SURF2"],C["ERR"],h)
def status(mic="ready",cloud=False,batt=78,chg=False):
  mc={"ready":C["SURF2"],"live":C["LIS"],"muted":C["ERR"]}[mic];ml={"ready":"MIC READY","live":"● REC","muted":"MIC MUTED"}[mic]
  bc=C["ERR"] if batt<=10 else C["PROC"] if batt<=20 else C["LIS"]
  s=R(0,0,800,40,C["CHROME"],0)+T(16,27,"09:41",18,None,"600")+R(300,8,200,24,mc,12)+T(400,26,ml,15,C["TX2"] if mic=="ready" else C["ON"],"700","middle")
  s+=(R(572,8,96,24,C["PROC"],12)+T(620,26,"CLOUD",15,C["ON"],"700","middle")) if cloud else T(668,27,"LOCAL",15,C["TX2"],"700","end")
  return s+R(684,12,60,16,C["CHROME"],4,C["TX2"])+R(686,14,int(56*batt/100),12,bc,2)+T(790,27,f"{batt}%"+("⚡" if chg else ""),14,None,"600","end")
def hints(c="",r="Action: Ask",back=True):
  return R(0,424,800,56,C["CHROME"],0)+T(16,458,"‹ Swipe from left edge: Back" if back else "",16,C["TX2"])+T(420,458,c,16,C["TX2"],"400","middle")+T(784,458,r,16,C["TX2"],"400","end")
def title(s,back=True):return (btn(16,48,56,"‹",C["SURF"]) if back else "")+T(88 if back else 16,86,s,28,None,"700")
def orb(c,lbl,sub):return f'<circle cx="400" cy="210" r="96" fill="none" stroke="{c}" stroke-width="8"/><circle cx="400" cy="210" r="64" fill="{c}" opacity="0.2"/>'+T(400,222,lbl,30,c,"700","middle")+T(400,350,sub,20,C["TX2"],"400","middle")
def dialog(t,lines,b1,b2,dest=False,h=320):
  s=R(0,40,800,384,"#000000",0).replace('/>',' opacity="0.7"/>')+R(100,64 if h>320 else 80,600,h,C["SURF"],16,C["ERR"] if dest else C["LINE"])
  y0=64 if h>320 else 80;s+=T(400,y0+50,t,24,None,"700","middle")
  for i,l in enumerate(lines):s+=T(400,y0+88+i*28,l,17,C["TX2"],"400","middle")
  return s+btn(124,y0+h-80,264,b1)+(btn(412,y0+h-80,264,b2,C["ERR"],C["ON"]) if dest else pri(412,y0+h-80,264,b2))
def screens(theme):
  C.clear();C.update(THEMES[theme]);S={}
  def add(n,b):S[n]=f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="480" viewBox="0 0 800 480"><rect width="800" height="480" fill="{C["BG"]}"/>{b}</svg>'
  # 00 onboarding
  b=status()+T(16,88,"Welcome to PocketMate",28,None,"700")+T(16,120,"Step 2 of 4 · Privacy",18,C["TX2"])
  for i,(t,s) in enumerate([("Everything stays on this device","Notes, audio, photos and search run locally."),("Mic only records while you hold Action","Hardware switch + LED show mic state."),("Cloud is OFF","Turn it on per feature later, with consent.")]):
    y=144+i*72;b+=R(16,y,768,64)+T(32,y+28,t,19,None,"700")+T(32,y+52,s,15,C["TX2"])
  add("00-onboarding",b+btn(16,364,240,"Back")+pri(528,364,256,"Continue")+hints("","Action: try a question",back=False))
  # 01 home
  tiles=["Ask","Capture","Memory","Scan text","Tasks","Privacy"]
  b=status()+T(16,88,"Good morning, Anand",28,None,"700")+T(16,116,"Next: Standup 10:00 · 3 tasks due today",18,C["TX2"])
  for i,s in enumerate(tiles):
    x=16+(i%3)*260;y=136+(i//3)*136;f=C["ACC"] if i==0 else C["SURF2"];b+=R(x,y,248,124,f,12,C["TX"] if i==2 else None)+T(x+124,y+72,s,24,C["ON"] if i==0 else C["TX"],"700","middle")
  add("01-home",b+hints("Vol ±: move focus · both: open","Action hold: Talk",back=False))
  add("02-ptt-listening",status("live")+orb(C["LIS"],"Listening","“Remind me to call the supplier at 4…”")+btn(300,368,200,"Cancel",h=48)+hints("Vol ±: speaker","Release: Send",back=False))
  add("03-processing",status()+orb(C["PROC"],"Thinking","Searching memory · on-device model")+R(250,360,300,8,C["SURF2"],4)+R(250,360,180,8,C["PROC"],4)+btn(300,376,200,"Cancel",h=44)+hints("","Action: interrupt + new ask",back=False))
  add("04-response",status()+title("Answer")+R(16,108,768,180)+T(32,144,"Reminder set: Call supplier",22,None,"700")+T(32,176,"Today 16:00 · from your voice request",18,C["TX2"])+T(32,216,"You mentioned this supplier in a note on Oct 18.",18)+R(32,232,300,40,C["SURF2"],20)+T(48,258,"Source: Voice note · Oct 18 ›",16,C["ACC"],"600")+btn(16,300,240,"Undo")+btn(272,300,240,"Edit")+pri(528,300,256,"Done")+hints("Vol ±: scroll","Action: Follow-up"))
  add("05-capture",status()+title("Capture")+btn(16,112,372,"Voice note",C["SURF"],None,140)+btn(412,112,372,"Photo (describe)",C["SURF"],None,140)+btn(16,268,372,"Typed note",C["SURF"],None,140)+btn(412,268,372,"Scan text (OCR)",C["SURF"],None,140)+hints("Vol ±: move focus","Action hold: Voice note"))
  b=status()+title("Memory")+R(88,104,696,48,C["SURF2"],24)+T(108,136,"supplier invoice",18)+R(16,164,768,72)+T(32,192,"Answer: Invoice #4471 is due Oct 30 (₹42,000).",18,None,"600")+T(32,220,"Based on 2 sources ↓",15,C["TX2"])
  for i,(t,s) in enumerate([("Scan · Invoice #4471","Oct 18 · OCR"),("Voice note · supplier call","Oct 18 · 0:42"),("Typed note · vendors","Oct 02")]):
    y=248+i*58;b+=R(16,y,768,50,C["SURF"],12,C["ACC"] if i==0 else None)+T(32,y+31,t,18)+T(768,y+31,s+"  ›",15,C["TX2"],"400","end")
  add("06-memory-search",b+hints("Vol ±: select · both: open","Action: Ask by voice"))
  add("07-memory-detail",status()+title("Voice note · Oct 18")+R(16,108,768,200)+T(32,140,"“Supplier says invoice 4471 due on the 30th,",18)+T(32,168,"42 thousand, net 15 terms…”",18)+R(32,192,736,40,C["SURF2"],20)+R(32,192,240,40,C["ACC"],20)+T(52,218,"▶ 0:14 / 0:42",16,C["ON"],"700")+T(32,270,"Source: mic · local ASR · on device · linked: 1 task",15,C["TX2"])+btn(16,320,240,"Play")+btn(272,320,240,"Edit text")+dng(528,320,256,"Delete…")+hints("Vol ±: seek 5 s","Action: Ask about this"))
  add("08-ocr-capture",status()+title("Scan text")+R(16,104,560,312,"#000000",8,C["LINE"])+''.join(R(x,y,40,6,C["ACC"],2) for x,y in [(56,144),(496,144),(56,370),(496,370)])+T(296,264,"[ camera preview ]",18,"#A8AEB4","400","middle")+pri(592,104,192,"Capture",96)+btn(592,212,192,"Flash",h=64)+btn(592,288,192,"Import",h=64)+hints("Vol ±: zoom","Action: Shutter"))
  add("09-ocr-result",status()+title("Scanned text")+R(16,104,240,240,C["SURF2"],8)+T(136,230,"[ thumb ]",16,C["TX2"],"400","middle")+R(272,104,512,240)+T(288,136,"INVOICE #4471",18,None,"700")+T(288,164,"Due: 30 Oct 2026",18)+T(288,192,"Total: ₹42,000",18)+T(288,236,"Detected: 1 date → create reminder?",15,C["PROC"],"600")+pri(16,360,240,"Save")+btn(272,360,240,"Remind")+dng(528,360,256,"Discard")+hints("Vol ±: scroll","Action: Ask about it"))
  add("09b-photo-result",status()+title("Photo")+R(16,104,320,240,C["SURF2"],8)+T(176,230,"[ photo ]",16,C["TX2"],"400","middle")+R(352,104,432,240)+T(368,136,"Looks like:",15,C["TX2"])+T(368,166,"A 4-pin JST connector on",18,None,"600")+T(368,192,"a green PCB, pin 1 marked.",18,None,"600")+T(368,232,"Tags: electronics, connector",15,C["TX2"])+T(368,262,"Analyzed on device (basic model)",15,C["TX2"])+R(368,280,400,44,C["SURF2"],22)+T(568,308,"Ask cloud for more detail…",16,C["ACC"],"600","middle")+pri(16,360,240,"Save")+btn(272,360,240,"Add note")+dng(528,360,256,"Discard")+hints("Vol ±: scroll","Action: Ask about photo"))
  b=status()+title("Tasks")+pri(624,48,160,"+ New")
  for i,(t,s,d) in enumerate([("Call supplier","Today 16:00",0),("Submit expense report","Today",0),("Review PCB rev B","Tomorrow",0),("Buy USB-C cable","Done",1)]):
    y=112+i*76;b+=R(16,y,768,64,C["SURF"],12,C["ACC"] if i==0 else None)+R(32,y+12,40,40,C["LIS"] if d else C["SURF2"],8)+T(88,y+40,t,20,C["TX2"] if d else C["TX"],"600")+T(768,y+40,s,16,C["TX2"],"400","end")
  add("10-tasks-list",b+hints("Vol ±: select · both: done","Action: Add by voice"))
  add("11-task-create",status()+title("New reminder")+R(16,108,768,56,C["SURF2"])+T(32,144,"Call supplier",20)+T(16,196,"When",16,C["TX2"])+pri(16,208,180,"Today")+btn(212,208,180,"Tomorrow")+btn(408,208,180,"16:00")+btn(604,208,180,"Repeat…")+T(16,300,"From: voice request · Oct 21 09:41",15,C["TX2"])+btn(16,340,372,"Cancel")+pri(412,340,372,"Save")+hints("Vol ±: adjust time","Action: Dictate title"))
  def kb(rows,field,lang,mode):
    b=status()+btn(16,48,56,"‹",C["SURF"])+R(88,52,696,48,C["SURF2"],8,C["ACC"])+T(104,84,field,18)
    if mode:b+=R(560,60,212,32,C["ACC"],16)+T(666,82,mode,14,C["ON"],"700","middle")
    for r,row in enumerate(rows):
      x0=[16,52,128][r]
      for i,k in enumerate(row):b+=btn(x0+i*76,108+r*62,72,k,h=56)
    return b+btn(16,232,108,"⇧",h=56)+btn(676,232,108,"⌫",h=56)+btn(16,294,108,"?123",h=56)+btn(128,294,108,lang,C["ACC"],C["ON"],56)+btn(240,294,320,"space",h=56)+pri(564,294,220,"Save",56)
  add("11b-keyboard",kb(["qwertyuiop","asdfghjkl","zxcvbnm"],"PCB rev B: swap U3 footprint|","EN | हि","")+hints("Vol ±: cursor · EN key: switch","Action hold: dictate (EN)"))
  add("11c-keyboard-hindi",kb(["qwertyuiop","asdfghjkl","zxcvbnm"],"saplaayar ko kal|","हि | EN","Phonetic (default)")+R(16,358,768,62,C["SURF"],8)+"".join(btn(24+i*170,365,162,w,C["ACC"] if i==0 else C["SURF2"],C["ON"] if i==0 else None,48) for i,w in enumerate(["कल","काल","कॉल","kal"]))+btn(712,365,64,"⌄",h=48)+hints("Vol ±: cursor","Action hold: dictate (हिंदी)"))
  add("11d-keyboard-inscript",kb([["ौ","ै","ा","ी","ू","ब","ह","ग","द","ज"],["ो","े","्","ि","ु","प","र","क","त"],["ं","म","न","व","ल","स","य"]],"सप्लायर को कॉल करना है|","हि | EN","InScript (optional)")+hints("Vol ±: cursor","Action hold: dictate (हिंदी)"))
  # 12 privacy
  b=status("muted",cloud=True)+title("Privacy")+R(16,104,768,60,C["SURF"],12,C["ERR"])+T(32,130,"Microphone MUTED (hardware switch) · LED red",18,C["ERR"],"700")+T(32,154,"No audio can be recorded. Slide switch to enable.",15,C["TX2"])
  b+=T(16,190,"Cloud permissions (off by default · remembered per feature)",16,C["TX2"],"600")
  for i,(l,v,on) in enumerate([("Ask / answers","Granted Oct 21",1),("Photo understanding","Granted Oct 20",1),("Speech-to-text","Not allowed",0),("OCR","Not allowed",0)]):
    x=16+(i%2)*388;y=200+(i//2)*64;b+=R(x,y,380,56)+T(x+16,y+26,l,17,None,"600")+T(x+16,y+46,v,14,C["PROC"] if on else C["TX2"])+(btn(x+256,y+8,112,"Revoke",C["SURF2"],C["ERR"],40) if on else T(x+364,y+36,"Off",16,C["TX2"],"600","end"))
  b+=btn(16,336,768,"Retention: Keep forever  ·  Review / export / delete data ›",h=64)
  add("12-privacy",b+hints("Vol ±: select · both: toggle","Action: disabled (muted)"))
  add("12b-cloud-consent",status()+dialog("Send this to <provider> cloud?",["Feature: Photo understanding · 1 image (~1.2 MB)","Your choice is remembered for this feature only.","Revoke anytime in Privacy › Cloud permissions.","CLOUD badge stays visible while any feature is allowed."],"Keep local","Allow",h=344)+hints("","Action: —",back=False))
  add("12c-revoke-confirm",status(cloud=True)+dialog("Revoke Photo understanding?",["Future use asks again. Local copies are kept.","Deletion request to provider:","✓ Delete request sent · 14 items (failures retried 7 days)","or ⚠ Provider doesn't support deletion — logged"],"Cancel","Revoke",dest=True,h=344)+hints("","Action: —",back=False))
  b=status(cloud=True)+title("Cloud log · Photo understanding")
  for i,(w,what,sz,st) in enumerate([("Oct 21 09:45","Delete request · 14 items","—","Retry 2/7d"),("Oct 21 09:30","1 photo (connector)","1.2 MB","OK"),("Oct 20 17:55","1 photo","1.4 MB","Timeout"),("Oct 19 11:10","1 photo","1.1 MB","OK")]):
    y=104+i*56;b+=R(16,y,768,48)+T(32,y+31,w,16,C["TX2"])+T(200,y+31,what,17)+T(640,y+31,sz,16,C["TX2"],"400","end")+T(768,y+31,st,16,C["ERR"] if st not in("OK",) else C["LIS"],"700","end")
  add("12d-cloud-log",b+T(16,340,"Log follows auto-delete (min 30 days). Deletions + failures recorded.",15,C["TX2"])+btn(16,360,372,"Export log",h=48)+dng(412,360,372,"Revoke feature…",h=48)+hints("Vol ±: scroll · chord: open item","Action: —"))
  b=status()+title("My data")
  for i,(l,v) in enumerate([("Voice notes","38 · 120 MB"),("Photos & scans","54 · 410 MB"),("Notes & tasks","212 · 2 MB"),("Cloud request log","9 entries")]):b+=R(16,104+i*50,768,44)+T(32,133+i*50,l,18)+T(768,133+i*50,v,16,C["TX2"],"400","end")
  b+=T(16,320,"Auto-delete",16,C["TX2"],"600")+pri(140,300,150,"Never",h=32).replace('y="323"','y="322"')+btn(300,300,110,"30 d",h=32)+btn(420,300,110,"90 d",h=32)+btn(540,300,110,"365 d",h=32)
  b+=btn(16,344,372,"Export (Markdown+JSON zip)")+dng(412,344,372,"Delete…")
  add("13-data-review",b+hints("Vol ±: select","Action: —"))
  b=status()+title("Export")+R(16,104,768,56)+T(32,128,"pocketmate-export-2026-10-21.zip · AES-256 encrypted",17,None,"700")+T(32,150,"Markdown + JSON + media · 532 MB",15,C["TX2"])
  b+=R(16,168,248,200,C["SURF"],12,C["ACC"])+T(32,198,"USB mass storage",18,None,"700")+T(32,226,"Connect USB-C;",15,C["TX2"])+T(32,248,"appears as a drive.",15,C["TX2"])+T(32,300,"Waiting for cable…",15,C["PROC"],"600")
  import random;rnd=random.Random(4);q=R(280,168,200,200,"#FFFFFF",8)
  for i in range(21):
    for j in range(21):
      if (i<7 and j<7) or (i<7 and j>13) or (i>13 and j<7):
        if i%7 in(0,6) or j%7 in(0,6) or (2<=i%7<=4 and 2<=j%7<=4) or (i>13 and 2<=(i-14)<=4 and 2<=j<=4):q+=R(290+j*8.5,178+i*8.5,8.5,8.5,"#000000",0)
      elif rnd.random()<0.5:q+=R(290+j*8.5,178+i*8.5,8.5,8.5,"#000000",0)
  b+=q+R(496,168,288,200)+T(512,196,"Wi-Fi (HTTPS)",18,None,"700")+T(512,222,"1 Scan QR on phone/PC",15,C["TX2"])+T(512,244,"https://pocketmate.local:8443",14,C["ACC"],"600")+T(512,268,"2 Accept self-signed cert",15,C["TX2"])+T(512,286,"  fingerprint 3F:A2:…:9C",14,C["TX2"])+T(512,310,"3 Enter PIN: 482 913",15,None,"700")+T(512,334,"Expires 10 min · 1 device",14,C["TX2"])
  b+=R(16,376,432,40,C["SURF2"],8)+T(28,402,"Pass: tiger-lotus-7319-river (shown once)",15,None,"700")+btn(456,376,104,"↻ New",h=40)+btn(568,376,112,"Choose…",h=40)+btn(688,376,96,"Stop",h=40)
  add("13b-export",b+hints("","Action: —"))
  add("14-delete-confirm",status()+dialog("Delete all voice notes?",["38 items · 120 MB · cannot be undone","Linked tasks are kept; sources removed.","Hold Delete for 1.5 s"],"Cancel","Hold to delete",dest=True)+hints("","Action: —",back=False))
  add("15-battery",status(batt=64,chg=True)+title("Battery")+R(16,104,376,240)+T(204,200,"64%",56,None,"700","middle")+T(204,240,"Charging · USB-C PD 15 W",17,C["TX2"],"400","middle")+T(204,268,"Full in ~45 min",17,C["TX2"],"400","middle")+R(408,104,376,240)+T(424,136,"Estimate: ~7 h typical use",17)+T(424,168,"Temp: 38 °C · Health: Good",17)+T(424,200,"Battery saver at 20%",17)+T(424,232,"Safe shutdown at 3%",17)+T(424,280,"Last 24 h: ▁▂▃▅▆▇█▆▅",17,C["TX2"])+btn(16,360,768,"Battery saver: Auto",h=48)+hints("","Action: Ask"))
  add("15b-low-battery",status(batt=8)+dialog("Battery low · 8%",["About 25 min left. Battery saver is on.","At 3% PocketMate saves your data and shuts down safely.","Recording in progress will be saved first."],"Dismiss","Shut down now",dest=False)+hints("","Action: Ask",back=False))
  # onboarding steps
  def ob(n,step,t,sub,body,cta="Continue"):
    add(n,status()+T(16,88,t,28,None,"700")+T(16,120,f"Step {step} of 7 · {sub}",18,C["TX2"])+''.join(f'<circle cx="{620+i*24}" cy="80" r="7" fill="{C["ACC"] if i<step else C["SURF2"]}"/>' for i in range(7))+body+(btn(16,364,240,"Back") if step>1 else "")+pri(528,364,256,cta)+hints("","Action: —",back=False))
  ob("00a-ob-welcome",1,"Welcome to PocketMate","Hello",T(400,230,"Capture anything. Find it later. Get it done.",22,None,"600","middle")+T(400,270,"Private by default — runs on this device.",18,C["TX2"],"400","middle"),"Get started")
  ob("00b-ob-language",2,"Language","Language",pri(16,150,372,"English",h=80)+btn(412,150,372,"हिंदी (Hindi)",h=80)+T(16,280,"Both keyboards and dictation are available; change anytime in Settings.",16,C["TX2"]))
  b=""
  for i,(n,s2) in enumerate([("HomeNet-5G","🔒 ▂▄▆█"),("Office","🔒 ▂▄▆"),("CafeFree","open ▂▄")]):b+=R(16,140+i*60,768,52,C["SURF"],12,C["ACC"] if i==0 else None)+T(32,172+i*60,n,18,None,"600")+T(768,172+i*60,s2,16,C["TX2"],"400","end")
  ob("00c-ob-wifi",3,"Wi-Fi","Wi-Fi (optional)",b+T(16,340,"Skip: everything core works offline.",16,C["TX2"]))
  S["00d-ob-privacy"]=S.pop("00-onboarding").replace("Step 2 of 4","Step 4 of 7")
  b=T(16,148,"All off. Allow per feature now or later (you'll be asked first).",16,C["TX2"])
  for i,l in enumerate(["Ask / answers","Speech-to-text","Photo understanding","OCR"]):
    y=164+i*48;b+=R(16,y,768,42)+T(32,y+28,l,17)+R(704,y+8,64,26,C["SURF2"],13)+f'<circle cx="{718}" cy="{y+21}" r="10" fill="{C["TX2"]}"/>'
  ob("00e-ob-cloud",5,"Cloud choices","Cloud",b)
  b=''.join(R(16+i*260,140,248,200)+T(140+i*260,190,t,20,None,"700","middle")+T(140+i*260,226,a,15,C["TX2"],"400","middle")+T(140+i*260,250,c,15,C["TX2"],"400","middle") for i,(t,a,c) in enumerate([("Action","Hold to talk · tap toggle","Double: quick note"),("Volume ±","Move / scroll","Both together: select"),("Power","Tap sleep · 2 s menu","Mic switch: hard mute")]))
  ob("00f-ob-controls",6,"Controls","Try it",b+T(400,330,"Try now: hold Action and say “hello”",18,C["LIS"],"700","middle"))
  ob("00g-ob-done",7,"You're set","Done",T(400,230,"✓ Ready",40,C["LIS"],"700","middle")+T(400,280,"Tip: double-press Action for a quick voice note.",18,C["TX2"],"400","middle"),"Go to Home")
  # settings
  b=status()+title("Settings")
  for i,(l,v) in enumerate([("Theme","Auto (light sensor)"),("Wi-Fi","HomeNet-5G"),("Bluetooth","Off"),("Language","English · हिंदी"),("Display","Brightness auto · sleep 30 s"),("About & updates","v0.3.1 · update available")]):
    x=16+(i%2)*388;y=104+(i//2)*100;b+=R(x,y,380,88,C["SURF"],12,C["ACC"] if i==0 else None)+T(x+16,y+38,l,20,None,"700")+T(x+16,y+66,v+" ›",15,C["PROC"] if "update" in v else C["TX2"])
  add("16-settings",b+hints("Vol ±: select · both: open","Action: Ask"))
  b=status()+title("Theme")
  for i,(l,v) in enumerate([("Auto","Switch by ambient light (sensor)"),("Dark","Default, best indoors / night"),("Light","High contrast, sunlight")]):b+=R(16,104+i*76,768,64,C["SURF"],12,C["ACC"] if i==0 else None)+f'<circle cx="48" cy="{136+i*76}" r="12" fill="{C["ACC"] if i==0 else C["SURF2"]}"/>'+T(76,132+i*76,l,20,None,"700")+T(76,154+i*76,v,15,C["TX2"])
  add("16b-settings-theme",b+T(16,350,"Auto switches to Light above ~2,000 lux, Dark below ~200 lux (hysteresis 10 s).",15,C["TX2"])+hints("Vol ±: select · both: choose","Action: Ask"))
  add("17-power-menu",status()+R(0,40,800,384,"#000000",0).replace('/>',' opacity="0.75"/>')+R(160,64,480,344,C["SURF"],16,C["LINE"])+T(400,108,"Power",24,None,"700","middle")+pri(184,128,432,"Shut down",60)+btn(184,196,432,"Restart",h=60)+btn(184,264,212,"Airplane",h=60)+btn(404,264,212,"Lock",h=60)+btn(184,336,432,"Cancel",h=52)+hints("Vol ±: select · both: choose","Hold Power 10 s: force off",back=False))
  add("18a-update-available",status()+title("Update")+R(16,104,768,200)+T(32,140,"PocketMate 0.4.0 available",22,None,"700")+T(32,172,"38 MB · signed by PocketMate · verified ✓",16,C["LIS"],"600")+T(32,204,"• Hindi transliteration improvements",16)+T(32,230,"• Faster memory search",16)+T(32,256,"Needs ≥ 30% battery or charger. Data is kept.",15,C["TX2"])+btn(16,320,372,"Later")+pri(412,320,372,"Install now")+hints("","Action: Ask"))
  add("18b-update-progress",status(chg=True)+T(400,150,"Installing update",28,None,"700","middle")+R(150,200,500,16,C["SURF2"],8)+R(150,200,310,16,C["ACC"],8)+T(400,250,"62% · step 2 of 3 (writing B slot)",18,C["TX2"],"400","middle")+T(400,290,"Keep device on. If interrupted, it rolls back automatically.",16,C["TX2"],"400","middle")+hints("","Controls locked",back=False))
  add("18c-update-done",status()+T(400,180,"✓ Updated to 0.4.0",30,C["LIS"],"700","middle")+T(400,224,"Restarted on new version · data intact",18,C["TX2"],"400","middle")+btn(16,320,372,"What's new")+pri(412,320,372,"Done")+hints("","Action: Ask",back=False))
  b=status()+T(16,88,"Recovery mode",28,C["PROC"],"700")+T(16,118,"Entered via Power + Vol− at boot, or after 3 failed boots",16,C["TX2"])
  for i,(l,c) in enumerate([("Boot previous version (rollback)",None),("Check & repair storage",None),("Export data to USB (encrypted)",None),("Factory reset (erase all)…","d")]):b+=(dng if c else btn)(16,136+i*68,768,l)
  add("19b-recovery-reset",status()+dialog("Factory reset — erase everything?",["Deletes all notes, audio, photos, settings.","Hold Vol− for 3 s to confirm · release to cancel","Erasing in 2…"],"Cancel","Hold Vol− (3 s)",dest=True)+R(424,366,160,4,"#fff",2)+hints("","Vol− hold: confirm",back=False))
  add("19-recovery",b+hints("Vol ±: select · both: run","Touch may be unavailable",back=False))
  add("13c-export-lockout",status()+title("Export")+R(16,104,768,240,C["SURF"],12,C["ERR"])+T(400,160,"Too many wrong PINs",26,C["ERR"],"700","middle")+T(400,200,"Wi-Fi download paused · try again in",18,C["TX2"],"400","middle")+T(400,256,"0:52",48,None,"700","middle")+T(400,300,"30 s → 1 m → 5 m → 15 m → 1 h · resets on download or new PIN · no wipe",15,C["TX2"],"400","middle")+btn(16,356,372,"New PIN + QR")+btn(412,356,372,"Stop sharing")+hints("","Action: —"))
  b=status()+title("Choose passphrase")+R(16,104,768,56,C["SURF2"],8,C["ACC"])+T(32,140,"••••••••••••••",20)+T(16,190,"Strength: Strong ✓  (min 12 characters or 4 words)",16,C["LIS"],"600")+R(16,206,768,44,C["SURF2"],8)+T(32,234,"Confirm: ••••••••••••••",18)
  add("13d-export-passphrase",b+T(16,288,"You'll need this to open the zip. PocketMate does not store it.",15,C["TX2"])+btn(16,340,372,"Use generated")+pri(412,340,372,"Use this")+hints("Vol ±: cursor","Action: —"))
  # errors
  def err(n,ic,t,lines,b1,b2,col=None):
    col=col or C["ERR"];b=status()+f'<circle cx="400" cy="130" r="44" fill="none" stroke="{col}" stroke-width="6"/>'+T(400,146,ic,44,col,"700","middle")+T(400,214,t,26,None,"700","middle")
    for i,l in enumerate(lines):b+=T(400,250+i*28,l,17,C["TX2"],"400","middle")
    add(n,b+btn(16,344,372,b1)+pri(412,344,372,b2)+hints("","Action: Ask"))
  err("20a-err-no-network","!","No network",["Offline: notes, search, OCR, tasks still work.","Cloud features and updates wait until online."],"Continue offline","Wi-Fi settings",C["PROC"])
  err("20b-err-cloud-unreachable","!","Cloud unreachable",["<provider> didn't respond within 4 s.","Answered on device instead (may be less detailed)."],"Keep local answer","Retry cloud",C["PROC"])
  err("20c-err-mic","✕","Microphone not working",["No signal from mics. Check the mute switch first.","If unmuted: restart, then run Diagnostics."],"Type instead","Run diagnostics")
  err("20d-err-camera","✕","Camera unavailable",["Camera not detected or busy.","Try again, or import an image from USB."],"Cancel","Retry")
  err("20e-err-storage-full","!","Storage almost full",["97% used (31.0 of 32 GB) · new recordings paused.","Warning shown at 90%. Largest: Photos & scans 18 GB."],"Review data","Free up space")
  err("20f-err-ocr-no-text","?","No text found",["Hold steady, fill the frame, add light.","Saved as a photo instead? Nothing is stored yet."],"Save as photo","Retake",C["PROC"])
  err("20g-err-update-failed","↺","Update failed · rolled back",["0.4.0 didn't start; restored 0.3.1. Data intact.","Error code U-207 · logged for support."],"Details","Retry later",C["PROC"])
  err("20h-err-thermal","!","Device is hot · 76 °C",["Throttled at 75 °C. Camera & charging paused.","Warm hint at 70 °C · safe shutdown at 85 °C."],"Dismiss","Battery & temp")
  # settings details
  b=status()+title("Wi-Fi")+R(16,104,768,56,C["SURF"],12,C["ACC"])+T(32,140,"HomeNet-5G · Connected",18,None,"700")+T(768,140,"▂▄▆█  192.168.1.42",15,C["TX2"],"400","end")
  for i,(n2,x) in enumerate([("Office","🔒 ▂▄▆ · saved"),("CafeFree","open ▂▄"),("Add network…","")]):b+=R(16,168+i*56,768,48)+T(32,198+i*56,n2,18)+T(768,198+i*56,x,15,C["TX2"],"400","end")
  add("16c-settings-wifi",b+R(16,344,768,64)+T(32,372,"Wi-Fi",18,None,"700")+T(32,396,"On · Airplane mode off",15,C["TX2"])+R(704,360,64,30,C["ACC"],15)+'<circle cx="752" cy="375" r="11" fill="#fff"/>'+hints("Vol ±: select · chord: open","Action: Ask"))
  b=status()+title("Bluetooth")+R(16,104,768,56)+T(32,140,"Bluetooth",18,None,"700")+R(704,117,64,30,C["ACC"],15)+'<circle cx="752" cy="132" r="11" fill="#fff"/>'+T(16,190,"Paired",16,C["TX2"],"600")
  for i,(n2,x) in enumerate([("Pixel Buds","Connected · audio"),("Keyboards","Coming in v2")]):b+=R(16,200+i*56,768,48,C["SURF"],12,C["ACC"] if i==0 else None)+T(32,230+i*56,n2,18)+T(768,230+i*56,x,15,C["TX2"],"400","end")
  add("16d-settings-bluetooth",b+pri(16,336,768,"Pair new device")+hints("Vol ±: select · chord: open","Action: Ask"))
  b=status()+title("Display")+R(16,104,768,72)+T(32,134,"Brightness · Auto",18,None,"700")+R(32,150,600,8,C["SURF2"],4)+R(32,150,380,8,C["ACC"],4)+T(768,160,"60%",16,C["TX2"],"400","end")
  for i,(l,v) in enumerate([("Screen sleep","30 s"),("Text size","Default (18)"),("Keyboard (Hindi)","Phonetic · InScript"),("Left-edge swipe back","On")]):
    x=16+(i%2)*388;y=188+(i//2)*72;b+=R(x,y,380,64)+T(x+16,y+40,l,17)+T(x+364,y+40,v+" ›",16,None,"600","end")
  add("16e-settings-display",b+hints("Vol ±: adjust · chord: next","Action: Ask"))
  b=status()+title("About")
  for i,(l,v) in enumerate([("Software","PocketMate 0.3.1 · build 2026.10.18"),("Device","CM5 4 GB · serial PM-0042"),("Storage","12.4 of 32 GB · A/B slots ~6 GB each*"),("Battery health","96% · 41 cycles"),("Legal & licenses","›")]):b+=R(16,104+i*52,768,46)+T(32,133+i*52,l,17,C["TX2"])+T(768,133+i*52,v,16,None,"600","end")
  add("16f-settings-about",b+T(16,378,"* slot size pending Software confirmation",14,C["TX2"])+hints("","Action: Ask"))
  add("03b-processing-cloud",status(cloud=True)+orb(C["PROC"],"Thinking","Asking <provider> cloud…")+R(250,360,300,8,C["SURF2"],4)+R(250,360,140,8,C["PROC"],4)+T(400,394,"Slow network · on-device answer in 2 s if no reply",15,C["PROC"],"600","middle")+hints("","Action: interrupt + new ask",back=False))
  b=status()+R(16,48,768,44,C["SURF"],10,C["PROC"])+T(32,77,"Device warm (71 °C) · may slow down soon",16,C["PROC"],"600")+R(16,100,768,44,C["SURF"],10,C["PROC"])+T(32,129,"Storage 90% full · Free up space ›",16,C["PROC"],"600")
  for i,t in enumerate(["Ask","Capture","Memory","Scan text","Tasks","Privacy"]):
    x=16+(i%3)*260;y=156+(i//3)*132;b+=R(x,y,248,120,C["ACC"] if i==0 else C["SURF2"])+T(x+124,y+68,t,24,C["ON"] if i==0 else C["TX"],"700","middle")
  add("20i-warn-banners",b+hints("Vol ±: move focus","Action hold: Talk",back=False))
  b=status()+btn(16,48,56,"‹",C["SURF"])+T(88,86,"Office",28,None,"700")+R(16,104,768,0)
  b+=R(16,104,620,56,C["SURF2"],8,C["ACC"])+T(32,140,"••••••••|",20)+btn(648,104,136,"Show")
  for r,row in enumerate(["qwertyuiop","asdfghjkl","zxcvbnm"]):
    x0=[16,52,128][r]
    for i,k in enumerate(row):b+=btn(x0+i*76,172+r*62,72,k,h=54)
  b+=btn(16,358,108,"?123",h=54)+btn(128,358,432,"space",h=54)+pri(564,358,220,"Join",54)
  add("16g-wifi-password",b+hints("Vol ±: cursor","Action: —"))
  b=status()+title("Pair earbuds")+T(16,128,"Put earbuds in pairing mode (open case, hold button).",16,C["TX2"])+R(16,140,768,0)
  for i,(n2,x) in enumerate([("Pixel Buds Pro","Earbuds · ▂▄▆"),("JBL Tune 230","Earbuds · ▂▄"),("Searching…","")]):b+=R(16,148+i*60,768,52,C["SURF"],12,C["ACC"] if i==0 else None)+T(32,180+i*60,n2,18,None if x else C["TX2"],"600")+T(768,180+i*60,x,15,C["TX2"],"400","end")
  add("16h-bt-pair-scan",b+T(16,350,"Only audio devices shown in MVP (keyboards in v2).",15,C["TX2"])+hints("Vol ±: select · chord: pair","Action: —"))
  add("16i-bt-pair-confirm",status()+dialog("Pair with Pixel Buds Pro?",["Code 482913 should match on the device (if shown).","Audio: answers & voice notes play here.","Mic stays on PocketMate (earbud mic not used)."],"Cancel","Pair")+hints("","Action: —",back=False))
  add("16j-bt-paired",status()+T(400,170,"✓ Connected",36,C["LIS"],"700","middle")+T(400,214,"Pixel Buds Pro · battery 80% · audio routed",18,C["TX2"],"400","middle")+btn(16,320,372,"Test sound")+pri(412,320,372,"Done")+hints("Vol ±: earbud volume","Action: Ask",back=False))
  b=status()+title("Free up space")+R(16,104,768,32,C["SURF2"],16)+R(16,104,698,32,C["PROC"],16)+T(400,126,"91% · 29.1 of 32 GB",15,C["ON"],"700","middle")
  for i,(l,v) in enumerate([("Photos & scans older than 1 year","6.2 GB"),("Voice-note audio (keep transcripts)","3.1 GB"),("Duplicate photos","0.8 GB"),("Cached models & logs","1.4 GB")]):b+=R(16,148+i*52,768,46)+R(28,158+i*52,26,26,C["ACC"] if i!=2 else C["SURF2"],6)+T(68,178+i*52,l,17)+T(768,178+i*52,v,16,None,"600","end")
  add("20j-free-up-space",b+btn(16,364,240,"Export first",h=48)+btn(272,364,512,"Delete selected · 10.7 GB",C["ERR"],C["ON"],48)+hints("Vol ±: select · chord: toggle","Action: —"))
  b=status()+title("Diagnostics")
  for i,(l,v,ok) in enumerate([("Microphones (2)","L ok · R no signal",0),("Speaker","Tone played ✓",1),("Camera","Autofocus ok ✓",1),("Touch","Pass ✓",1),("Battery / charger","96% health ✓",1),("Storage","eMMC ok ✓",1)]):
    x=16+(i%2)*388;y=104+(i//2)*72;b+=R(x,y,380,64,C["SURF"],12,C["ERR"] if not ok else None)+T(x+16,y+28,l,17,None,"600")+T(x+16,y+52,v,15,C["LIS"] if ok else C["ERR"])
  add("21-diagnostics",b+btn(16,330,372,"Run again",h=48)+pri(412,330,372,"Save report (local)",48)+T(16,404,"Report has no audio or personal data.",14,C["TX2"])+hints("","Action: Test mic"))
  b=status()+title("Legal & licenses")
  for i,(l,v) in enumerate([("Privacy policy","on-device copy"),("Terms of use",""),("Open-source licenses","142 packages"),("Model licenses","ASR · LLM · OCR · TTS"),("Regulatory (FCC/CE/BIS)","e-label")]):b+=R(16,104+i*60,768,52)+T(32,136+i*60,l,18)+T(768,136+i*60,v+" ›",15,C["TX2"],"400","end")
  add("16k-legal",b+hints("Vol ±: select · chord: open","Action: Ask"))
  b=status()+title("What's new in 0.4.0")
  for i,(l,v) in enumerate([("Hindi phonetic keyboard","Type “kal”, pick कल from suggestions"),("Faster memory search","~2× quicker on large libraries"),("Earbuds","Pair Bluetooth earbuds for private answers"),("Cloud log","See every request and deletion")]):b+=R(16,104+i*62,768,54)+T(32,128+i*62,l,18,None,"700")+T(32,150+i*62,v,15,C["TX2"])
  add("18d-whats-new",b+pri(528,360,256,"Got it",48)+hints("Vol ±: scroll","Action: Ask"))
  return S
LIGHT={"01-home","06-memory-search","04-response","12-privacy","16-settings"}
allpng=[]
for th in ["dark","light"]:
  for n,s in sorted(screens(th).items()):
    if th=="light" and n not in LIGHT:continue
    nm=n if th=="dark" else n+"-light"
    open(f"svg/{nm}.svg","w").write(s);cairosvg.svg2png(bytestring=s.encode(),write_to=f"png/{nm}.png");allpng.append(nm)
W,H=360,216;cols=6;rows=(len(allpng)+cols-1)//cols;sheet=Image.new("RGB",(cols*(W+16)+16,rows*(H+36)+16),"#808080");d=ImageDraw.Draw(sheet)
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",15)
for i,n in enumerate(allpng):
  im=Image.open(f"png/{n}.png").convert("RGB").resize((W,H),Image.LANCZOS);x=16+(i%cols)*(W+16);y=16+(i//cols)*(H+36);sheet.paste(im,(x,y));d.text((x,y+H+6),n,fill="#000",font=f)
sheet.save("overview.png");print(len(allpng))
