import pyaudio
import numpy as np
import time
import openwakeword
from openwakeword.model import Model

# Download all models first
openwakeword.utils.download_models()

def start_wakeword_listener(on_detected):

    # Load without specifying model — uses whatever is available
    oww_model = Model(inference_framework="onnx")

    print("Available models:", list(oww_model.models.keys()))

    CHUNK   = 1280
    FORMAT  = pyaudio.paInt16
    CHANNELS = 1
    RATE    = 16000

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("✅ Wake word active — say 'Hey JARVIS' anytime!\n")

    last_detected = 0
    cooldown = 3

    try:
        while True:
            raw_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(raw_data, dtype=np.int16)
            prediction = oww_model.predict(audio_data)

            for model_name, score in prediction.items():
                if score > 0.5:
                    now = time.time()
                    if now - last_detected > cooldown:
                        print(f"\n🔔 Wake word detected! (score: {score:.2f})")
                        last_detected = now
                        on_detected()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Wake word error: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()