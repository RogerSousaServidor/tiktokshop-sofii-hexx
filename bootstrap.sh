#!/usr/bin/env bash
# Instalacao completa em pod novo (idempotente). Uso: bash /workspace/tiktokshop-sofii-hexx/bootstrap.sh
B=/workspace/runpod-slim/ComfyUI
PY=$B/.venv-cu128/bin/python
REPO=/workspace/tiktokshop-sofii-hexx
[ -x "$PY" ] || { echo "ERRO: $PY nao existe (ComfyUI/venv nao inicializado neste pod)"; exit 1; }
source $B/.venv-cu128/bin/activate
cd $REPO && git pull -q

echo "== 1/5 setup.py (custom nodes, modelos, LoRAs, FILM, workflows) =="
$PY setup.py

echo "== 2/5 dependencias Python (venv) =="
$PY -m pip install -q -r $B/custom_nodes/ComfyUI-QwenTTS/requirements.txt
$PY -m pip install -q scipy nvidia-npp sageattention
$PY -m pip install -q "torchcodec==0.10.*" --no-deps
$PY -m pip install -q "transformers==4.57.3"   # versao exigida pelo Qwen3-TTS (instalar por ultimo)

echo "== 3/5 patch LatentSync (wav via scipy + leitura de video via OpenCV) =="
$PY - <<'PYEOF'
p="/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI-LatentSync-Node/nodes.py"
s=open(p).read(); changed=False
if "_wavfile_fallback" not in s:
    old="torchaudio.save(audio_path, waveform, sample_rate)"
    if old in s:
        new=("import scipy.io.wavfile as _wavfile_fallback\n"
             "        _wav_np = waveform.clamp(-1, 1).cpu().numpy()\n"
             "        if _wav_np.ndim == 2:\n"
             "            _wav_np = _wav_np.T\n"
             "        _wavfile_fallback.write(audio_path, sample_rate, (_wav_np * 32767).astype('int16'))")
        s=s.replace(old,new); changed=True; print("patch wav aplicado")
    else: print("AVISO: linha torchaudio.save nao encontrada")
else: print("patch wav ja aplicado")
if "_read_video_cv2" not in s:
    call="io.read_video(output_video_path, pts_unit='sec')[0]"
    anchor="from typing import Optional, Dict, Any\n"
    if call in s and anchor in s:
        helper=anchor+'''
def _read_video_cv2(path):
    cap = cv2.VideoCapture(path)
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    cap.release()
    return torch.from_numpy(np.stack(frames))
'''
        s=s.replace(anchor,helper,1).replace(call,"_read_video_cv2(output_video_path)"); changed=True; print("patch video aplicado")
    else: print("AVISO: trecho de read_video nao encontrado")
else: print("patch video ja aplicado")
if changed: open(p,"w").write(s)
PYEOF

echo "== 4/5 ldconfig (NPP CUDA 13 p/ torchcodec) =="
echo "$B/.venv-cu128/lib/python3.12/site-packages/nvidia/cu13/lib" > /etc/ld.so.conf.d/nvidia-cu13.conf && ldconfig
$PY -c "import torchcodec;print('torchcodec ok',torchcodec.__version__)" 2>&1 | tail -1

echo "== 5/5 iniciando ComfyUI =="
bash $REPO/start.sh
