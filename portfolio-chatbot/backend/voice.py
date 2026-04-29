import io
import wave

import numpy as np

_tts    = None
_sr     = 24000   # XTTS-v2 native sample rate


def load_tts():
    global _tts, _sr
    if _tts is not None:
        return _tts

    try:
        from TTS.api import TTS
        print("Loading XTTS-v2 (first run downloads ~2 GB — subsequent starts are instant)…")
        model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        try:
            _sr = model.synthesizer.output_sample_rate
        except Exception:
            _sr = 24000
        _tts = model
        print(f"XTTS-v2 ready  (sample rate = {_sr} Hz)")
    except (ImportError, Exception) as e:
        err = str(e)
        if "No module" in err or isinstance(e, ImportError):
            print("WARNING: TTS package not found — /speak will be unavailable.")
        else:
            print(f"WARNING: TTS failed to load ({err}) — /speak will be unavailable.")
            print("         To fix: pip install 'transformers==4.36.2' 'huggingface_hub==0.20.3' 'tokenizers==0.15.2'")
        _tts = "unavailable"

    return _tts


def synthesize(text: str, voice_ref: str) -> bytes:
    tts = load_tts()
    if tts == "unavailable":
        raise RuntimeError("TTS not available — install Coqui TTS and retry.")

    wav_list = tts.tts(text=text, speaker_wav=voice_ref, language="en")

    # Convert float list → 16-bit PCM WAV bytes in memory
    audio = np.array(wav_list, dtype=np.float32)
    pcm   = (audio * 32767).clip(-32768, 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_sr)
        wf.writeframes(pcm.tobytes())
    buf.seek(0)
    return buf.read()
