"""Periksa MP4 akhir: decode, jumlah bingkai, audio, QR, subtitle, dan loop."""
from __future__ import annotations
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

FOLDER=Path(__file__).resolve().parent
AKAR=FOLDER.parents[3]
for tool in ('video-tools','presentation-tools'):
    sys.path.insert(0,str(AKAR/'.deploy-local'/tool))
import imageio_ffmpeg
import zxingcpp

FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
VIDEO=FOLDER/'Pasang_Surut_Branding_105s.mp4'
TAUTAN='https://pasang-surut.vercel.app/app'


def frame(second):
    raw=subprocess.check_output([FFMPEG,'-v','error','-ss',str(second),'-i',str(VIDEO),'-frames:v','1','-f','image2pipe','-c:v','png','-'])
    return Image.open(io.BytesIO(raw)).convert('RGB')


def main():
    frames,seconds=imageio_ffmpeg.count_frames_and_secs(str(VIDEO))
    assert frames==3150,(frames,seconds)
    assert abs(seconds-105)<.1,seconds
    info=subprocess.run([FFMPEG,'-hide_banner','-i',str(VIDEO)],capture_output=True,text=True).stderr
    assert '1920x1080' in info and '30 fps' in info and 'Video: h264' in info,info
    assert 'Audio: aac' in info and '48000 Hz, stereo' in info,info
    decode=subprocess.run([FFMPEG,'-v','error','-xerror','-i',str(VIDEO),'-map','0:v','-map','0:a','-f','null','-'],capture_output=True,text=True)
    assert decode.returncode==0,decode.stderr
    times=[4,12,20,28,35,44,54,64,77,87,98,101]
    board=Image.new('RGB',(1440,1184),'#0b1f2a')
    qr_checks=[]
    for k,t in enumerate(times):
        im=frame(t)
        assert im.size==(1920,1080)
        assert np.asarray(im).std()>12,(t,'bingkai kosong')
        board.paste(im.resize((480,270),Image.Resampling.LANCZOS),((k%3)*480,(k//3)*296))
        ImageDraw.Draw(board).text(((k%3)*480+12,(k//3)*296+272),f'{t:03}s',fill='white')
        if t in (98,101):
            for width in (1920,1280):
                check=im if width==1920 else im.resize((1280,720),Image.Resampling.LANCZOS)
                found=[b.text for b in zxingcpp.read_barcodes(check)]
                assert TAUTAN in found,(t,width,found)
                qr_checks.append(dict(second=t,width=width,url=TAUTAN))
        if t==98:im.save(FOLDER/'Poster_Branding.jpg',quality=94)
    board.save(FOLDER/'Storyboard_Branding.jpg',quality=94)
    first,last=frame(0),frame(104.966)
    loop_delta=float(np.abs(np.asarray(first,dtype=float)-np.asarray(last,dtype=float)).mean())
    assert loop_delta<1,loop_delta
    subtitles=json.loads((FOLDER/'subtitle.json').read_text(encoding='utf-8'))
    for i,s in enumerate(subtitles):
        assert 0<=s['mulai']<s['akhir']<=105,s
        if i:assert subtitles[i-1]['akhir']<=s['mulai']+.001,(subtitles[i-1],s)
    script=json.loads((FOLDER/'naskah.json').read_text(encoding='utf-8'))
    assert ' '.join(s['teks'] for s in subtitles)==' '.join(s['narasi'] for s in script['adegan'])
    loud=subprocess.run([FFMPEG,'-v','info','-i',str(VIDEO),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True)
    found=re.findall(r'\{\s*"input_i".*?\}',loud.stderr,re.S)
    assert loud.returncode==0 and found,loud.stderr[-2000:]
    meter=json.loads(found[-1])
    assert -18.5<float(meter['input_i'])<-13.5,meter
    assert float(meter['input_tp'])<-.5,meter
    report=dict(file=VIDEO.name,bytes=VIDEO.stat().st_size,sha256=hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
                duration_seconds=seconds,frames=frames,width=1920,height=1080,fps=30,codec='H.264 / yuv420p',
                audio='AAC stereo 48000 Hz',decode_errors=0,subtitles=len(subtitles),subtitle_text_matches_script=True,
                integrated_lufs=float(meter['input_i']),true_peak_dbtp=float(meter['input_tp']),
                qr=qr_checks,loop_mean_pixel_delta=loop_delta,visual_review_seconds=times,
                remaining_manual='Volume, keterbacaan dan loop pada TV/proyektor pameran perlu dicoba tim.')
    (FOLDER/'verifikasi.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
