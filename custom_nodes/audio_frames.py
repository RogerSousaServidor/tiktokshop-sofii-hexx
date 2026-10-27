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


NODE_CLASS_MAPPINGS = {"AudioToVideoFrames": AudioToVideoFrames, "ResampleFrames": ResampleFrames, "AudioSpeed": AudioSpeed}
NODE_DISPLAY_NAME_MAPPINGS = {"AudioToVideoFrames": "Audio → Video Frames (4n+1)", "ResampleFrames": "Resample Frames (fps → fps)", "AudioSpeed": "Audio Speed (pitch preservado)"}
