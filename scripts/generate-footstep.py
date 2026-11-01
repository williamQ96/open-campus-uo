# SPDX-License-Identifier: Apache-2.0
"""Original deterministic soft-shoe sample. Generated WAV dedicated to CC0."""
from pathlib import Path
import math
import random
import struct
import wave

root = Path(__file__).resolve().parents[1]
target = root / 'apps/web-preview/public/audio/footstep.wav'
target.parent.mkdir(parents=True, exist_ok=True)
rng = random.Random(31)
rate = 22050
samples = []
low = 0.0
for i in range(int(rate * 0.14)):
    t = i / rate
    low = low * 0.72 + rng.uniform(-1, 1) * 0.28
    attack = min(1, t / 0.004)
    envelope = attack * math.exp(-t * 36)
    value = (low * 0.65 + math.sin(2 * math.pi * 105 * t) * 0.18) * envelope
    samples.append(struct.pack('<h', int(max(-1, min(1, value)) * 30000)))
with wave.open(str(target), 'wb') as out:
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(rate)
    out.writeframes(b''.join(samples))
print(target)
