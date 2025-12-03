from faster_whisper import WhisperModel

model = WhisperModel("large-v2", device="cuda", compute_type="float16")
print("✅ Model downloaded & ready")
