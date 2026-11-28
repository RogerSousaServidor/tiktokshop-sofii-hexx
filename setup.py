import os
import time

# ============================================================
#  SETUP COMPLETO — RunPod Slim + ComfyUI + WAN 2.2
#  Workflows: 1A | 1B | 2 | 3 cenas | T2V+voz
#  Autor: Roger
# ============================================================

COMFY  = os.environ.get("COMFY", "/workspace/runpod-slim/ComfyUI")   # COMFY=/caminho/ComfyUI python3 setup.py  (outro template)
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
    f"{BASE}/loras",
    f"{BASE}/frame_interpolation",
    WF_DIR,
]:
    os.makedirs(pasta, exist_ok=True)

print("📁 Pastas criadas!\n")

# ── CUSTOM NODES ─────────────────────────────────────────────
print("=" * 60)
print("📦 INSTALANDO CUSTOM NODES")
print("=" * 60)

CUSTOM_NODES = [
    ("ComfyUI-WanVideoWrapper", "https://github.com/kijai/ComfyUI-WanVideoWrapper.git", True),
    ("ComfyUI-FishAudioS2", "https://github.com/imshivamohan/comfyui-fishaudios2.git", False),  # repo original (Saganaki22) saiu do ar (404) em 2026-10-14; fork identico, mesmas classes de no (FishS2VoiceCloneTTS etc) — deps auto-instalam no startup
    ("ComfyUI-QwenTTS", "https://github.com/1038lab/ComfyUI-QwenTTS.git", False),  # TTS pt-BR (Qwen3-TTS); modelos baixam no 1o uso; deps: pip install -r requirements.txt no venv
    ("ComfyUI-GGUF", "https://github.com/city96/ComfyUI-GGUF.git", True),  # UnetLoaderGGUF: carregador Wan 2.2 GGUF (workflow_60s_4blocos_gguf)
    ("ComfyUI-LatentSync-Node", "https://github.com/iVideoGameBoss/ComfyUI-LatentSync-Node.git", True),
]
for nome, url, pip_req in CUSTOM_NODES:
    p = f"{NODES}/{nome}"
    if os.path.exists(p):
        print(f"\n⏭️  {nome} já instalado — atualizando...")
        os.system(f"cd {p} && git pull")
    else:
        print(f"\n⬇️  Instalando {nome}...")
        os.system(f'cd {NODES} && git clone {url} "{nome}"')
    if pip_req and os.path.exists(f"{p}/requirements.txt"):
        os.system(f"pip install -r {p}/requirements.txt --break-system-packages -q")
# custom node local do repo: duracao do audio -> frames do video
os.makedirs(f"{NODES}/audio_frames", exist_ok=True)
os.system(f'wget -q -O "{NODES}/audio_frames/__init__.py" "https://raw.githubusercontent.com/RogerSousaServidor/tiktokshop-sofii-hexx/main/custom_nodes/audio_frames.py"')
wan_wrapper = f"{NODES}/ComfyUI-WanVideoWrapper"
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
    {
        "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
        "dest": f"{BASE}/loras",
        "size": "1.2 GB",
        "used": "T2V+voz (4 passos)"
    },
    {
        "name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
        "dest": f"{BASE}/loras",
        "size": "1.2 GB",
        "used": "T2V+voz (4 passos)"
    },
    {
        "name": "film_net_fp16.safetensors",
        "url":  "https://huggingface.co/Comfy-Org/frame_interpolation/resolve/main/frame_interpolation/film_net_fp16.safetensors",
        "dest": f"{BASE}/frame_interpolation",
        "size": "0.1 GB",
        "used": "T2V+voz (interpolacao 16->32fps)"
    },
]

