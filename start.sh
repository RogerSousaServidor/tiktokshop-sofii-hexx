#!/usr/bin/env bash
# Use em todo boot de pod (ldconfig se perde ao reiniciar o container). Uso: bash /workspace/tiktokshop-sofii-hexx/start.sh
B=${COMFY:-/workspace/runpod-slim/ComfyUI}   # COMFY=/caminho/ComfyUI bash start.sh  (outro template)
if [ -x "$B/.venv-cu128/bin/python" ]; then PY=$B/.venv-cu128/bin/python; VENV=$B/.venv-cu128
elif [ -x "$B/venv/bin/python" ]; then PY=$B/venv/bin/python; VENV=$B/venv
else PY=$(command -v python3); VENV=""; fi
[ -n "$VENV" ] && { echo "$VENV/lib/python3.12/site-packages/nvidia/cu13/lib" > /etc/ld.so.conf.d/nvidia-cu13.conf && ldconfig; }
pkill -9 -f "main.py" 2>/dev/null; sleep 3
# videos e temporarios saem do Network Volume (disco do container, apagado ao desligar o pod: baixe o mp4 antes)
mkdir -p /tmp/comfy_out /tmp/comfy_tmp
FLAGS="--output-directory /tmp/comfy_out --temp-directory /tmp/comfy_tmp"
[ "$NOSAGE" = "1" ] || FLAGS="$FLAGS --use-sage-attention"   # NOSAGE=1 bash start.sh  -> sobe sem sage attention (GPU nova)
[ "$CACHE_NONE" = "1" ] && FLAGS="$FLAGS --cache-none"       # CACHE_NONE=1 bash start.sh -> menos RAM
[ "$HIGHVRAM" = "1" ] && FLAGS="$FLAGS --highvram"          # HIGHVRAM=1 bash start.sh   -> modelos fixos na VRAM (GPU >= 80 GB: H100/H200); evita trocar alto/baixo ruido a cada segmento
cd $B && nohup $PY main.py --listen 0.0.0.0 --port 8188 --enable-cors-header $FLAGS > /tmp/comfyui.log 2>&1 &
sleep 60
curl -sI localhost:8188 | head -1
grep -i "sage\|To see the GUI" /tmp/comfyui.log | head -3
