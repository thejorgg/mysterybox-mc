"""Read the musician-facing CSV; harp pitch 1 is F-sharp 4."""
import csv
import math
import re


def read_notes(path):
    notes = []
    with path.open(newline='') as source:
        for line, row in enumerate(csv.DictReader(source), 2):
            try:
                tick = int(row['tick'])
                volume = int(row['volume_percent'])
                cents = float(row['cents'] or 0)
                match = re.fullmatch(r'([A-Ga-g])([#b]?)(-?\d+)', row['note'].strip())
                if not match:
                    raise ValueError('note must be a name such as C4, F#4, or Bb3')
                letter, accidental, octave = match.groups()
                midi = (int(octave) + 1) * 12 + {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}[letter.upper()]
                midi += {'':0,'#':1,'b':-1}[accidental]
                pitch = 2 ** ((midi - 66 + cents / 100) / 12)
                if tick < 1 or not 0 <= volume <= 100:
                    raise ValueError('tick must be at least 1; volume_percent must be 0–100')
                if not math.isfinite(pitch) or not .5 <= pitch <= 2:
                    raise ValueError('note plus cents must be within F#3–F#5 for vanilla harp playback')
                instrument = row['instrument'].strip()
                if not re.fullmatch('[a-z_]+', instrument):
                    raise ValueError('instrument must be a note-block sound name, such as harp')
                notes.append({'tick': tick, 'sound': 'minecraft:block.note_block.' + instrument,
                              'pitch': round(pitch, 8), 'volume': volume})
            except (KeyError, ValueError, OverflowError) as error:
                raise ValueError(f'{path}:{line}: {error}') from error
    if not notes:
        raise ValueError(f'{path}: melody must contain at least one note')
    return notes
