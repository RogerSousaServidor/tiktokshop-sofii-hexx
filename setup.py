import os
import time

# ============================================================
#  SETUP COMPLETO — RunPod Slim + ComfyUI + WAN 2.2
#  Workflows: 1A | 1B | 2
#  Autor: Roger
# ============================================================

COMFY  = "/workspace/runpod-slim/ComfyUI"
BASE   = f"{COMFY}/models"
WF_DIR = f"{COMFY}/user/default/workflows"
NODES  = f"{COMFY}/custom_nodes"
RAW    = "https://raw.githubusercontent.com/RogerSousaServidor/tiktokshop-sofii-hexx/main/workflows"

# ── CRIAR PASTAS ─────────────────────────────────────────────
for pasta in [
    f"{BASE}/diffusion_models",
    f"{BASE}/text_encoders",
    f"{BASE}/vae",
    f"{BASE}/clip_vision",
    WF_DIR,
]:
    os.makedirs(pasta, exist_ok=True)

print("📁 Pastas criadas!\n")

# ── CUSTOM NODES ─────────────────────────────────────────────
print("=" * 60)
print("📦 INSTALANDO CUSTOM NODES")
print("=" * 60)

# WanVideoWrapper — contém Wan22FunControlToVideo
wan_wrapper = f"{NODES}/ComfyUI-WanVideoWrapper"
if os.path.exists(wan_wrapper):
    print("\n⏭️  ComfyUI-WanVideoWrapper já instalado — atualizando...")
    os.system(f"cd {wan_wrapper} && git pull")
else:
    print("\n⬇️  Instalando ComfyUI-WanVideoWrapper...")
    os.system(f"cd {NODES} && git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git")

print("\n📦 Instalando dependências do WanVideoWrapper...")
os.system(f"pip install -r {wan_wrapper}/requirements.txt --break-system-packages -q")
print("✅ Custom nodes prontos!")

# ── LISTA DE MODELOS ─────────────────────────────────────────
MODELS = [
    {
        "name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "dest": f"{BASE}/text_encoders",
        "size": "4.6 GB",
        "used": "Todos"
    },
    {
        "name": "wan_2.1_vae.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
        "dest": f"{BASE}/vae",
        "size": "0.5 GB",
        "used": "Todos"
    },
    {
        "name": "wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors",
        "dest": f"{BASE}/diffusion_models",
        "size": "14.3 GB",
        "used": "1A e 2"
    },
    {
        "name": "wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors",
        "dest": f"{BASE}/diffusion_models",
        "size": "14.3 GB",
        "used": "1A e 2"
    },
    {
        "name": "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
        "dest": f"{BASE}/diffusion_models",
        "size": "14.3 GB",
        "used": "1B"
    },
    {
        "name": "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
        "dest": f"{BASE}/diffusion_models",
        "size": "14.3 GB",
        "used": "1B"
    },
    {
        "name": "clip_vision_h.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
        "dest": f"{BASE}/clip_vision",
        "size": "0.6 GB",
        "used": "1B"
    },
]

# ── LISTA DE WORKFLOWS ────────────────────────────────────────
WORKFLOWS = [
    {
        "name": "1A_divulgacao_produto_COM_referencia.json",
        "url":  f"{RAW}/1A_divulgacao_produto_COM_referencia.json",
        "desc": "Divulgação COM vídeo de referência"
    },
    {
        "name": "1B_divulgacao_produto_SEM_referencia.json",
        "url":  f"{RAW}/1B_divulgacao_produto_SEM_referencia.json",
        "desc": "Divulgação SEM vídeo de referência"
    },
    {
        "name": "2_dancinha_engajamento_seguidores.json",
        "url":  f"{RAW}/2_dancinha_engajamento_seguidores.json",
        "desc": "Dancinha pra engajamento"
    },
]

# ── FUNÇÃO DE DOWNLOAD ────────────────────────────────────────
def baixar(url, dest, nome, size=""):
    path = os.path.join(dest, nome)
    if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
        print(f"  ⏭️  Já existe: {nome} — pulando")
        return
    print(f"  ⬇️  {nome} {f'({size})' if size else ''}")
    ret = os.system(f'wget -c --show-progress "{url}" -P "{dest}"')
    if ret == 0:
        print(f"  ✅ Salvo!")
    else:
        print(f"  ❌ ERRO ao baixar {nome} — tente novamente")

# ── DOWNLOAD MODELOS ──────────────────────────────────────────
print("\n" + "=" * 60)
print("🧠 BAIXANDO MODELOS")
print("=" * 60)

total = len(MODELS)
for i, m in enumerate(MODELS, 1):
    print(f"\n[{i}/{total}] Workflow: {m['used']}")
    baixar(m["url"], m["dest"], m["name"], m["size"])

# ── DOWNLOAD WORKFLOWS ────────────────────────────────────────
print("\n" + "=" * 60)
print("🎬 BAIXANDO WORKFLOWS")
print("=" * 60)

for wf in WORKFLOWS:
    print(f"\n  → {wf['desc']}")
    baixar(wf["url"], WF_DIR, wf["name"])

# ── VERIFICAÇÃO FINAL ─────────────────────────────────────────
print("\n" + "=" * 60)
print("🔍 VERIFICANDO TUDO...")
print("=" * 60)

erros = []
ok    = []

for m in MODELS:
    path = os.path.join(m["dest"], m["name"])
    if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
        size_gb = os.path.getsize(path) / (1024**3)
        ok.append(f"  ✅ {m['name']} ({size_gb:.1f} GB)")
    else:
        erros.append(f"  ❌ FALTANDO: {m['name']}")

for wf in WORKFLOWS:
    path = os.path.join(WF_DIR, wf["name"])
    if os.path.exists(path):
        ok.append(f"  ✅ {wf['name']}")
    else:
        erros.append(f"  ❌ FALTANDO: {wf['name']}")

# Verificar custom node
if os.path.exists(wan_wrapper):
    ok.append(f"  ✅ ComfyUI-WanVideoWrapper (custom node)")
else:
    erros.append(f"  ❌ FALTANDO: ComfyUI-WanVideoWrapper")

print("\n📦 RESULTADO:\n")
for linha in ok:
    print(linha)

if erros:
    print("\n⚠️  ATENÇÃO — Arquivos com problema:\n")
    for e in erros:
        print(e)
    print("\n💡 Rode o script novamente pra tentar baixar os que faltaram.")
else:
    print(f"""
{'=' * 60}
🎉 TUDO CERTO! REINICIANDO COMFYUI...
{'=' * 60}
""")
    # Reiniciar ComfyUI pra ativar os custom nodes
    os.system("pkill -f 'main.py'")
    time.sleep(3)
    os.system(f"cd {COMFY} && nohup python main.py --listen 0.0.0.0 --port 8188 > /tmp/comfyui.log 2>&1 &")
    time.sleep(5)
    print(f"""
✅ ComfyUI reiniciado com custom nodes ativos!

🚀 Acesse: http://localhost:8188

🎬 Workflows disponíveis no menu:
   1A — Divulgação COM vídeo de referência
   1B — Divulgação SEM vídeo de referência
   2  — Dancinha pra engajamento

📸 Inputs:
   1A e 2 → Foto da modelo + Vídeo de referência
   1B     → Foto da modelo + Prompt descritivo

{'=' * 60}
""")
