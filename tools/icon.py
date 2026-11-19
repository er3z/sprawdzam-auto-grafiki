"""Znak Sprawdzam Auto (licznik z ptaszkiem) narysowany wektorowo z logo-pelne.svg."""
from PIL import Image, ImageDraw
INK=(17,17,17,255); RED=(200,16,46,255)
def icon(scale=8):
    # współrzędne z SVG (viewBox ikony ok. 0..120 x 0..80)
    S=scale; W,H=int(120*S),int(84*S)
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    def P(x,y): return (x*S,y*S)
    def line(pts,w,c):
        pts=[P(*p) for p in pts]; d.line(pts,fill=c,width=int(w*S),joint="curve")
        for p in pts: r=w*S/2; d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=c)
    # łuk: środek (60,72), r=52, od 180 do 360 stopni
    r=52+4.5; d.arc([P(60-r,72-r),P(60+r,72+r)],180,360,fill=INK,width=int(9*S))
    for p in [(8,72),(112,72)]: q=P(*p); rr=4.5*S; d.ellipse([q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr],fill=INK)
    line([(22,40),(30,45)],6,INK); line([(60,18),(60,28)],6,INK); line([(98,40),(90,45)],6,INK)
    line([(34,54),(54,74),(96,28)],12,RED)
    q=P(54,74); rr=7*S; d.ellipse([q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr],fill=INK)
    return im.crop(im.getbbox())
if __name__=="__main__":
    import sys
    size=int(sys.argv[2]) if len(sys.argv)>2 else 1080
    bg=(244,241,234)
    ic=icon(16); ic.thumbnail((int(size*0.64),int(size*0.64)),Image.LANCZOS)
    im=Image.new("RGB",(size,size),bg); im.paste(ic,((size-ic.width)//2,(size-ic.height)//2+int(size*0.03)),ic)
    im.save(sys.argv[1])
