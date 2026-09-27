"""Build a disposable headless GameTest pack for the chest light lifecycle.

Run with an empty output directory, then include it alongside the gameplay pack
in GameTestMain. Require lightcheck:results completed=1 and errors=0 in saved NBT;
the always_pass wrapper alone does not establish success.
"""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
args = parser.parse_args()
root = args.output


def document(name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def function(name, commands):
    path = root / f'data/lightcheck/function/{name}.mcfunction'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(commands) + '\n')


def expect(condition):
    return f'execute unless {condition} run scoreboard players add #errors lightcheck 1'


document('pack.mcmeta', {'pack': {'min_format': [121, 0], 'max_format': [121, 0], 'description': 'Disposable chest light checks'}})
document('data/lightcheck/test_environment/light.json', {'type': 'minecraft:function', 'setup': 'lightcheck:setup'})
document('data/lightcheck/test_instance/light.json', {'type': 'minecraft:function', 'environment': 'lightcheck:light', 'function': 'minecraft:always_pass', 'structure': 'minecraft:empty', 'setup_ticks': 40, 'max_ticks': 1, 'required': True})
for name, minimum, maximum in [('source', 9, 9), ('neighbor', 8, 8), ('removed', 0, 4)]:
    document(f'data/lightcheck/predicate/{name}.json', {'type': 'minecraft:location_check', 'predicate': {'light': {'light': {'min': minimum, 'max': maximum}}}})
function('setup', [
    'data modify storage mysterybox:runtime disabled set value 1b',
    'function mysterybox:load', 'scoreboard objectives add lightcheck dummy',
    'scoreboard players set #errors lightcheck 0', 'time set midnight',
    'forceload add 0 0',
    'execute positioned 8.5 80 8.5 run function lightcheck:install',
    'schedule function lightcheck:observe 5t',
])
function('install', [
    'fill ~-2 ~-1 ~-2 ~2 ~3 ~2 minecraft:air',
    # Keep the section nonempty so vanilla retains cave_air/void_air block states.
    'setblock ~2 ~2 ~2 minecraft:stone',
    'summon marker ~ ~ ~ {Tags:["mysterybox.anchor"]}',
    'function mysterybox:collision/install',
    expect('block ~ ~1 ~ minecraft:light[level=9,waterlogged=false]'),
    'function mysterybox:light/install',
    expect('entity @e[tag=mysterybox.anchor,nbt={data:{light_air:"minecraft:air"}}]'),
])
function('observe', ['execute positioned 8.5 80 8.5 run function lightcheck:assertions'])
checks = [
    'execute positioned ~ ~1 ~ unless predicate lightcheck:source run scoreboard players add #errors lightcheck 1',
    'execute positioned ~1 ~1 ~ unless predicate lightcheck:neighbor run scoreboard players add #errors lightcheck 1',
    'execute positioned ~ ~1 ~ if predicate lightcheck:neighbor run scoreboard players add #errors lightcheck 1',
    'execute positioned ~1 ~1 ~ if predicate lightcheck:source run scoreboard players add #errors lightcheck 1',
    'function mysterybox:load',
    expect('block ~ ~1 ~ minecraft:light[level=9,waterlogged=false]'),
    'function mysterybox:collision/remove', expect('block ~ ~1 ~ minecraft:air'),
]
# All replaced air variants must round-trip; reinstalling must not lose ownership.
for air in ('air', 'cave_air', 'void_air'):
    checks += [f'setblock ~ ~1 ~ minecraft:{air}', 'function mysterybox:light/install',
               'function mysterybox:light/install', 'function mysterybox:light/remove',
               expect(f'block ~ ~1 ~ minecraft:{air}')]
# Do not claim or replace an unrelated solid block or another owner's light.
for block in ('minecraft:stone', 'minecraft:light[level=15]'):
    checks += [f'setblock ~ ~1 ~ {block}', 'function mysterybox:light/install',
               'function mysterybox:light/remove', expect(f'block ~ ~1 ~ {block}')]
# An administrator's replacement survives cleanup of the old ownership record.
checks += ['setblock ~ ~1 ~ minecraft:air', 'function mysterybox:light/install',
           'setblock ~ ~1 ~ minecraft:stone', 'function mysterybox:light/remove',
           expect('block ~ ~1 ~ minecraft:stone'), 'setblock ~ ~1 ~ minecraft:air',
           'function mysterybox:collision/install', 'function mysterybox:light/remove',
           'scoreboard players set #crate mb 1', 'function mysterybox:box/tick',
           expect('block ~ ~1 ~ minecraft:light[level=9]'),
           'scoreboard players set #crate mb 0', 'function mysterybox:collision/remove',
           'schedule function lightcheck:finish 5t']
function('assertions', checks)
function('finish', [
    'execute positioned 8.5 81 8.5 unless predicate lightcheck:removed run scoreboard players add #errors lightcheck 1',
    'execute store result storage lightcheck:results errors int 1 run scoreboard players get #errors lightcheck',
    'data modify storage lightcheck:results completed set value 1',
])
print(root)
