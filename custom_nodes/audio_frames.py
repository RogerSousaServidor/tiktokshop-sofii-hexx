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
    """Mistura efeitos sonoros (arquivos em ComfyUI/input/sfx/ ou input/) na fala, por instante.
    effects: uma linha por efeito -> 'segundos, arquivo, volume'  ex: 15.0, pop.wav, 0.6   ('#' = comentario)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "audio": ("AUDIO",),
            "effects": ("STRING", {"multiline": True, "default": "0.3, whoosh.wav, 0.5\n15.0, pop.wav, 0.6"}),
        }}

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
        out = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                raise ValueError(f"linha invalida (use 'segundos, arquivo, volume'): {raw!r}")
            out.append((float(parts[0]), parts[1], float(parts[2]) if len(parts) > 2 and parts[2] else 0.6))
        return out

    @staticmethod
    def _mix(x, sr, lines, base_dir):
        """x: ndarray float32 [C, T]. Retorna ndarray [C, T] com os efeitos somados."""
        import os
        import subprocess
        import numpy as np
        ff = AudioSpeed._ffmpeg()
        c, total = x.shape
        y = x.copy()
        for t, name, vol in lines:
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

    def run(self, audio, effects):
        import numpy as np
        import torch
        lines = self._parse(effects)
        if not lines:
            return (audio,)
        wav, sr = audio["waveform"], int(audio["sample_rate"])
        base = self._input_dir()
        outs = []
        for i in range(wav.shape[0]):
            x = wav[i].detach().cpu().float().numpy()
            outs.append(torch.from_numpy(self._mix(x, sr, lines, base)))
        return ({"waveform": torch.stack(outs).to(wav.dtype), "sample_rate": sr},)


NODE_CLASS_MAPPINGS = {"AudioToVideoFrames": AudioToVideoFrames, "ResampleFrames": ResampleFrames, "AudioSpeed": AudioSpeed, "AudioSFXMix": AudioSFXMix}
NODE_DISPLAY_NAME_MAPPINGS = {"AudioToVideoFrames": "Audio → Video Frames (4n+1)", "ResampleFrames": "Resample Frames (fps → fps)", "AudioSpeed": "Audio Speed (pitch preservado)", "AudioSFXMix": "Audio SFX Mix (efeitos por instante)"}
