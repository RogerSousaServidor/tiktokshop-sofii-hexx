class AudioToVideoFrames:
    """AUDIO -> numero de frames Wan (4n+1) para o video durar o mesmo que o audio."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "audio": ("AUDIO",),
            "fps": ("INT", {"default": 30, "min": 1, "max": 120}),
            "max_frames": ("INT", {"default": 901, "min": 5, "max": 4001}),
        }}

    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("length", "seconds")
    FUNCTION = "run"
    CATEGORY = "audio/utils"

    def run(self, audio, fps, max_frames):
        seconds = audio["waveform"].shape[-1] / float(audio["sample_rate"])
        n = int(seconds * fps)
        n = min(n, max_frames)
        n = max(((n - 1) // 4) * 4 + 1, 5)  # Wan exige 4n+1
        return (n, seconds)


class ResampleFrames:
    """Reamostra frames de src_fps para dst_fps (indice mais proximo), mantendo a duracao real."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "images": ("IMAGE",),
            "src_fps": ("FLOAT", {"default": 32.0, "min": 1.0, "max": 240.0}),
            "dst_fps": ("FLOAT", {"default": 25.0, "min": 1.0, "max": 240.0}),
        }}

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "image/batch"

    def run(self, images, src_fps, dst_fps):
        n = images.shape[0]
        n_out = max(int(n * dst_fps / src_fps), 1)
        idx = [min(int(i * src_fps / dst_fps), n - 1) for i in range(n_out)]
        return (images[idx],)

