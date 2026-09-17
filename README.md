# 🎬 WAN 2.2 — TikTok Shop Video Workflows

Setup completo pra RunPod Slim + ComfyUI + WAN 2.2.  
Baixa modelos, coloca workflows no lugar certo e verifica tudo automaticamente.

---

## 🚀 Como usar no RunPod

### 1. Sobe o pod com o template **Slim ComfyUI**

### 2. Abre o JupyterLab e cola isso numa célula:

```python
!wget -c "https://raw.githubusercontent.com/RogerSousaServidor/tiktokshop-sofii-hexx/main/setup.py"
exec(open("setup.py").read())
```

### 3. Aguarda o download (~63 GB no total)

### 4. Abre o ComfyUI na porta **8188**

### 5. Vai em **Menu (≡) → Workflows** e escolhe qual usar

---

## 🎬 Workflows incluídos

| # | Arquivo | Quando usar |
|---|---|---|
| 1A | `1A_divulgacao_produto_COM_referencia.json` | Você tem um vídeo de referência de movimento |
| 1B | `1B_divulgacao_produto_SEM_referencia.json` | Não tem vídeo, só prompt |
| 2  | `2_dancinha_engajamento_seguidores.json` | Dancinhas pra viralizar |

---

## 📸 O que colocar em cada workflow

| Workflow | Input 1 | Input 2 |
|---|---|---|
| 1A | Foto da modelo COM produto | Vídeo de movimento suave |
| 1B | Foto da modelo COM produto | Só editar o prompt |
| 2  | Foto da modelo | Vídeo de dança de referência |

---

## 📦 Modelos baixados automaticamente

| Modelo | Tamanho | Usado em |
|---|---|---|
| `umt5_xxl_fp8_e4m3fn_scaled` | 4.6 GB | Todos |
| `wan_2.1_vae` | 0.5 GB | Todos |
| `wan2.2_fun_control_high_noise_14B_fp8_scaled` | 14.3 GB | 1A e 2 |
| `wan2.2_fun_control_low_noise_14B_fp8_scaled` | 14.3 GB | 1A e 2 |
| `wan2.2_i2v_high_noise_14B_fp8_scaled` | 14.3 GB | 1B |
| `wan2.2_i2v_low_noise_14B_fp8_scaled` | 14.3 GB | 1B |
| `clip_vision_h` | 0.6 GB | 1B |

**Total: ~63 GB**

---

## 📁 Estrutura do repositório

```
/
├── setup.py                                      ← Cola no JupyterLab
├── README.md
└── workflows/
    ├── 1A_divulgacao_produto_COM_referencia.json
    ├── 1B_divulgacao_produto_SEM_referencia.json
    └── 2_dancinha_engajamento_seguidores.json
```

---

## 🔍 Verificação automática

O script verifica no final se tudo foi baixado corretamente.  
Se algo falhar, é só rodar de novo — o `wget -c` continua de onde parou.
