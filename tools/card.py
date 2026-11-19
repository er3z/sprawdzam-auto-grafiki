import sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
ROBOTO="/usr/share/fonts/truetype/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf"
def rob(size,wdth,wght):
    from PIL import ImageFont
    ft=ImageFont.truetype(ROBOTO,size)
    try: ft.set_variation_by_axes([wght,wdth])
    except Exception: pass
    return ft
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
BG=(244,241,234); INK=(20,20,20); ACC=(200,16,46); GRID=(226,222,212)
F="/usr/share/fonts/opentype/inter/"
def f(n,s): return ImageFont.truetype(F+n,s)
def card(title,label,date,out,logo=os.path.join(HERE,"logo.png")):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    for x in range(0,W,54): d.line([(x,0),(x,H)],fill=GRID,width=1)
    for y in range(0,H,54): d.line([(0,y),(W,y)],fill=GRID,width=1)
    M=90
    d.rectangle([M,M,M+14,M+14],fill=ACC)
    d.text((M+30,M-6),f"{label.upper()}  ·  {date}",font=f("Inter-SemiBold.otf",28),fill=INK)
    # title autosize
    for size in range(118,60,-4):
        ft=rob(size,80,700); maxw=W-2*M
        words=title.split(); lines=[]; cur=""
        for w in words:
            t=(cur+" "+w).strip()
            if d.textlength(t,font=ft)<=maxw: cur=t
            else: lines.append(cur); cur=w
        lines.append(cur)
        lh=int(size*1.08)
        if len(lines)<=5: break
    y=(H-lh*len(lines))//2-40
    for ln in lines:
        d.text((M,y),ln,font=ft,fill=INK); y+=lh
    d.rectangle([M,y+30,M+120,y+38],fill=ACC)
    # logo / wordmark
    by=H-M-40
    if logo and os.path.exists(logo):
        lg=Image.open(logo).convert("RGBA"); lg.thumbnail((560,80),Image.LANCZOS); im.paste(lg,(M,H-M-lg.height+6),lg)
    else:
        d.rounded_rectangle([M,by-6,M+52,by+46],radius=10,fill=INK)
        d.line([(M+13,by+20),(M+23,by+31),(M+40,by+8)],fill=BG,width=6)
        d.text((M+70,by-2),"SPRAWDZAM AUTO",font=f("Inter-ExtraBold.otf",34),fill=INK)
    if False: d.text((W-M,by+2),"@sprawdzam_auto",font=f("Inter-Medium.otf",28),fill=(110,110,110),anchor="ra")
    im.save(out,"JPEG",quality=92)
if __name__=="__main__":
    card(*sys.argv[1:6])