class AudioSpeed:
    """Acelera/desacelera o AUDIO preservando o tom (ffmpeg atempo). A duracao final = original / speed."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "audio": ("AUDIO",),
            "speed": ("FLOAT", {"default": 1.08, "min": 0.5, "max": 2.0, "step": 0.01}),
        }}

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("AUDIO",)
    FUNCTION = "run"
    CATEGORY = "audio/utils"

    @staticmethod
    def _ffmpeg():
        import shutil
        p = shutil.which("ffmpeg")
        if p:
            return p
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()

    def run(self, audio, speed):
        import subprocess
        import numpy as np
        import torch
        if abs(speed - 1.0) < 1e-3:
            return (audio,)
        wav, sr = audio["waveform"], int(audio["sample_rate"])
        ff = self._ffmpeg()
        outs = []
        for i in range(wav.shape[0]):
            x = wav[i].detach().cpu().float().numpy()          # [C, T]
            c = x.shape[0]
            cmd = [ff, "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", str(c), "-i", "pipe:0",
                   "-filter:a", f"atempo={speed:.4f}", "-f", "f32le", "-ar", str(sr), "-ac", str(c), "pipe:1"]
            r = subprocess.run(cmd, input=np.ascontiguousarray(x.T).tobytes(), capture_output=True, check=True)
            y = np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, c).T.copy()
            outs.append(torch.from_numpy(y))
        t = min(o.shape[-1] for o in outs)
        return ({"waveform": torch.stack([o[..., :t] for o in outs]).to(wav.dtype), "sample_rate": sr},)

class AudioSFXMix:
    """Mistura efeitos sonoros na fala (arquivos em ComfyUI/input/sfx/ ou input/).
    Lista manual 'effects' (uma linha por efeito): 'tempo, arquivo, volume'
      tempo = segundos (ex: 15.0) OU inicio de um bloco de voz: bloco1, bloco2+0.3, bloco3-0.2, fim-1.0
      ('#' = comentario)
    Automatico: corte_sfx toca em todo corte de cena (a cada 'corte_cada' s).
    bloco1..3 (opcionais): audios dos blocos de voz, usados so para saber quando cada bloco comeca
    (as duracoes sao divididas por 'speed', use o mesmo valor do AudioSpeed)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "effects": ("STRING", {"multiline": True, "default": "# tempo (s) ou blocoN, arquivo, volume\n0.3, whoosh.wav, 0.5\nbloco3, pop.wav, 0.6"}),
            },
            "optional": {
                "bloco1": ("AUDIO",),
                "bloco2": ("AUDIO",),
                "bloco3": ("AUDIO",),
                "speed": ("FLOAT", {"default": 1.08, "min": 0.5, "max": 2.0, "step": 0.01}),
                "corte_sfx": ("STRING", {"default": "whoosh.wav"}),
                "corte_cada": ("FLOAT", {"default": 7.5, "min": 0.0, "max": 60.0, "step": 0.1}),
                "corte_vol": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.05}),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("AUDIO",)
    FUNCTION = "run"
    CATEGORY = "audio/utils"

    @staticmethod
    def _input_dir():
        try:
            import folder_paths
            return folder_paths.get_input_directory()
        except Exception:
            return "input"

    @staticmethod
    def _parse(text):
        """Retorna lista de (tempo_str, arquivo, volume). tempo_str e resolvido depois."""
        out = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                raise ValueError(f"linha invalida (use 'tempo, arquivo, volume'): {raw!r}")
            out.append((parts[0], parts[1], float(parts[2]) if len(parts) > 2 and parts[2] else 0.6))
        return out

    @staticmethod
    def _resolve_time(tok, starts, total):
        """tok: '15.0' | 'bloco2' | 'bloco3+0.5' | 'fim-1.0'. starts: {1: seg, 2: seg, ...}. total: duracao (s)."""
        import re
        t = tok.strip().lower()
        m = re.fullmatch(r"(bloco(\d+)|fim)\s*([+-]\s*\d+(?:\.\d+)?)?", t)
        if m:
            off = float(m.group(3).replace(" ", "")) if m.group(3) else 0.0
            if m.group(1) == "fim":
                return total + off
            k = int(m.group(2))
            if k not in starts:
                raise ValueError(f"'{tok}': ligue o audio do bloco{k} no node (entrada bloco{k})")
            return starts[k] + off
        return float(t)

    @classmethod
    def _plan(cls, lines, starts, total, corte_sfx, corte_cada, corte_vol):
        """Junta efeitos manuais e de corte de cena -> lista (segundos, arquivo, volume)."""
        plan = [(cls._resolve_time(t, starts, total), f, v) for t, f, v in lines]
        if corte_sfx and corte_cada > 0:
            k = 1
            while k * corte_cada < total - 0.5:
                plan.append((k * corte_cada, corte_sfx, corte_vol))
                k += 1
        return sorted(plan)

    @staticmethod
    def _mix(x, sr, plan, base_dir):
        """x: ndarray float32 [C, T]. plan: [(segundos, arquivo, volume)]. Retorna [C, T] com os efeitos somados."""
        import os
        import subprocess
        import numpy as np
        ff = AudioSpeed._ffmpeg()
        c, total = x.shape
        y = x.copy()
        for t, name, vol in plan:
            f = None
            for d in (os.path.join(base_dir, "sfx"), base_dir):
                cand = name if os.path.isabs(name) else os.path.join(d, name)
                if os.path.exists(cand):
                    f = cand
                    break
            if f is None:
                raise FileNotFoundError(f"efeito nao encontrado: {name} (procurado em {base_dir}/sfx e {base_dir})")
            cmd = [ff, "-v", "error", "-i", f, "-f", "f32le", "-ar", str(sr), "-ac", str(c), "pipe:1"]
            r = subprocess.run(cmd, capture_output=True, check=True)
            e = np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, c).T * vol
            start = max(int(round(t * sr)), 0)
            if start >= total:
                continue
            n = min(e.shape[1], total - start)
            y[:, start:start + n] += e[:, :n]
        peak = float(np.abs(y).max()) if y.size else 0.0
        if peak > 0.98:
            y = y * (0.98 / peak)
        return y

    def run(self, audio, effects, bloco1=None, bloco2=None, bloco3=None, speed=1.08,
            corte_sfx="whoosh.wav", corte_cada=7.5, corte_vol=0.5):
        import torch
        lines = self._parse(effects)
        wav, sr = audio["waveform"], int(audio["sample_rate"])
        total = wav.shape[-1] / float(sr)
        starts, acc = {}, 0.0
        for k, b in enumerate((bloco1, bloco2, bloco3), 1):
            if b is None:
                break
            starts[k] = acc / speed
            acc += b["waveform"].shape[-1] / float(b["sample_rate"])
        plan = self._plan(lines, starts, total, (corte_sfx or "").strip(), corte_cada, corte_vol)
        if not plan:
            return (audio,)
        base = self._input_dir()
        outs = []
        for i in range(wav.shape[0]):
            x = wav[i].detach().cpu().float().numpy()
            outs.append(torch.from_numpy(self._mix(x, sr, plan, base)))
        return ({"waveform": torch.stack(outs).to(wav.dtype), "sample_rate": sr},)


