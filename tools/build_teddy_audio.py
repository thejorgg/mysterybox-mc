"""Build the sample-timed witch echo from an installed vanilla asset cache.

python tools/build_teddy_audio.py --assets /path/to/meta/assets --index 34
Requires ffmpeg. No download, credentials, GUI, or source recording required.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--assets', type=Path, required=True)
parser.add_argument('--index', default='34')
args = parser.parse_args()
settings = json.loads((ROOT / 'source/teddy_audio.json').read_text())
assets = args.assets.expanduser()
index = json.loads((assets / 'indexes' / f'{args.index}.json').read_text())
digest = index['objects'][settings['source_asset']]['hash']
original = assets / 'objects' / digest[:2] / digest
if hashlib.sha1(original.read_bytes()).hexdigest() != digest:
    raise ValueError('Vanilla laugh asset does not match its asset-index digest')
rate = settings['sample_rate']
pitch = settings['pitch_multiplier']
delay = settings['echo_delay_ms']
gains = settings['echo_gains']
output_gain = settings['output_gain']
if type(rate) is not int or rate != 48000:
    raise ValueError('sample_rate must be 48000')
if not isinstance(pitch, (int, float)) or not 1 < pitch <= 2:
    raise ValueError('pitch_multiplier must be greater than 1 and at most 2')
if type(delay) is not int or not 0 <= delay <= 1000:
    raise ValueError('echo_delay_ms must be an integer from 0 to 1000')
if len(gains) != 3 or any(not isinstance(g, (int, float)) or not 0 <= g <= 1 for g in gains) or not 0 < sum(gains) <= 1:
    raise ValueError('echo_gains must contain three nonnegative gains summing to at most 1')
if not isinstance(output_gain, (int, float)) or not 0 < output_gain <= 3:
    raise ValueError('output_gain must be greater than 0 and at most 3')
filters = [f'aresample={rate},asetrate={round(rate * pitch)},aresample={rate},asplit=3[a][b][c]']
for i, label in enumerate('abc'):
    samples = round(rate * delay * i / 1000)
    filters.append(f'[{label}]adelay={samples}S:all=1,volume={gains[i]}[{label}out]')
filters.append(f'[aout][bout][cout]amix=inputs=3:normalize=0,volume={output_gain}')
output = ROOT / 'resourcepack/assets/mysterybox/sounds/teddy_laugh.ogg'
output.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(original), '-filter_complex', ';'.join(filters), '-ac', '1', '-ar', str(rate), '-c:a', 'libvorbis', '-q:a', '6', str(output)], check=True)
print(json.dumps({'output': str(output.relative_to(ROOT)), 'source_sha1': digest, 'pitch_multiplier': pitch, 'voice_offsets_samples': [round(rate * delay * i / 1000) for i in range(3)], 'voice_offsets_ms': [delay * i for i in range(3)]}))
