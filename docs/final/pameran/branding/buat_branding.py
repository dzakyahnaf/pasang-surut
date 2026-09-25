"""Motion design branding 105 detik. Sumber scene/narasi: naskah.json.

Menggunakan renderer data versi 60 detik sebagai modul. Versi lama tetap utuh.
--cuplikan menghasilkan contact sheet; --render menghasilkan MP4 bersuara.
"""
from __future__ import annotations
import argparse
import json
import math
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

FOLDER = Path(__file__).resolve().parent
AKAR = FOLDER.parents[3]
sys.path.insert(0, str(FOLDER.parent))
import buat_video as v

W,H,FPS=1920,1080,30
DATA=json.loads((FOLDER/'naskah.json').read_text(encoding='utf-8'))
C=DATA['copy']
DURASI=DATA['durasi']
SUBS=json.loads((FOLDER/'subtitle.json').read_text(encoding='utf-8')) if (FOLDER/'subtitle.json').exists() else []
KERJA=AKAR/'.deploy-local/branding'
KERJA.mkdir(parents=True,exist_ok=True)
KELUARAN=FOLDER/'Pasang_Surut_Branding_105s.mp4'


def smooth(t,a,d):return v.maju(t,a,d)
def text(im,xy,s,size=40,color='tinta-balik',alpha=1,weight=500,mono=False,anchor='la'):
    font=v.huruf('data' if mono else 'ui',(600 if weight>=600 else 400) if mono else weight,size)
    width=font.getlength(s)
    # Tidak memotong teks; kegagalan layout menghentikan produksi.
    left=xy[0]-(width if anchor[0]=='r' else width/2 if anchor[0]=='m' else 0)
    assert left >= -2 and left+width <= W+2, ('teks di luar bingkai',s,left,width)
    v.teks(ImageDraw.Draw(im,'RGBA'),xy,s,font,color,alpha,anchor=anchor)


def para(im,xy,s,width=1100,size=38,color='tinta-3',alpha=1,weight=400):
    x,y=xy
    for line in v.bungkus(s,v.huruf('ui',weight,size),width):
        text(im,(x,y),line,size,color,alpha,weight)
        y+=size*1.24
    return y


def line_reveal(im,pts,f,color='rute',width=7,alpha=1):
    pts=v.potong_lintasan(np.asarray(pts,dtype=float),min(1,max(0,f)))
    if len(pts)>1:
        ImageDraw.Draw(im,'RGBA').line([tuple(p) for p in pts],fill=v.rgba(color,alpha),width=width,joint='curve')