class ZoomPunch:
    """Zoom 'punch-in' por frame, com tempo exato (sincroniza com os SFX).
    Cada tempo em 'inicios' (segundos, separados por virgula) dispara um zoom 1.0 -> 'zoom' em 'duracao' s
    (ease-out: comeca rapido e assenta). 'volta' > 0: depois relaxa de volta a 1.0 em 'volta' s; 0 = mantem ate o proximo disparo.
    Recorta o centro e reamostra (bicubico) direto para out_w x out_h: substitui o node de upscale (uma unica reamostragem)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "images": ("IMAGE",),
            "inicios": ("STRING", {"default": "0, 7.5625, 15.0625, 22.5625"}),
            "zoom": ("FLOAT", {"default": 1.25, "min": 1.0, "max": 3.0, "step": 0.01}),
            "duracao": ("FLOAT", {"default": 0.25, "min": 0.03, "max": 3.0, "step": 0.01}),
            "volta": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 5.0, "step": 0.05}),
            "fps": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 120.0}),
            "out_w": ("INT", {"default": 720, "min": 16, "max": 4096}),
            "out_h": ("INT", {"default": 1280, "min": 16, "max": 4096}),
        }}

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "image/batch"

    @staticmethod
    def zoom_at(t, starts, zoom, dur, volta):
        """Fator de zoom no instante t (s). starts: lista ordenada de disparos."""
        prev = [s for s in starts if s <= t + 1e-9]
        if not prev:
            return 1.0
        e = t - prev[-1]
        u = min(max(e / dur, 0.0), 1.0)
        k = 1.0 - (1.0 - u) ** 3                       # ease-out cubico
        if volta > 0 and e > dur:
            v = min((e - dur) / volta, 1.0)
            k *= 1.0 - (v * v * (3 - 2 * v))           # smoothstep de volta
        return 1.0 + (zoom - 1.0) * k

    def run(self, images, inicios, zoom, duracao, volta, fps, out_w, out_h):
        import torch
        import torch.nn.functional as F
        starts = sorted(float(x) for x in inicios.replace(";", ",").split(",") if x.strip())
        n, h, w, c = images.shape
        out = torch.empty((n, out_h, out_w, c), dtype=images.dtype)
        zs = [self.zoom_at(i / fps, starts, zoom, duracao, volta) for i in range(n)]
        dev = images.device
        # grade de saida normalizada [-1,1]; escala = 1/zoom recorta o centro (aspecto da saida = aspecto da entrada)
        ys = torch.linspace(-1 + 1.0 / out_h, 1 - 1.0 / out_h, out_h, device=dev)
        xs = torch.linspace(-1 + 1.0 / out_w, 1 - 1.0 / out_w, out_w, device=dev)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        for a in range(0, n, 16):
            b = min(a + 16, n)
            x = images[a:b].permute(0, 3, 1, 2).float()
            z = torch.tensor(zs[a:b], device=dev, dtype=torch.float32).view(-1, 1, 1)
            grid = torch.stack([gx[None] / z, gy[None] / z], dim=-1)
            y = F.grid_sample(x, grid, mode="bicubic", padding_mode="border", align_corners=False)
            out[a:b] = y.clamp(0, 1).permute(0, 2, 3, 1).to(images.dtype).cpu()
        return (out,)


NODE_CLASS_MAPPINGS = {"AudioToVideoFrames": AudioToVideoFrames, "ResampleFrames": ResampleFrames, "AudioSpeed": AudioSpeed, "AudioSFXMix": AudioSFXMix, "ZoomPunch": ZoomPunch}
NODE_DISPLAY_NAME_MAPPINGS = {"AudioToVideoFrames": "Audio → Video Frames (4n+1)", "ResampleFrames": "Resample Frames (fps → fps)", "AudioSpeed": "Audio Speed (pitch preservado)", "AudioSFXMix": "Audio SFX Mix (efeitos por instante)", "ZoomPunch": "Zoom Punch (por tempo, com upscale)"}
