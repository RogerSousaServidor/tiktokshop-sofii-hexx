#!/usr/bin/env bash
# Use em todo boot de pod (ldconfig se perde ao reiniciar o container). Uso: bash /workspace/tiktokshop-sofii-hexx/start.sh
B=/workspace/runpod-slim/ComfyUI
PY=$B/.venv-cu128/bin/python
echo "$B/.venv-cu128/lib/python3.12/site-packages/nvidia/cu13/lib" > /etc/ld.so.conf.d/nvidia-cu13.conf && ldconfig
pkill -9 -f "main.py" 2>/dev/null; sleep 3
cd $B && nohup $PY main.py --listen 0.0.0.0 --port 8188 --enable-cors-header --use-sage-attention > /tmp/comfyui.log 2>&1 &
sleep 60
curl -sI localhost:8188 | head -1
grep -i "sage\|To see the GUI" /tmp/comfyui.log | head -3