# ── LISTA DE WORKFLOWS ────────────────────────────────────────
WORKFLOWS = [
    {"name": "1B_divulgacao_produto_SEM_referencia.json", "url": f"{RAW}/1B_divulgacao_produto_SEM_referencia.json", "desc": "Divulgação SEM referência"},
    {"name": "30s_foto_por_cena.json", "url": f"{RAW}/30s_foto_por_cena.json", "desc": "30 s: voz Qwen + efeitos + 1 foto e 1 prompt por cena (720x1280, 30 fps)"},
    {"name": "wan22_t2v_foto_voz.json", "url": f"{RAW}/wan22_t2v_foto_voz.json", "desc": "T2V + foto + voz Qwen3 TTS + LipSync (30 s)"},
    {"name": "wan22_t2v_foto_voz_22s.json", "url": f"{RAW}/wan22_t2v_foto_voz_22s.json", "desc": "T2V + voz + LipSync (ate 22 s, 3 segmentos)"},
    {"name": "wan22_t2v_foto_voz_15s.json", "url": f"{RAW}/wan22_t2v_foto_voz_15s.json", "desc": "T2V + voz + LipSync (ate 15 s, 2 segmentos)"},
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
    os.system(f'wget -q -O "{WF_DIR}/{wf["name"]}" "{wf["url"]}"')

# ── EFEITOS SONOROS PADRAO (gerados com ffmpeg, sem direitos autorais) ─────────
# Usados pelo node AudioSFXMix. Nao sobrescreve arquivos que ja existem em input/sfx/ (troque pelos seus quando quiser).
print("\n" + "=" * 60)
print("🔊 EFEITOS SONOROS PADRAO (input/sfx)")
print("=" * 60)
import shutil, subprocess
SFX_DIR = f"{COMFY}/input/sfx"
os.makedirs(SFX_DIR, exist_ok=True)
_ff = shutil.which("ffmpeg")
if not _ff:
    try:
        import imageio_ffmpeg
        _ff = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        _ff = None
SFX = {
    # swoosh: ruido rosa filtrado com subida e descida suaves (0,7 s)
    "whoosh.wav": ["-f", "lavfi", "-i", "anoisesrc=color=pink:duration=0.7:amplitude=0.9:sample_rate=44100",
                   "-af", "highpass=f=250,lowpass=f=5000,afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.4,volume=3.5,alimiter=limit=0.9"],
    # pop: seno curto com queda rapida de frequencia e volume (0,2 s)
    "pop.wav": ["-f", "lavfi", "-i", "aevalsrc=sin(2*PI*(600+1800*exp(-t*45))*t)*exp(-t*22):d=0.2:s=44100",
                "-af", "volume=0.9"],
    # notificacao: dois tons (880 Hz e 1320 Hz), 0,5 s no total
    "notificacao.wav": ["-f", "lavfi", "-i", "aevalsrc=if(lt(t\\,0.18)\\,sin(2*PI*880*t)\\,sin(2*PI*1320*t))*exp(-3*mod(t\\,0.18)/0.18)*0.6:d=0.5:s=44100"],
}
if _ff is None:
    print("  ⚠️  ffmpeg nao encontrado — coloque seus efeitos manualmente em", SFX_DIR)
else:
    for nome, args in SFX.items():
        destino = os.path.join(SFX_DIR, nome)
        if os.path.exists(destino) and os.path.getsize(destino) > 1000:
            print(f"  ⏭️  Já existe: {nome} — mantendo")
            continue
        r = subprocess.run([_ff, "-y", "-v", "error", *args, "-ac", "2", "-ar", "44100", destino], capture_output=True, text=True)
        print(f"  ✅ Gerado: {nome}" if r.returncode == 0 else f"  ❌ ERRO ao gerar {nome}: {r.stderr.strip()[:200]}")

# ── VOZ DE REFERENCIA DA SOFII (usada pelo LoadAudio dos workflows Qwen3 TTS) ─────────
# Baixa para input/ so se ainda nao existir (para trocar a voz, substitua o arquivo em input/ ou em assets/ no GitHub).
print("\n" + "=" * 60)
print("🎤 VOZ DE REFERENCIA (input/Sofii_audio_novo.m4a)")
print("=" * 60)
VOZ = f"{COMFY}/input/Sofii_audio_novo.m4a"
os.makedirs(f"{COMFY}/input", exist_ok=True)
if os.path.exists(VOZ) and os.path.getsize(VOZ) > 1000:
    print("  ⏭️  Já existe: Sofii_audio_novo.m4a — mantendo")
else:
    os.system(f'wget -q -O "{VOZ}" "{RAW.rsplit("/workflows", 1)[0]}/assets/Sofii_audio_novo.m4a"')
    print("  ✅ Baixado: Sofii_audio_novo.m4a" if os.path.exists(VOZ) and os.path.getsize(VOZ) > 1000 else "  ❌ ERRO ao baixar Sofii_audio_novo.m4a")

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

for nome, _, _ in CUSTOM_NODES:
    if os.path.exists(f"{NODES}/{nome}"):
        ok.append(f"  ✅ {nome} (custom node)")
    else:
        erros.append(f"  ❌ FALTANDO: {nome}")

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
   3 cenas / T2V + voz Fish Audio + LipSync

📸 Inputs:
   1A e 2 → Foto da modelo + Vídeo de referência
   1B     → Foto da modelo + Prompt descritivo

{'=' * 60}
""")