class Branding:
    def __init__(self):
        self.old=v.Video()
        self.scenario=self.old.d['skenario']
        self.ui=Image.open(AKAR/'docs/final/presentasi/aset/demo_08.png').convert('RGB')
        self.qr=self.old.qr.resize((444,444),Image.Resampling.NEAREST)
        self.route_layers={}
        for hour in ('8','13'):
            self.route_layers[hour]=[]
            for kind,wide in [('rute_abai_rob',v.LEBAR_ABAI),('rute_sadar_rob',v.LEBAR_RUTE)]:
                coords=self.old.d['rute'][(hour,kind)]['geometry']['coordinates']
                self.route_layers[hour].append((coords,wide,kind))

    def title(self,im,scene,t,size=104,width=1200,y=240):
        text(im,(72,148),scene['label'],25,'air-1',smooth(t,0,.5),700)
        for k,s in enumerate(scene['judul']):
            a=smooth(t,.12+k*.15,.65)
            yy=y+k*size*1.09+(1-a)*24
            text(im,(72,yy),s,size,alpha=a,weight=600)
        return y+len(scene['judul'])*size*1.09

    def schematic(self,im,t,x=1280,y=270,kind='water'):
        """Motif vektor merek, tanpa mengaku sebagai kedalaman terukur."""
        d=ImageDraw.Draw(im,'RGBA')
        a=smooth(t,.6,.7)
        for k in range(5):
            yy=y+110+k*72
            pts=[(x-40+i*6,yy+22*math.sin(i/11+t*.48+k*.52)) for i in range(90)]
            line_reveal(im,pts,smooth(t,.5+k*.08,1.2),'air-2',3,a*.65)
        route=[(x,y+360),(x+60,y+360),(x+160,y+190),(x+330,y+190),(x+440,y+60)]
        line_reveal(im,route,smooth(t,.8,2),'rute',9,a)
        for px,py in (route[0],route[-1]):
            v.lingkaran(im,px,py,14,'lambung-1','rute',3,a)
            v.lingkaran(im,px,py,5,'rute',alfa=a)
        f=(t*.13)%1
        path=v.potong_lintasan(np.asarray(route,float),f)
        if len(path):
            px,py=path[-1]
            v.lingkaran(im,px,py,7,'tinta-balik',alfa=a)

    def opening(self,im,sc,t):
        y=self.title(im,sc,t,size=112,y=270)
        para(im,(76,y+74),sc['ringkas'],1050,46,alpha=smooth(t,1.1,.6))
        self.schematic(im,t)

    def problem(self,im,sc,t):
        y=self.title(im,sc,t,size=112,y=260)
        para(im,(76,y+75),sc['ringkas'],1060,43,alpha=smooth(t,1,.6))
        d=ImageDraw.Draw(im,'RGBA')
        x,y=1340,325
        a=smooth(t,.5,.8)
        v.lingkaran(im,x+160,y+120,118,'lambung-2','lambung-3',3,a)
        for k in range(12):
            rad=k*math.pi/6
            d.line([(x+160+100*math.sin(rad),y+120-100*math.cos(rad)),(x+160+110*math.sin(rad),y+120-110*math.cos(rad))],fill=v.rgba('tinta-3',a),width=3)
        rot=.9+smooth(t,.9,3.4)*2.0
        d.line([(x+160,y+120),(x+160+70*math.sin(rot),y+120-70*math.cos(rot))],fill=v.rgba('tinta-balik',a),width=6)
        d.line([(x+160,y+120),(x+120,y+90)],fill=v.rgba('air-2',a),width=8)
        # Ilustrasi kendaraan pengiriman bergerak di atas garis jalan.
        xx=x-80+smooth(t,1.3,3.5)*60; yy=y+355
        d.rounded_rectangle((xx,yy,xx+250,yy+115),radius=6,outline=v.rgba('air-1',a),width=5)
        d.line([(xx+250,yy+30),(xx+325,yy+30),(xx+363,yy+75),(xx+363,yy+115),(xx+250,yy+115)],fill=v.rgba('air-1',a),width=5)
        for px in (xx+60,xx+292):v.lingkaran(im,px,yy+115,23,'lambung-1','tinta-balik',5,a)
        d.line([(x-100,yy+145),(x+470,yy+145)],fill=v.rgba('lambung-3',a),width=3)

    def hero(self,im,sc,t):
        y=self.title(im,sc,t,size=206,y=218)
        para(im,(80,y+25),sc['ringkas'],1100,48,alpha=smooth(t,1,.6))
        text(im,(80,840),C['tim'],29,'tinta-3',smooth(t,2,.6))
        self.schematic(im,t,x=1280,y=260)

    def application(self,im,sc,t):
        self.title(im,sc,t,size=60,y=246)
        for k,s in enumerate(sc['ringkas'].split('\n')):
            active=k==min(2,int(t/4.2))
            text(im,(76,564+k*72),s,31,'air-1' if active else 'tinta-3',smooth(t,.8+k*.3,.5),600)
        box=(552,168,1270,762)
        # Tangkapan aplikasi asli; zoom mempertahankan rasio gambar.
        z=1+.09*smooth(t,5,6)
        cx,cy=800-80*smooth(t,5,6),480+28*smooth(t,5,6)
        ww,hh=1600/z,960/z
        crop=(cx-ww/2,cy-hh/2,cx+ww/2,cy+hh/2)
        shot=self.ui.transform((box[2],box[3]),Image.Transform.EXTENT,crop,Image.Resampling.BICUBIC)
        v.tempel(im,shot,box[:2],smooth(t,.2,.6))
        d=ImageDraw.Draw(im,'RGBA')
        d.rectangle((box[0]-2,box[1]-2,box[0]+box[2]+2,box[1]+box[3]+2),outline=v.rgba('lambung-3'),width=2)
        # Sorotan kontrol untuk penjelasan, bukan rekaman klik langsung.
        phase=min(2,int(t/4.2))
        target=[(8,24,345,198),(8,234,345,290),(10,840,1590,925)][phase]
        a=.7*smooth(t,.9,.5)
        sx=box[2]/ww; sy=box[3]/hh
        x0=max(box[0],box[0]+(target[0]-crop[0])*sx)
        y0=max(box[1],box[1]+(target[1]-crop[1])*sy)
        x1=min(box[0]+box[2],box[0]+(target[2]-crop[0])*sx)
        y1=min(box[1]+box[3],box[1]+(target[3]-crop[1])*sy)
        if y1>y0:d.rectangle((x0,y0,x1,y1),outline=v.rgba('rute',a),width=3)
        text(im,(552,126),C['potret'],25,'tinta-3')

    def route(self,im,sc,t):
        # Pakai geometri sebenarnya dan data dengan waktu yang jelas.
        hour='8' if t<10 else '13'
        change=smooth(t,9.3,1.3)
        base=Image.new('RGB',(W,H),v.WARNA['lambung-1'])
        layers=[]
        if change<1:
            for coords,width,kind in self.route_layers['8']:
                f=smooth(t,1.0 if kind=='rute_abai_rob' else 2.0,1.7)
                layers.append((self.old.peta_dekat.rute(coords,width,f,putus=kind=='rute_abai_rob',warna='rute-abai' if kind=='rute_abai_rob' else 'rute'),1-change))
        if change>0:
            for coords,width,kind in self.route_layers['13']:
                if kind=='rute_sadar_rob':layers.append((self.old.peta_dekat.rute(coords,width,smooth(t,9.8,1.8)),change))
        self.old.peta(base,t,1,8,13,change,1,layers)
        self.old.titik_perjalanan(base,ImageDraw.Draw(base,'RGBA'),1)
        self.old.atribusi(ImageDraw.Draw(base,'RGBA'),1)
        crop=base.crop((560,64,1856,860)).resize((1210,743),Image.Resampling.LANCZOS)
        v.tempel(im,crop,(640,176))
        self.title(im,sc,t,size=61,y=230)
        para(im,(74,414),sc['ringkas'],535,32,'air-1')
        text(im,(74,486),'08.00 WIB' if hour=='8' else '13.00 WIB',46,'tinta-balik',mono=True,weight=600)
        ps=self.old.d['rute'][(hour,'rute_sadar_rob')]['properties']
        pb=self.old.d['rute'][(hour,'rute_abai_rob')]['properties']
        text(im,(74,573),C['rute_sadar'],32,'tinta-balik',weight=600)
        text(im,(74,622),v.angka(ps['menit']),66,'rute',mono=True,weight=600)
        text(im,(302,652),C['menit'],27,'tinta-3')
        text(im,(74,718),C['rute_biasa']+': '+v.angka(pb['menit'])+' '+C['menit'],29,'tinta-3')
        detail=(f"Estimasi maksimum {v.angka(ps['kedalaman_maks_cm'])} cm pada rute" if hour=='8' else C['kering_model'])
        para(im,(74,780),detail,525,29,'air-1')
        para(im,(74,870),C['model'],525,25,'tinta-3')
        # Pita waktu grafis agar perubahan jam terbaca dari jauh.
        text(im,(665,128),C['skenario'],25,'tinta-3')
        d=ImageDraw.Draw(im,'RGBA')
        yy=890
        v.kotak(d,(1160,824,648,75),'lambung-1',.94,6)
        text(im,(1182,844),'08.00',27,'tinta-3',mono=True)
        text(im,(1760,844),'13.00',27,'tinta-3',mono=True,anchor='ra')
        d.line([(1310,861),(1630,861)],fill=v.rgba('lambung-3'),width=4)
        v.lingkaran(im,1310+320*change,861,9,'rute')

    def impact(self,im,sc,t):
        self.title(im,sc,t,size=100,y=212)
        delta=self.scenario['8']['selisih']
        for k,(n,key,label) in enumerate([(delta['menit'],'menit',C['menit']),(delta['km'],'km',C['km'])]):
            x=1090; y=246+k*224
            a=smooth(t,.6+k*.5,.65)
            text(im,(x,y),'+'+v.angka(n,1 if key=='menit' else 2),113,'rute',a,600,True)
            text(im,(x,y+130),label,33,'tinta-3',a)
        para(im,(76,534),sc['ringkas'],850,43,'air-1',smooth(t,1,.6))
        para(im,(76,696),C['dampak_konteks'],900,28,alpha=smooth(t,1.6,.6))
        para(im,(76,798),C['batas_bbm'],1700,32,alpha=smooth(t,2,.6))
        para(im,(76,855),C['batas_waktu'],1650,26,alpha=smooth(t,2,.6))
        d=ImageDraw.Draw(im,'RGBA')
        d.line([(1020,252),(1020,707)],fill=v.rgba('lambung-3'),width=2)

    def method(self,im,sc,t):
        self.title(im,sc,t,size=90,y=200)
        d=ImageDraw.Draw(im,'RGBA')
        for k,(name,desc) in enumerate(zip(C['metode'],C['metode_keterangan'])):
            x=88+k*458; y=590
            a=smooth(t,.8+k*.6,.65)
            if k<3:line_reveal(im,[(x+42,y+42),(x+420,y+42)],smooth(t,1+k*.6,.8),'lambung-3',3,a)
            v.lingkaran(im,x+24,y+42,25,'lambung-2','air-2',2,a)
            text(im,(x+24,y+42),str(k+1),25,'air-1',a,600,True,'mm')
            text(im,(x,y+112),name,40,'tinta-balik',a,600)
            text(im,(x,y+173),desc,29,'tinta-3',a)
        para(im,(80,860),C['bukan_sensor'],1730,30,alpha=smooth(t,3,.6))

    def roadmap(self,im,sc,t):
        self.title(im,sc,t,size=100,y=230)
        for k,name in enumerate(C['lanjut']):
            yy=290+k*174; x=1160
            a=smooth(t,.6+k*.6,.6)
            text(im,(x,yy),f'0{k+1}',29,'air-2',a,600,True)
            para(im,(x+85,yy-6),name,600,45,'tinta-balik',a,600)
        para(im,(76,788),C['roadmap'],1650,32,alpha=smooth(t,2.2,.5))
        para(im,(76,860),C['batas'],1650,30,alpha=smooth(t,2.5,.5))

    def closing(self,im,sc,t):
        text(im,(76,156),sc['label'],28,'air-1',smooth(t,0,.6),700)
        text(im,(76,304),'PASANG SURUT',128,alpha=smooth(t,.2,.7),weight=700)
        para(im,(80,486),DATA['tagline'],1010,53,'tinta-balik',smooth(t,.7,.7),500)
        para(im,(80,649),sc['ringkas'],1040,46,'air-1',smooth(t,1,.6),600)
        text(im,(80,816),C['tim'],29,'tinta-3',smooth(t,1.5,.6))
        text(im,(80,875),C['batas'],28,'tinta-3',smooth(t,2,.6))
        d=ImageDraw.Draw(im,'RGBA')
        a=smooth(t,.3,.6)
        v.kotak(d,(1260,242,508,508),'dek-1',a,6)
        v.tempel(im,self.qr,(1292,274),a)
        text(im,(1514,789),C['cta'],37,'tinta-balik',a,600,anchor='ma')
        text(im,(1514,849),C['url'],25,'tinta-3',a,400,True,'ma')

    def frame(self,t):
        sc=next((s for s in DATA['adegan'] if s['mulai']<=t<s['akhir']),DATA['adegan'][-1])
        elapsed=t-sc['mulai']; length=sc['akhir']-sc['mulai']
        im=Image.new('RGB',(W,H),v.WARNA['lambung-1'])
        funcs={'pembuka':self.opening,'masalah':self.problem,'brand':self.hero,'aplikasi':self.application,'rute':self.route,'dampak':self.impact,'metode':self.method,'lanjut':self.roadmap,'penutup':self.closing}
        funcs[sc['id']](im,sc,elapsed)
        # Pudar singkat pada pergantian adegan.
        a=min(1,elapsed/.25,max(0,(length-elapsed)/.25))
        if a<1:im=Image.blend(Image.new('RGB',(W,H),v.WARNA['lambung-1']),im,a)
        d=ImageDraw.Draw(im,'RGBA')
        text(im,(72,42),C['brand_kecil'],31,weight=700)
        text(im,(1848,49),C['acara'],21,'tinta-3',mono=True,anchor='ra')
        d.line([(72,104),(1848,104)],fill=v.rgba('lambung-3'),width=2)
        # Subtitle menyatu dalam gambar, di area khusus maksimal dua baris.
        sub=next((s for s in SUBS if s['mulai']<=t<s['akhir']),None)
        if sub:
            lines=v.bungkus(sub['teks'],v.huruf('ui',500,35),1720)
            assert len(lines)<=2, ('subtitle terlalu panjang',sub)
            y=974 if len(lines)==1 else 951
            for s in lines:
                text(im,(W/2,y),s,35,'tinta-balik',weight=500,anchor='ma')
                y+=43
        # Penanda kemajuan adegan tanpa angka hitung mundur.
        for k,s in enumerate(DATA['adegan']):
            x=72+1776*s['mulai']/DURASI
            width=1776*(s['akhir']-s['mulai'])/DURASI-4
            d.line([(x,1040),(x+width,1040)],fill=v.rgba('lambung-3'),width=3)
            progress=max(0,min(1,(t-s['mulai'])/(s['akhir']-s['mulai'])))
            if progress:d.line([(x,1040),(x+width*progress,1040)],fill=v.rgba('air-2'),width=3)
        fade=min(1,t/.4,max(0,(DURASI-1/FPS-t)/.5))
        if fade<1:im=Image.blend(Image.new('RGB',(W,H),v.WARNA['lambung-1']),im,fade)
        return im


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cuplikan',action='store_true')
    p.add_argument('--render',action='store_true')
    args=p.parse_args()
    movie=Branding()
    if args.cuplikan:
        times=[4,12,20,28,35,44,54,64,77,87,98,101]
        board=Image.new('RGB',(1440,4*296),v.WARNA['lambung-1'])
        for k,t in enumerate(times):
            frame=movie.frame(t)
            frame.save(KERJA/f'frame_{t:03}.png')
            thumb=frame.resize((480,270),Image.Resampling.LANCZOS)
            board.paste(thumb,((k%3)*480,(k//3)*296))
            ImageDraw.Draw(board).text(((k%3)*480+12,(k//3)*296+272),f'{t:03}s',fill='white',font=v.huruf('data',400,16))
        board.save(FOLDER/'Storyboard_Branding.jpg',quality=92)
        print('storyboard:',FOLDER/'Storyboard_Branding.jpg',flush=True)
    if args.render:
        import imageio_ffmpeg
        ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
        mix=KERJA/'mix.wav'
        assert mix.exists(),'buat_audio.py dahulu'
        cmd=[ffmpeg,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
             '-i',str(mix),'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','18','-tune','animation',
             '-pix_fmt','yuv420p','-profile:v','high','-level:v','4.1','-c:a','aac','-b:a','192k',
             '-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar','48000','-movflags','+faststart','-t',str(DURASI),str(KELUARAN)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        start=time.perf_counter()
        try:
            for i in range(round(DURASI*FPS)):
                proc.stdin.write(movie.frame(i/FPS).tobytes())
                if i%150==0:print(f'render {i}/{DURASI*FPS} · {time.perf_counter()-start:.1f}s',flush=True)
        finally:
            proc.stdin.close()
        assert proc.wait()==0,'encoder gagal'
        print('video:',KELUARAN,'bytes:',KELUARAN.stat().st_size,flush=True)

if __name__=='__main__':main()
