"""Narasi Indonesia, subtitle bertiming, dan musik instrumental prosedural.

Alat produksi saja. Naskah publik dikirim ke layanan TTS Edge melalui edge-tts;
tidak membaca .env atau mengirim data pribadi. Cache MP3 mencegah permintaan ulang.
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import math
import re
import subprocess
import sys
import wave
from pathlib import Path
import numpy as np

FOLDER = Path(__file__).resolve().parent
AKAR = FOLDER.parents[3]
for sub in ('voice-tools', 'video-tools'):
    sys.path.insert(0, str(AKAR / '.deploy-local' / sub))
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
NASKAH = json.loads((FOLDER / 'naskah.json').read_text(encoding='utf-8'))
CACHE = FOLDER / 'audio'
CACHE.mkdir(exist_ok=True)
KERJA = AKAR / '.deploy-local' / 'branding'
KERJA.mkdir(exist_ok=True)


async def narasi():
    import edge_tts
    for scene in NASKAH['adegan']:
        stem = CACHE / scene['id']
        cache_key = hashlib.sha256((scene['narasi'] + NASKAH['voice'] + NASKAH['rate']).encode()).hexdigest()
        js = stem.with_suffix('.json')
        if js.exists() and stem.with_suffix('.mp3').exists():
            if json.loads(js.read_text())['cache_key'] == cache_key:
                continue
        boundaries = []
        speak = edge_tts.Communicate(scene['narasi'], NASKAH['voice'],
                                     rate=NASKAH['rate'], boundary='WordBoundary')
        with stem.with_suffix('.mp3').open('wb') as f:
            async for chunk in speak.stream():
                if chunk['type'] == 'audio':
                    f.write(chunk['data'])
                elif chunk['type'] == 'WordBoundary':
                    boundaries.append({k: chunk[k] for k in ('offset', 'duration', 'text')})
        js.write_text(json.dumps(dict(cache_key=cache_key, boundaries=boundaries), ensure_ascii=False, indent=2), encoding='utf-8')
        print('narasi:', scene['id'], flush=True)


def decode(path, tempo=1.0):
    cmd = [FFMPEG, '-v', 'error', '-i', str(path)]
    if tempo != 1:
        cmd += ['-af', f'atempo={tempo:.8f}']
    cmd += ['-f', 'f32le', '-ac', '1', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.check_output(cmd), dtype='<f4').copy()


def tulis_wav(path, audio):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(audio.shape[1] if audio.ndim > 1 else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype('<i2').tobytes())


def musik(durasi):
    """Komposisi D minor 96 BPM: pad, marimba sintetis, bass dan ketukan ringan.

    Semua gelombang disintesis di sini; tidak memakai lagu, loop, atau sampel luar.
    """
    out = np.zeros((int(durasi * SR), 2), np.float32)
    rng = np.random.default_rng(24092026)
    beat = 60 / 96
    def note(midi): return 440 * 2 ** ((midi - 69) / 12)
    def add(sig, at, amp=1.0, pan=0.0):
        i = int(at * SR)
        j = min(len(out), i + len(sig))
        if i >= len(out): return
        sig = sig[:j-i] * amp
        out[i:j, 0] += sig * math.sqrt((1-pan)/2)
        out[i:j, 1] += sig * math.sqrt((1+pan)/2)
    def tone(midi, length, kind):
        t = np.arange(int(length * SR), dtype=np.float32) / SR
        f = note(midi)
        if kind == 'pad':
            env = np.minimum(t/.32, 1) * np.minimum((length-t)/.7, 1)
            return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*(f*1.002)*t)
                    + .15*np.sin(4*np.pi*f*t)) * env * .18
        env = np.minimum(t/.006, 1) * np.exp(-t*(3.5 if kind == 'pluck' else 5))
        return (np.sin(2*np.pi*f*t) + .22*np.sin(4*np.pi*f*t)) * env
    chords = [(50,57,62,65), (46,53,58,62), (53,60,65,69), (48,55,60,64)]
    for bar in range(math.ceil(durasi/(4*beat))):
        at = bar*4*beat
        chord = chords[bar % 4]
        for k, n in enumerate(chord):
            add(tone(n+12, 4*beat+.7, 'pad'), at, .12, (k-1.5)*.28)
        for b in (0, 2):
            add(tone(chord[0]-12, .65, 'bass'), at+b*beat, .24)
        # Motif renggang agar narasi tetap terdengar jelas.
        for k, b in enumerate((0, .75, 1.5, 2.5, 3.25)):
            n = chord[(k+bar//4)%4]+24
            add(tone(n, .85, 'pluck'), at+b*beat, .10, (-1)**k*.48)
        if 2 <= bar < 39:
            for b in (0, 2):
                t = np.arange(int(.23*SR), dtype=np.float32)/SR
                phase = 2*np.pi*(48*t + (75/22)*(1-np.exp(-22*t)))
                kick = np.sin(phase)*np.exp(-20*t)*np.minimum(t/.004,1)
                add(kick, at+b*beat, .20)
            for b in (1, 3):
                t = np.arange(int(.13*SR), dtype=np.float32)/SR
                noise = rng.normal(0,1,len(t)).astype(np.float32)
                clap = np.diff(noise, prepend=0)*np.exp(-40*t)*np.minimum(t/.004,1)
                add(clap, at+b*beat, .045, .15)
            for k in range(8):
                t = np.arange(int(.045*SR),dtype=np.float32)/SR
                noise = rng.normal(0,1,len(t)).astype(np.float32)
                hat = np.diff(noise,prepend=0)*np.exp(-100*t)*np.minimum(t/.002,1)
                add(hat, at+k*.5*beat, .022 if k%2 else .032, -.25)
    time = np.arange(len(out), dtype=np.float32)/SR
    fade = np.minimum(time/2,1)*np.minimum((durasi-time)/2,1)
    out *= fade[:,None]
    return out


def srt_time(t):
    ms = int(round(t*1000))
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def main():
    asyncio.run(narasi())
    durasi = NASKAH['durasi']
    voice = np.zeros(int(durasi*SR), np.float32)
    subs, segments = [], []
    for sc in NASKAH['adegan']:
        source = CACHE / (sc['id']+'.mp3')
        pcm = decode(source)
        budget = sc['akhir']-sc['mulai']-1.25
        tempo = max(1., len(pcm)/SR/budget)
        assert tempo <= 1.22, (sc['id'], 'narasi terlalu panjang', tempo)
        if tempo>1:
            pcm = decode(source,tempo)
        peak = max(float(np.max(np.abs(pcm))), .001)
        pcm *= .65/peak
        at = sc['mulai']+.55
        end = at+len(pcm)/SR
        assert end < sc['akhir']-.3, (sc['id'], end)
        i = round(at*SR)
        voice[i:i+len(pcm)] += pcm
        bounds = json.loads(source.with_suffix('.json').read_text(encoding='utf-8'))['boundaries']
        words=sc['narasi'].split()
        normalize=lambda s: re.sub(r'\W+', '', s).lower()
        assert [normalize(w) for w in words]==[normalize(b['text']) for b in bounds], ('urutan kata TTS berubah',sc['id'])
        line=[]
        for k,b in enumerate(bounds):
            if not line: start=b['offset']/1e7
            # Pakai ejaan dan tanda baca naskah, bukan metadata TTS yang polos.
            word=words[k]
            line.append(word)
            stop=(b['offset']+b['duration'])/1e7
            if word.endswith(('.', '?', '!')) or len(' '.join(line))>64 or stop-start>4 or k==len(bounds)-1:
                next_start=at+bounds[k+1]['offset']/1e7/tempo if k+1<len(bounds) else end
                subs.append(dict(mulai=at+start/tempo,akhir=min(end,next_start,at+stop/tempo+.25),teks=' '.join(line)))
                line=[]
        segments.append(dict(id=sc['id'], mulai=at,akhir=end,tempo=tempo,words=len(sc['narasi'].split())))
    music = musik(durasi)
    # Turunkan musik ketika narasi berbunyi, dengan transisi lembut 150 ms.
    block=480
    rms=np.sqrt(np.mean(voice.reshape(-1,block)**2,axis=1))
    gate=np.minimum(rms/.012,1)
    gate=np.convolve(gate,np.ones(31)/31,mode='same')
    duck=np.repeat(1-.70*gate,block)[:len(voice)]
    music*=duck[:,None]*.85
    mixed=music+voice[:,None]*.92
    peak=float(np.max(np.abs(mixed)))
    if peak>.92:mixed*=.92/peak
    tulis_wav(KERJA/'mix.wav', mixed)
    tulis_wav(KERJA/'narasi.wav', voice)
    tulis_wav(KERJA/'musik.wav', music)
    (FOLDER/'subtitle.json').write_text(json.dumps(subs,ensure_ascii=False,indent=2),encoding='utf-8')
    (FOLDER/'Pasang_Surut_Branding_ID.srt').write_text('\n\n'.join(f"{i+1}\n{srt_time(s['mulai'])} --> {srt_time(s['akhir'])}\n{s['teks']}" for i,s in enumerate(subs))+'\n',encoding='utf-8')
    info=dict(voice=NASKAH['voice'],source='Microsoft Edge TTS via edge-tts 7.2.8',music='Sintesis orisinal prosedural 96 BPM, tanpa sampel eksternal',durasi=durasi,sample_rate=SR,peak_dbfs=20*math.log10(float(np.max(np.abs(mixed)))),segments=segments,subtitles=len(subs))
    (FOLDER/'audio_manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(info,ensure_ascii=True,indent=2))

if __name__=='__main__': main()
