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


NODE_CLASS_MAPPINGS = {"AudioToVideoFrames": AudioToVideoFrames, "ResampleFrames": ResampleFrames}
NODE_DISPLAY_NAME_MAPPINGS = {"AudioToVideoFrames": "Audio → Video Frames (4n+1)", "ResampleFrames": "Resample Frames (fps → fps)"}
