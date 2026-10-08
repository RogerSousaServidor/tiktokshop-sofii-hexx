import os
import time

# ============================================================
#  SETUP COMPLETO — RunPod Slim + ComfyUI + WAN 2.2
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

CUSTOM_NODES = [
    {
        "name": "ComfyUI-WanVideoWrapper",
        "repo": "https://github.com/kijai/ComfyUI-WanVideoWrapper.git",
        "desc": "WAN 2.2 Fun Control + I2V"
    },
    {
        "name": "ComfyUI-QwenTTS",
        "repo": "https://github.com/1038lab/ComfyUI-QwenTTS.git",
        "desc": "Voice Clone + TTS (voz da Sofii)"
    },
    {
        "name": "ComfyUI-LatentSync-Node",
        "repo": "https://github.com/iVideoGameBoss/ComfyUI-LatentSync-Node.git",
        "desc": "Lip Sync (sincroniza a boca)"
    },
]

for node in CUSTOM_NODES:
    path = f"{NODES}/{node['name']}"
    print(f"\n→ {node['name']} ({node['desc']})")
    if os.path.exists(path):
        print(f"  ⏭️  Já instalado — atualizando...")
        os.system(f"cd {path} && git pull")
    else:
        print(f"  ⬇️  Instalando...")
        os.system(f"cd {NODES} && git clone {node['repo']}")
    req = f"{path}/requirements.txt"
    if os.path.exists(req):
        print(f"  📦 Instalando dependências...")
        os.system(f"pip install -r {req} --break-system-packages -q")
    print(f"  ✅ Pronto!")

# ── MODELOS ──────────────────────────────────────────────────
MODELS = [
    # COMPARTILHADOS
    {
        "name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "dest": f"{BASE}/text_encoders",
        "size": "4.6 GB", "used": "Todos"
    },
    {
        "name": "wan_2.1_vae.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
        "dest": f"{BASE}/vae",
        "size": "0.5 GB", "used": "Todos"
    },
    {
        "name": "clip_vision_h.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
        "dest": f"{BASE}/clip_vision",
        "size": "0.6 GB", "used": "T2V + 1B"
    },
    # FUN CONTROL (1A, 2, 3 cenas)
    {
        "name": "wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors",
        "dest": f"{BASE}/diffusion_models",
        "size": "14.3 GB", "used": "1A, 2 e 3 Cenas"
    },
    {
        "name": "wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors",
        "dest": f"{BASE}/diffusion_models",
        "size": "14.3 GB", "used": "1A, 2 e 3 Cenas"
    },
    # I2V (1B e T2V)
    {
        "name": "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
        "dest": f"{BASE}/diffusion_models",
        "size": "14.3 GB", "used": "1B e T2V"
    },
    {
        "name": "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
        "dest": f"{BASE}/diffusion_models",
        "size": "14.3 GB", "used": "1B e T2V"
    },
]

# ── WORKFLOWS ─────────────────────────────────────────────────
WORKFLOWS = [
    {
        "name": "1A_divulgacao_produto_COM_referencia.json",
        "url":  f"{RAW}/1A_divulgacao_produto_COM_referencia.json",
        "desc": "Divulgação COM vídeo de referência (Fun Control)"
    },
    {
        "name": "1B_divulgacao_produto_SEM_referencia.json",
        "url":  f"{RAW}/1B_divulgacao_produto_SEM_referencia.json",
        "desc": "Divulgação SEM vídeo de referência (I2V)"
    },
    {
        "name": "2_dancinha_engajamento_seguidores.json",
        "url":  f"{RAW}/2_dancinha_engajamento_seguidores.json",
        "desc": "Dancinha pra engajamento"
    },
    {
        "name": "tiktok_3_cenas_ids_reais.json",
        "url":  f"{RAW}/tiktok_3_cenas_ids_reais.json",
        "desc": "3 Cenas COM CHAINING: Gancho + Corpo + CTA (ultimo frame automatico)"
    },
    {
        "name": "wan22_t2v_foto_voz.json",
        "url":  f"{RAW}/wan22_t2v_foto_voz.json",
        "desc": "T2V: Foto + Prompt + Voz + LipSync"
    },
    {
        "name": "tiktok_3_cenas_chaining.json",
        "url":  f"{RAW}/tiktok_3_cenas_chaining.json",
        "desc": "3 Cenas COM CHAINING automatico"
    },
]

# ── DOWNLOAD ──────────────────────────────────────────────────
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
        print(f"  ❌ ERRO ao baixar {nome}")

print("\n" + "=" * 60)
print("🧠 BAIXANDO MODELOS")
print("=" * 60)

for i, m in enumerate(MODELS, 1):
    print(f"\n[{i}/{len(MODELS)}] Workflow: {m['used']}")
    baixar(m["url"], m["dest"], m["name"], m["size"])

print("\n" + "=" * 60)
print("🎬 BAIXANDO WORKFLOWS")
print("=" * 60)

for wf in WORKFLOWS:
    print(f"\n  → {wf['desc']}")
    baixar(wf["url"], WF_DIR, wf["name"])

# ── VERIFICAÇÃO ───────────────────────────────────────────────
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

for node in CUSTOM_NODES:
    if os.path.exists(f"{NODES}/{node['name']}"):
        ok.append(f"  ✅ {node['name']}")
    else:
        erros.append(f"  ❌ FALTANDO: {node['name']}")

print("\n📦 RESULTADO:\n")
for linha in ok:
    print(linha)

if erros:
    print("\n⚠️  ATENÇÃO — Problemas:\n")
    for e in erros:
        print(e)
    print("\n💡 Rode o script de novo pra baixar o que faltou.")
else:
    print(f"\n{'=' * 60}")
    print("🎉 TUDO CERTO! REINICIANDO COMFYUI...")
    print(f"{'=' * 60}\n")
    os.system("pkill -f 'main.py'")
    time.sleep(3)
    os.system(f"cd {COMFY} && nohup python main.py --listen 0.0.0.0 --port 8188 > /tmp/comfyui.log 2>&1 &")
    time.sleep(5)
    print(f"""
✅ ComfyUI reiniciado com tudo ativo!

🚀 Acesse: http://localhost:8188

🎬 Workflows disponíveis:
   1A  — Divulgação COM vídeo de referência
   1B  — Divulgação SEM vídeo de referência
   2   — Dancinha pra engajamento
   ⭐  tiktok_3_cenas — Gancho + Corpo + CTA
   🆕  wan22_t2v_foto_voz — Foto + Prompt + Voz + LipSync

{'=' * 60}
""")
