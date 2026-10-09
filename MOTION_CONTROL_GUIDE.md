# 🎬 Motion Control Workflow - Guia Simplificado

## O que faz esse workflow?

Pega um **vídeo de referência** (com movimentos), pega uma **sua imagem/foto**, e gera um vídeo novo replicando **exatamente os mesmos movimentos** do vídeo original mas com a sua imagem.

---

## 📋 Estrutura do Workflow (11 Nodes)

```
┌─────────────────────────────────────────────────────────────┐
│                    MOTION CONTROL PIPELINE                   │
└─────────────────────────────────────────────────────────────┘

[INPUTS]
├─ LoadImage (Node 7)      → Sua foto/imagem
├─ LoadVideo (Node 9)      → Vídeo de referência (movimentos)
└─ LoadVideo (Node 10)     → Outro vídeo de referência

[MODELS & CONFIG]
├─ UNETLoader (Node 0)     → Modelo de geração
├─ CLIPLoader (Node 1)     → CLIP para entender prompts
├─ VAELoader (Node 2)      → VAE para decodificar
└─ ModelSamplingSD3 (Node 6) → Configuração do sampling

[PROCESSING - MAIN]
├─ Wan22FunControlToVideo (Node 3) → ⭐ CORAÇÃO DO WORKFLOW
│  └─ Pega: Imagem + Vídeo (movimento) + Modelo
│  └─ Faz: "Aplica os movimentos do vídeo na sua imagem"
└─ KSamplerAdvanced (Nodes 4, 5)   → Refinamento

[OUTPUT]
└─ SaveVideo (Node 8)              → Salva o resultado
```

---

## ⚙️ Como Usar

### 1️⃣ **Preparar suas entradas**

```
Input Video (Motion Reference):
├─ Node 9 ou Node 10: "seu_video_movimento.mp4"
│  └─ Esse vídeo define os MOVIMENTOS
│  └─ Pode ser qualquer vídeo com pessoa dançando, caminhando, etc

Sua Imagem (Reference):
└─ Node 7: "sua_foto.jpg"
   └─ Essa é YOU
   └─ Será aplicado o movimento do vídeo nessa imagem
```

### 2️⃣ **Parametrizar o Motion Control**

No **Node 3** (Wan22FunControlToVideo), você tem:

- **fps**: 30 (ou quanto quiser)
- **width/height**: 832x480 recomendado
- **length**: **77 frames padrão** → aumente isso pra mais segundos!
  - 77 frames = 2.5 seg
  - 300 frames = 10 seg
  - 600 frames = 20 seg (com 48GB VRAM)

### 3️⃣ **Rodar no RunPod**

```bash
# No seu servidor ComfyUI
1. Importar: motion_control_simplified.json
2. Configurar inputs (vídeo + imagem)
3. Aumentar "length" conforme VRAM disponível
4. Clicar "Queue"
5. Aguardar processamento
```

---

## 🎯 O que Muda Conforme a VRAM

| VRAM | Frames Max | Duração | Resolução |
|------|-----------|---------|-----------|
| 24GB | 150 | 5 seg | 832x480 |
| 48GB | 300-400 | 10-13 seg | 832x480 |
| 96GB | 600+ | 20 seg | 832x480 |
| 190GB | 900-1000 | 30+ seg | 832x480 |

**Qualidade: MANTIDA em toda a faixa** ✨

---

## 📝 Dicas Pro

✅ **Vídeo de referência limpo** = melhor resultado
✅ **Imagem com rosto claro** = mais estável
✅ **Comece com 150 frames** e vá aumentando
✅ **Mesma resolução** em tudo = menos bugs

⚠️ **Aumentar resolução** gasta MUITO mais VRAM
⚠️ **Frame_load_cap=0** = carrega TÁ DOS os frames (máximo)

---

## 🔧 Nodes Explicados

| Node | Função | Ajustar? |
|------|--------|----------|
| LoadImage | Sua imagem | Mudar arquivo |
| LoadVideo (2x) | Vídeos de movimento | Mudar arquivo |
| Wan22FunControl | **APLICA movimento** | Mudar prompt/length |
| KSampler | Refina detalhe | Mudar steps/seed |
| SaveVideo | Salva resultado | Mudar formato |

---

## 🚀 Exemplo Prático

### Cenário: Gerar video de você dançando igual Grudado no TikTok

1. **Input Video**: `grudado_dancing.mp4` (qualquer vídeo com dança)
2. **Sua Imagem**: `você.jpg` 
3. **Node 3 - Settings**:
   - fps: 30
   - width: 832
   - height: 480
   - **length: 600** (20 segundos)
   - prompt: "a person is dancing energetically"

4. **Rodar** → Resultado: VOCÊ dançando assim! 🎉

---

## 💾 Arquivo Incluído

- `motion_control_simplified.json` - Workflow pronto pra rodar

Basta importar no seu ComfyUI e configurar as entradas!

