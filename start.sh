#!/usr/bin/env bash
# Use em todo boot de pod (ldconfig se perde ao reiniciar o container). Uso: bash /workspace/tiktokshop-sofii-hexx/start.sh
B=/workspace/runpod-slim/ComfyUI
PY=$B/.venv-cu128/bin/python
echo "$B/.venv-cu128/lib/python3.12/site-packages/nvidia/cu13/lib" > /etc/ld.so.conf.d/nvidia-cu13.conf && ldconfig
pkill -9 -f "main.py" 2>/dev/null; sleep 3
# videos e temporarios saem do Network Volume (disco do container, apagado ao desligar o pod: baixe o mp4 antes)
mkdir -p /tmp/comfy_out /tmp/comfy_tmp
FLAGS="--output-directory /tmp/comfy_out --temp-directory /tmp/comfy_tmp"
[ "$NOSAGE" = "1" ] || FLAGS="$FLAGS --use-sage-attention"   # NOSAGE=1 bash start.sh  -> sobe sem sage attention (GPU nova)
[ "$CACHE_NONE" = "1" ] && FLAGS="$FLAGS --cache-none"       # CACHE_NONE=1 bash start.sh -> menos RAM
cd $B && nohup $PY main.py --listen 0.0.0.0 --port 8188 --enable-cors-header $FLAGS > /tmp/comfyui.log 2>&1 &
sleep 60
curl -sI localhost:8188 | head -1
grep -i "sage\|To see the GUI" /tmp/comfyui.log | head -3
