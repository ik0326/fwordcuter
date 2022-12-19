import sounddevice as sd
import numpy as np
duration = 3  # 3秒間再生する

# sd.default.device = [0, 0] # Input, Outputデバイス指定
output_device_info = sd.query_devices(device=sd.default.device[1])

f0 = 980
offset = 0
sr_out = int(output_device_info["default_samplerate"])

def callback(outdata, frames, time, status):
    global sr_out, offset, f0
    n_samples, n_channels = outdata.shape
    
    t = np.arange(offset, offset+n_samples) / sr_out
    for k in range(n_channels):
        outdata[:, k] = np.sin(2*np.pi*f0*t) / n_channels

    offset += n_samples
    
with sd.OutputStream(
        channels=2, 
        dtype='float32', 
        callback=callback
    ):
    sd.sleep(int(duration * 1000))