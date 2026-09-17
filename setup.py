import os

# ============================================================
#  SETUP COMPLETO — RunPod Slim + ComfyUI + WAN 2.2
#  Workflows: 1A | 1B | 2
#  Autor: Roger
# ============================================================

BASE   = "/workspace/runpod-slim/ComfyUI/models"
WF_DIR = "/workspace/runpod-slim/ComfyUI/user/default/workflows"
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
    if os.path.exists(path):
        atual = os.path.getsize(path)
        if atual > 1_000_000:  # maior que 1MB = válido
            print(f"  ⏭️  Já existe: {nome} — pulando")
            return
    print(f"  ⬇️  {nome} {f'({size})' if size else ''}")
    ret = os.system(f'wget -c --show-progress "{url}" -P "{dest}"')
    if ret == 0:
        print(f"  ✅ Salvo!")
    else:
        print(f"  ❌ ERRO ao baixar {nome} — tente novamente")

# ── DOWNLOAD MODELOS ──────────────────────────────────────────
print("=" * 60)
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

erros   = []
ok      = []

for m in MODELS:
    path = os.path.join(m["dest"], m["name"])
    if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
        size_gb = os.path.getsize(path) / (1024**3)
        ok.append(f"  ✅ {m['name']} ({size_gb:.1f} GB)")
    else:
        erros.append(f"  ❌ FALTANDO: {m['name']} → {m['dest']}")

for wf in WORKFLOWS:
    path = os.path.join(WF_DIR, wf["name"])
    if os.path.exists(path):
        ok.append(f"  ✅ {wf['name']}")
    else:
        erros.append(f"  ❌ FALTANDO: {wf['name']} → {WF_DIR}")

print("\n📦 MODELOS E WORKFLOWS:\n")
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
🎉 TUDO CERTO! PRONTO PRA USAR!
{'=' * 60}

🚀 Acesse o ComfyUI:
   http://localhost:8188

🎬 Seus workflows estão em:
   Menu (≡) → Workflows → escolha o que quer usar

📋 Workflows disponíveis:
   1A — Divulgação COM vídeo de referência (Fun Control)
   1B — Divulgação SEM vídeo de referência (I2V puro)
   2  — Dancinha pra engajamento e seguidores

📸 Inputs necessários:
   1A e 2 → Foto da modelo + Vídeo de referência
   1B     → Foto da modelo + Prompt descritivo

{'=' * 60}
""")
