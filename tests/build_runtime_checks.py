"""Generate opt-in, real-Minecraft regression checks for a disposable 26.3 world.

Usage: python tests/build_runtime_checks.py --minecraft-jar /path/to/26.3.jar
Install the resulting checks ZIP alongside the gameplay datapack.
/function mbcheck:rewards (player or server console; idle box and clear drops required)
Run these as a player:
/function mbcheck:enchantments
/function mbcheck:economy
/function mbcheck:placement (stand in an empty 5x4x3 space in Creative)
Economy checks replace held items and XP; NEVER run in a valued world.
"""
import argparse
import itertools
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--minecraft-jar', type=Path, required=True)
args = parser.parse_args()
catalog = json.loads((ROOT/'source/catalog-26.3.json').read_text())
gear = list(dict.fromkeys(catalog['weapons'] + catalog['armor'] + catalog['tools']))
files = {}


def function(name, commands):
    files[f'data/mbcheck/function/{name}.mcfunction'] = '\n'.join(commands) + '\n'


with zipfile.ZipFile(args.minecraft_jar) as jar:
    def tag_values(kind, tag):
        result = set()
        for value in json.loads(jar.read(f'data/minecraft/tags/{kind}/{tag}.json'))['values']:
            value = value['id'] if isinstance(value, dict) else value
            result.update(tag_values(kind, value[11:]) if value.startswith('#minecraft:') else [value])
        return result

    def resolve(kind, values):
        if isinstance(values, str):
            return tag_values(kind, values[11:]) if values.startswith('#minecraft:') else {values}
        return set().union(*(resolve(kind, value) for value in values)) if values else set()

    expected_armor = tag_values('item', 'enchantable/armor') | {'minecraft:elytra'}
    if set(catalog['armor']) != expected_armor or len(catalog['weapons'] + catalog['armor']) != len(set(catalog['weapons'] + catalog['armor'])):
        raise ValueError('Reward catalog must include each player armor item and elytra exactly once')

    definitions = {entry['id']: json.loads(jar.read(f'data/minecraft/enchantment/{entry["id"].split(":")[1]}.json')) for entry in catalog['enchantments']}
    exclusive = set()
    for name, definition in definitions.items():
        for other in resolve('enchantment', definition.get('exclusive_set', [])):
            if name != other:
                exclusive.add(tuple(sorted((name, other))))
    supported = {name: resolve('item', definition['supported_items']) for name, definition in definitions.items()}
    for item in gear:
        for mode in ('normal', 'godmode'):
            if mode == 'godmode' and item not in {
                'minecraft:netherite_sword', 'minecraft:netherite_chestplate',
                'minecraft:netherite_pickaxe', 'minecraft:netherite_axe',
                'minecraft:crossbow', 'minecraft:trident', 'minecraft:brush',
            }:
                continue
            checks = ['scoreboard players add #samples mbcheck 1',
                      f'execute unless data storage mysterybox:runtime reward{{id:"{item}",count:1}} run scoreboard players add #errors mbcheck 1',
                      'execute store result score #count mbcheck run data get storage mysterybox:runtime reward.components."minecraft:enchantments"',
                      'execute unless score #count mbcheck matches 1.. run scoreboard players add #errors mbcheck 1']
            for name, definition in definitions.items():
                path = f'reward.components."minecraft:enchantments"."{name}"'
                if item not in supported[name]:
                    checks.append(f'execute if data storage mysterybox:runtime {path} run scoreboard players add #errors mbcheck 1')
                level = definition['max_level']
                expected_level = str(level) if mode == 'godmode' else f'1..{level}'
                checks += [f'execute store result score #level mbcheck run data get storage mysterybox:runtime {path}',
                           f'execute if data storage mysterybox:runtime {path} unless score #level mbcheck matches {expected_level} run scoreboard players add #errors mbcheck 1']
            for left, right in sorted(exclusive):
                checks.append(f'execute if data storage mysterybox:runtime reward.components."minecraft:enchantments"."{left}" if data storage mysterybox:runtime reward.components."minecraft:enchantments"."{right}" run scoreboard players add #errors mbcheck 1')
            function(f'check/{mode}/{item.split(":")[1]}', checks)

setup = ['execute unless score #state mb matches 0 run return run tellraw @s {"text":"Wait for an idle mystery box before testing.","color":"red"}',
         'execute unless entity @e[tag=mysterybox.anchor,limit=1] run return run tellraw @s {"text":"Place a mystery box before testing.","color":"red"}',
         'execute if entity @e[tag=mysterybox.reward] run return run tellraw @s {"text":"Wait until the reward display clears before testing.","color":"red"}',
         'scoreboard objectives add mbcheck dummy',
         'scoreboard players set #errors mbcheck 0',
         'data modify storage mbcheck:state saved_config set from storage mysterybox:config']
restore = [f'data modify storage mysterybox:config {key} set from storage mbcheck:state saved_config.{key}' for key in json.loads((ROOT/'source/defaults.json').read_text())]
restore_runtime = [
    command
    for key in ('loot_mode', 'reward', 'loot_table', 'loot_sets_v1',
                'binding_curse', 'vanishing_curse', 'mending_basis_points')
    for command in (
        f'execute if data storage mbcheck:state saved_runtime.{key} run data modify storage mysterybox:runtime {key} set from storage mbcheck:state saved_runtime.{key}',
        f'execute unless data storage mbcheck:state saved_runtime.{key} run data remove storage mysterybox:runtime {key}',
    )
]
commands = setup + ['scoreboard players set #samples mbcheck 0',
                    'data modify storage mbcheck:state saved_runtime set from storage mysterybox:runtime',
                    'data modify storage mysterybox:runtime loot_mode set value "combat"',
                    'data modify storage mysterybox:runtime binding_curse set value 0',
                    'data modify storage mysterybox:runtime vanishing_curse set value 0',
                    'data modify storage mysterybox:runtime mending_basis_points set value 0',
                    'summon item_display ~ ~ ~ {Tags:["mysterybox.reward","mbcheck.probe"],item:{id:"minecraft:paper",count:1}}']
# Keep the expanded compatibility checks within vanilla's command-chain budget.
for power, item in itertools.product((1, 30), gear):
    commands += [f'data modify storage mysterybox:config enchant_level_min set value {power}',
                 f'data modify storage mysterybox:config enchant_level_max set value {power}',
                 f'item replace entity @e[tag=mbcheck.probe,limit=1] contents with {item}',
                 'function mysterybox:reward/prepare',
                 'function mbcheck:check/normal/'+item.split(':')[1],
                 'execute if data storage mysterybox:runtime reward.components."minecraft:enchantments"."minecraft:mending" run scoreboard players add #errors mbcheck 1']
commands += restore + ['kill @e[tag=mbcheck.probe]'] + restore_runtime + [
    'execute store result storage mbcheck:results enchantment_errors int 1 run scoreboard players get #errors mbcheck',
    'execute store result storage mbcheck:results enchantment_samples int 1 run scoreboard players get #samples mbcheck',
    'tellraw @s [{"text":"Enchantment checks: "},{"score":{"name":"#errors","objective":"mbcheck"}},{"text":" errors / "},{"score":{"name":"#samples","objective":"mbcheck"}},{"text":" samples"}]']
function('enchantments', commands)


def reward_case(name, item, mode='combat', bonus=(), potion=None, curse=False,
                mending_chance=0, seeded_infinity=False):
    """Exercise the actual preparation, visual, and entity-drop functions."""
    stack = {'id': item, 'count': 16 if item in ('minecraft:tnt', 'minecraft:bedrock')
             else 64 if item == 'minecraft:enchanted_golden_apple' else 1}
    if potion:
        stack['components'] = {'minecraft:potion_contents': {'potion': potion}}
    if seeded_infinity:
        stack['components'] = {'minecraft:enchantments': {'minecraft:infinity': 1}}
    stack_nbt = json.dumps(stack, separators=(',', ':'))
    observed = {'id': item, 'count': stack['count']}
    if potion:
        observed['components'] = dict(stack['components'])
    if curse and item not in gear:
        observed.setdefault('components', {})['minecraft:enchantments'] = {'minecraft:binding_curse': 1}
    expected_bonus = [
        dict(extra, components={'minecraft:enchantments': {'minecraft:binding_curse': 1}})
        if curse else extra
        for extra in bonus
    ]
    expected = (observed, *expected_bonus)
    checks = [
        f'data modify storage mysterybox:config loot_mode set value "{"default" if mode == "combat" else mode}"',
        f'data modify storage mysterybox:config binding_curse set value {int(curse)}',
        f'data modify storage mysterybox:config mending_basis_points set value {mending_chance}',
        'execute store result score #valid mbcheck run function mysterybox:reward/select_mode',
        'execute unless score #valid mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
        f'execute unless data storage mysterybox:runtime {{loot_mode:"{mode}",binding_curse:{int(curse)},mending_basis_points:{mending_chance}}} run scoreboard players add #errors mbcheck 1',
        # Preparation and drop must retain the chosen mode/flags despite later edits.
        f'data modify storage mysterybox:config loot_mode set value "{"default" if mode == "godmode" else "godmode"}"',
        f'data modify storage mysterybox:config binding_curse set value {int(not curse)}',
        f'data modify storage mysterybox:config mending_basis_points set value {10000 - mending_chance}',
        f'data modify entity @e[type=item_display,tag=mbcheck.probe,limit=1] item set value {stack_nbt}',
    ]
    if seeded_infinity:
        checks.append('execute unless data entity @e[type=item_display,tag=mbcheck.probe,limit=1] item.components."minecraft:enchantments"."minecraft:infinity" run scoreboard players add #errors mbcheck 1')
    checks += [
        'function mysterybox:reward/prepare',
        'scoreboard players add #samples mbcheck 1',
        f'execute unless data storage mysterybox:runtime reward{json.dumps(observed, separators=(",", ":"))} run scoreboard players add #errors mbcheck 1',
    ]
    if item not in gear:
        if curse:
            checks += [
                'execute store result score #count mbcheck run data get storage mysterybox:runtime reward.components."minecraft:enchantments"',
                'execute unless score #count mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
            ]
        else:
            checks.append('execute if data storage mysterybox:runtime reward.components."minecraft:enchantments" run scoreboard players add #errors mbcheck 1')
        checks += [
            f'data modify storage mbcheck:state expected_reward set value {json.dumps(observed, separators=(",", ":"))}',
            'scoreboard players set #changed mbcheck 0',
            'execute store success score #changed mbcheck run data modify storage mbcheck:state expected_reward set from storage mysterybox:runtime reward',
            'execute if score #changed mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
        ]
    if curse:
        checks += [
            'scoreboard players set #level mbcheck 0',
            'execute store result score #level mbcheck run data get storage mysterybox:runtime reward.components."minecraft:enchantments"."minecraft:binding_curse"',
            'execute unless score #level mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
        ]
    if item in gear:
        if mending_chance == 0:
            checks.append('execute if data storage mysterybox:runtime reward.components."minecraft:enchantments"."minecraft:mending" run scoreboard players add #errors mbcheck 1')
        else:
            checks += [
                'scoreboard players set #level mbcheck 0',
                'execute store result score #level mbcheck run data get storage mysterybox:runtime reward.components."minecraft:enchantments"."minecraft:mending"',
                'execute unless score #level mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
                'execute if data storage mysterybox:runtime reward.components."minecraft:enchantments"."minecraft:infinity" run scoreboard players add #errors mbcheck 1',
            ]
    if item == 'minecraft:shulker_box':
        checks.append('execute if data storage mysterybox:runtime reward.components."minecraft:container" run scoreboard players add #errors mbcheck 1')
    if mode == 'godmode' and item in gear:
        checks.append('function mbcheck:check/godmode/' + item.split(':')[1])
    checks += [
        'data merge entity @e[type=item_display,tag=mbcheck.probe,limit=1] {item_display:"gui"}',
        'function mysterybox:reward/visual',
        f'execute unless entity @e[type=item_display,tag=mbcheck.probe,nbt={{item_display:"{"gui" if item == "minecraft:trident" else "none"}"}}] run scoreboard players add #errors mbcheck 1',
        # Mode is captured by the purchase; later config edits cannot affect drops.
        'data modify storage mysterybox:config loot_mode set value "extended"',
        'function mysterybox:reward/drop',
        'execute positioned ~ ~1.62 ~ run tag @e[type=item,tag=!mbcheck.drop,distance=..0.65] add mbcheck.drop',
        'scoreboard players set #actual mbcheck 0',
        'execute as @e[type=item,tag=mbcheck.drop,distance=..2] run scoreboard players add #actual mbcheck 1',
        f'execute unless score #actual mbcheck matches {len(expected)} run scoreboard players add #errors mbcheck 1',
    ]
    for expected_stack in expected:
        nbt = json.dumps({'Item': expected_stack}, separators=(',', ':'))
        checks += ['scoreboard players set #matched mbcheck 0',
                   f'execute as @e[type=item,tag=mbcheck.drop,distance=..2,nbt={nbt}] run scoreboard players add #matched mbcheck 1',
                   'execute unless score #matched mbcheck matches 1 run scoreboard players add #errors mbcheck 1']
    for extra in expected_bonus:
        bonus_selector = json.dumps({'Item': {'id': extra['id'], 'count': extra['count']}}, separators=(',', ':'))
        if curse:
            checks += [
                'scoreboard players set #count mbcheck 0',
                f'execute as @e[type=item,tag=mbcheck.drop,distance=..2,nbt={bonus_selector}] store result score #count mbcheck run data get entity @s Item.components."minecraft:enchantments"',
                'execute unless score #count mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
                'scoreboard players set #level mbcheck 0',
                f'execute as @e[type=item,tag=mbcheck.drop,distance=..2,nbt={bonus_selector}] store result score #level mbcheck run data get entity @s Item.components."minecraft:enchantments"."minecraft:binding_curse"',
                'execute unless score #level mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
            ]
        else:
            checks.append(f'execute as @e[type=item,tag=mbcheck.drop,distance=..2,nbt={bonus_selector}] if data entity @s Item.components."minecraft:enchantments" run scoreboard players add #errors mbcheck 1')
    main_nbt = json.dumps({'Item': observed}, separators=(',', ':'))
    checks += [
        'scoreboard players set #changed mbcheck 0',
        f'execute store success score #changed mbcheck run data modify entity @e[type=item,tag=mbcheck.drop,distance=..2,nbt={main_nbt},limit=1] Item set from storage mysterybox:runtime reward',
        'execute if score #changed mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
    ]
    if item == 'minecraft:shulker_box':
        checks += [
            'execute if entity @e[type=minecraft:shulker,distance=..3] run scoreboard players add #errors mbcheck 1',
            'tag @e[type=minecraft:shulker,distance=..3] add mbcheck.spawned',
            'kill @e[type=minecraft:shulker,tag=mbcheck.spawned,distance=..3]',
        ]
    checks.append('kill @e[type=item,tag=mbcheck.drop,distance=..2]')
    function('rewards/case/' + name, checks)


reward_case('healing', 'minecraft:potion', potion='minecraft:strong_healing')
reward_case('splash', 'minecraft:splash_potion', potion='minecraft:swiftness')
reward_case('lingering', 'minecraft:lingering_potion', potion='minecraft:regeneration')
reward_case('shulker', 'minecraft:shulker_box')
reward_case('bow', 'minecraft:bow', bonus=({'id': 'minecraft:arrow', 'count': 64},))
reward_case('crossbow', 'minecraft:crossbow', bonus=({'id': 'minecraft:arrow', 'count': 64},))
reward_case('trident', 'minecraft:trident')
reward_case('tnt', 'minecraft:tnt', mode='godmode', bonus=({'id': 'minecraft:flint_and_steel', 'count': 1},))
reward_case('golden_apple', 'minecraft:enchanted_golden_apple', mode='godmode')
reward_case('bedrock', 'minecraft:bedrock', mode='godmode')
for item in ('netherite_sword', 'netherite_chestplate', 'netherite_pickaxe',
             'netherite_axe', 'crossbow', 'trident', 'brush'):
    reward_case('godmode_' + item, 'minecraft:' + item, mode='godmode',
                bonus=({'id': 'minecraft:arrow', 'count': 64},) if item == 'crossbow' else ())
reward_case('cursed_healing', 'minecraft:potion', potion='minecraft:strong_healing', curse=True)
reward_case('cursed_bow', 'minecraft:bow', bonus=({'id': 'minecraft:arrow', 'count': 64},), curse=True)
reward_case('cursed_tnt', 'minecraft:tnt', mode='godmode', bonus=({'id': 'minecraft:flint_and_steel', 'count': 1},), curse=True)
reward_case('cursed_bedrock', 'minecraft:bedrock', mode='godmode', curse=True)
reward_case('mending_bow', 'minecraft:bow', bonus=({'id': 'minecraft:arrow', 'count': 64},),
            mending_chance=10000, seeded_infinity=True)
reward_case('mending_crossbow', 'minecraft:crossbow', bonus=({'id': 'minecraft:arrow', 'count': 64},),
            mending_chance=10000)
reward_case('mending_pickaxe', 'minecraft:netherite_pickaxe', mending_chance=10000)
reward_case('mending_brush', 'minecraft:brush', mending_chance=10000)
reward_case('mending_trident', 'minecraft:trident', mending_chance=10000)
reward_case('mending_potion', 'minecraft:potion', potion='minecraft:strong_healing', mending_chance=10000)

rewards = [
    'data modify storage mbcheck:results reward_status set value "refused"',
    'data modify storage mbcheck:results reward_errors set value -1',
    'data modify storage mbcheck:results reward_samples set value 0',
    'execute unless score #state mb matches 0 run return run say Mystery box must be idle for reward checks',
    'execute unless entity @e[tag=mysterybox.anchor,limit=1] run return run say Place a mystery box before reward checks',
    'execute if entity @e[tag=mysterybox.reward] run return run say A reward display is already active',
    'execute at @e[tag=mysterybox.anchor,limit=1] positioned ~ ~1.62 ~ if entity @e[type=item,distance=..2] run return run say Clear item entities near the mystery box before reward checks',
    'execute at @e[tag=mysterybox.anchor,limit=1] if entity @e[type=minecraft:shulker,distance=..3] run return run say Clear shulkers near the mystery box before reward checks',
    'execute at @e[tag=mysterybox.anchor,limit=1] run function mbcheck:rewards/fixture',
]
function('rewards', rewards)
fixture = [
    'scoreboard objectives add mbcheck dummy',
    'scoreboard players set #errors mbcheck 0',
    'scoreboard players set #samples mbcheck 0',
    'data modify storage mbcheck:state saved_config set from storage mysterybox:config',
    'data modify storage mbcheck:state saved_runtime set from storage mysterybox:runtime',
    'data modify storage mysterybox:config vanishing_curse set value 0',
    'data modify storage mysterybox:config loot_mode set value "default"',
    'data modify storage mysterybox:config binding_curse set value 1',
    'data modify storage mysterybox:config mending_basis_points set value 670',
    'execute store result score #valid mbcheck run function mysterybox:reward/select_mode',
    'scoreboard players add #samples mbcheck 1',
    'execute unless score #valid mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
    'execute unless data storage mysterybox:runtime {loot_mode:"combat",binding_curse:1,mending_basis_points:670} run scoreboard players add #errors mbcheck 1',
    'data modify storage mysterybox:config loot_mode set value "invalid"',
    'execute store result score #valid mbcheck run function mysterybox:reward/select_mode',
    'scoreboard players add #samples mbcheck 1',
    'execute unless score #valid mbcheck matches 0 run scoreboard players add #errors mbcheck 1',
    'data modify storage mysterybox:config loot_mode set value "all"',
    'data modify storage mysterybox:config teddy_basis_points set value 1000',
    'data modify storage mysterybox:runtime loot_table set value "mysterybox:all_gear"',
    'function mysterybox:config/loot_upgrade',
    'scoreboard players add #samples mbcheck 1',
    'execute unless data storage mysterybox:config {loot_mode:"default",teddy_basis_points:400} run scoreboard players add #errors mbcheck 1',
    'execute unless data storage mysterybox:runtime {loot_table:"mysterybox:weapons_armor"} run scoreboard players add #errors mbcheck 1',
    'execute store result score #valid mbcheck run function mysterybox:reward/select_mode',
    'execute unless score #valid mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
    'execute unless data storage mysterybox:runtime {loot_mode:"combat"} run scoreboard players add #errors mbcheck 1',
    'data modify storage mysterybox:config enchant_level_min set value 30',
    'data modify storage mysterybox:config enchant_level_max set value 30',
    'summon item_display ~ ~ ~ {Tags:["mysterybox.reward","mbcheck.probe"],item:{id:"minecraft:paper",count:1}}',
]
fixture += ['function mbcheck:rewards/case/' + name for name in
            ('healing', 'splash', 'lingering', 'shulker', 'bow', 'crossbow',
             'trident', 'tnt', 'golden_apple', 'bedrock',
             *(f'godmode_{name}' for name in ('netherite_sword', 'netherite_chestplate',
                                             'netherite_pickaxe', 'netherite_axe',
                                             'crossbow', 'trident', 'brush')),
             'cursed_healing', 'cursed_bow', 'cursed_tnt', 'cursed_bedrock',
             'mending_bow', 'mending_crossbow', 'mending_pickaxe',
             'mending_brush', 'mending_trident', 'mending_potion')]
# Independent switches must affect primary and bonus stacks, even after config edits.
for binding, vanishing in itertools.product((0, 1), repeat=2):
    fixture += [
        f'data modify storage mysterybox:config binding_curse set value {binding}',
        f'data modify storage mysterybox:config vanishing_curse set value {vanishing}',
        'data modify storage mysterybox:config loot_mode set value "default"',
        'function mysterybox:reward/select_mode',
        f'data modify storage mysterybox:config binding_curse set value {1-binding}',
        f'data modify storage mysterybox:config vanishing_curse set value {1-vanishing}',
        'item replace entity @e[tag=mbcheck.probe,limit=1] contents with minecraft:tnt 16',
        'function mysterybox:reward/prepare',
        'function mysterybox:reward/drop',
        'execute positioned ~ ~1.62 ~ run tag @e[type=item,distance=..0.65] add mbcheck.drop',
        'scoreboard players add #samples mbcheck 1',
    ]
    for item, count in (('tnt', 16), ('flint_and_steel', 1)):
        selector = f'@e[type=item,tag=mbcheck.drop,nbt={{Item:{{id:"minecraft:{item}",count:{count}}}}},limit=1]'
        fixture.append(f'execute unless entity {selector} run scoreboard players add #errors mbcheck 1')
        for curse, enabled in (('binding_curse', binding), ('vanishing_curse', vanishing)):
            fixture.append(f'execute {"unless" if enabled else "if"} data entity {selector} Item.components."minecraft:enchantments"."minecraft:{curse}" run scoreboard players add #errors mbcheck 1')
    fixture.append('kill @e[type=item,tag=mbcheck.drop]')
# Exercise the 200/10000 inclusion boundary and vanilla eligibility independently.
for item, bind_roll, vanish_roll, binding, vanishing in (
    ('netherite_helmet', 200, 201, True, False),
    ('netherite_helmet', 201, 200, False, True),
    ('netherite_helmet', 200, 200, True, True),
    ('netherite_helmet', 201, 201, False, False),
    ('netherite_sword', 200, 200, False, True),
    ('potion', 200, 200, False, False),
):
    fixture += [
        f'item replace entity @e[tag=mbcheck.probe,limit=1] contents with minecraft:{item}',
        f'scoreboard players set #binding_roll mb {bind_roll}',
        f'scoreboard players set #vanishing_roll mb {vanish_roll}',
        'function mysterybox:reward/random_curses',
        'scoreboard players add #samples mbcheck 1',
    ]
    for curse, expected in (('binding_curse', binding), ('vanishing_curse', vanishing)):
        fixture.append(f'execute {"unless" if expected else "if"} data entity @e[tag=mbcheck.probe,limit=1] item.components."minecraft:enchantments"."minecraft:{curse}" run scoreboard players add #errors mbcheck 1')
fixture += [
    'kill @e[type=item_display,tag=mbcheck.probe]',
] + restore_runtime + restore + [
    'data modify storage mbcheck:results reward_status set value "completed"',
    'execute store result storage mbcheck:results reward_errors int 1 run scoreboard players get #errors mbcheck',
    'execute store result storage mbcheck:results reward_samples int 1 run scoreboard players get #samples mbcheck',
    'tellraw @a [{"text":"Reward checks: "},{"score":{"name":"#errors","objective":"mbcheck"}},{"text":" errors / "},{"score":{"name":"#samples","objective":"mbcheck"}},{"text":" samples"}]',
]
function('rewards/fixture', fixture)
function('restore_xp', ['$experience set @s $(levels) levels',
                        '$experience set @s $(points) points'])


def expect_xp(levels, points):
    """Assert active level and bar points independently of lifetime XpTotal."""
    return ['execute store result score #levels mbcheck run experience query @s levels',
            f'execute unless score #levels mbcheck matches {levels} run scoreboard players add #errors mbcheck 1',
            'execute store result score #points mbcheck run experience query @s points',
            f'execute unless score #points mbcheck matches {points} run scoreboard players add #errors mbcheck 1']


def expect_payment(levels, points, price, affordable, remaining=None):
    """Probe the price check and optionally verify an exact point debit."""
    commands = [f'data modify storage mysterybox:config price_points set value {price}',
                f'scoreboard players set #price mb {price}',
                f'experience set @s {levels} levels',
                f'experience set @s {points} points',
                'execute store result score #can_pay mbcheck run function mysterybox:economy/check',
                f'execute unless score #can_pay mbcheck matches {int(affordable)} run scoreboard players add #errors mbcheck 1']
    if remaining is not None:
        commands += ['execute store result score #charged mbcheck run function mysterybox:economy/charge',
                     'execute unless score #charged mbcheck matches 1 run scoreboard players add #errors mbcheck 1']
    commands += expect_xp(*(remaining if remaining is not None else (levels, points)))
    return commands


commands = setup + ['execute if score @s mb_xp_credit matches 1.. run return run tellraw @s {"text":"Wait for your pending teddy refund before testing.","color":"red"}',
                    'execute if score @s mb_xp_pt_credit matches 1.. run return run tellraw @s {"text":"Wait for your pending teddy refund before testing.","color":"red"}',
                    'execute store result storage mbcheck:state saved_xp.levels int 1 run experience query @s levels',
                    'execute store result storage mbcheck:state saved_xp.points int 1 run experience query @s points',
                    'data modify storage mysterybox:config teddy_basis_points set value 0',
                    'data modify storage mysterybox:config price_points set value 95',
                    'item replace entity @s weapon.mainhand with minecraft:stone',
                    'item replace entity @s weapon.offhand with minecraft:air',
                    'experience set @s 7 levels',
                    'experience set @s 3 points',
                    'execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:purchase']
commands += expect_xp(7, 3)
commands += ['execute unless score #state mb matches 0 run scoreboard players add #errors mbcheck 1',
             'experience set @s 30 levels',
             'experience set @s 37 points',
             'execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:purchase']
commands += expect_xp(29, 49)  # 1395 + 37 - 95 = 1288 + 49
commands += ['execute unless items entity @s weapon.mainhand minecraft:stone run scoreboard players add #errors mbcheck 1',
             'execute unless score #state mb matches 1 run scoreboard players add #errors mbcheck 1',
             'execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:purchase']
commands += expect_xp(29, 49)
commands += ['data modify storage mysterybox:runtime reward set value {id:"minecraft:stone",count:1}']
commands += ['execute at @e[tag=mysterybox.anchor,limit=1] store result score #before mbcheck run execute if entity @e[type=item,distance=..8]',
             'execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:box/finish',
             'execute at @e[tag=mysterybox.anchor,limit=1] store result score #after mbcheck run execute if entity @e[type=item,distance=..8]',
             'scoreboard players operation #after mbcheck -= #before mbcheck',
             'execute unless score #after mbcheck matches 1 run scoreboard players add #errors mbcheck 1',
             'scoreboard players set #timer mb 20',
             'execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:box/close_tick',
             'execute unless score #state mb matches 0 run scoreboard players add #errors mbcheck 1',
             'data modify storage mysterybox:config teddy_basis_points set value 10000',
             'data modify storage mysterybox:config relocate set value 1',
             'experience set @s 30 levels',
             'experience set @s 37 points',
             'item replace entity @s weapon.mainhand with minecraft:air',
             'execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:purchase']
commands += expect_xp(29, 49)
commands += ['execute unless score #bear mb matches 1 run scoreboard players add #errors mbcheck 1',
             'execute unless data storage mysterybox:runtime reward.components{"minecraft:item_model":"mysterybox:teddy"} run scoreboard players add #errors mbcheck 1',
             'execute unless score @s mb_xp_pt_credit matches 95 run scoreboard players add #errors mbcheck 1',
             'data modify storage mysterybox:config price_points set value 7',
             'function mysterybox:economy/tick']
commands += expect_xp(29, 49)
commands += ['scoreboard players operation @s mb_xp_due = #xp_clock mb',
             'function mysterybox:economy/tick']
commands += expect_xp(30, 37)
commands += ['execute if score @s mb_xp_pt_credit matches 1.. run scoreboard players add #errors mbcheck 1',
             'function mysterybox:economy/tick']
commands += expect_xp(30, 37)
commands += ['execute at @e[tag=mysterybox.anchor,limit=1] store result score #before mbcheck run execute if entity @e[type=item,distance=..8]',
             'execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:box/finish',
             'execute at @e[tag=mysterybox.anchor,limit=1] store result score #after mbcheck run execute if entity @e[type=item,distance=..8]',
             'execute unless score #after mbcheck = #before mbcheck run scoreboard players add #errors mbcheck 1',
             'scoreboard players set #timer mb 20',
             'execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:box/close_tick',
             'execute unless score #state mb matches 2 run scoreboard players add #errors mbcheck 1',
             'scoreboard players set #state mb 0',
             'scoreboard players set #phase mb 0']

# At each piecewise XP-curve boundary, one point below the new level cannot
# pay the exact threshold but the next level can. The high-level probes detect
# premature scoreboard overflow and accidental reliance on lifetime XpTotal.
commands += expect_payment(7, 4, 95, True, (0, 0))
commands += expect_payment(16, 41, 394, False)
commands += expect_payment(17, 0, 394, True, (0, 0))
commands += expect_payment(31, 120, 1628, False)
commands += expect_payment(32, 0, 1628, True, (0, 0))
commands += expect_payment(10000, 1000, 95, True, (10000, 905))
commands += expect_payment(21863, 75703, 2147483647, False)
commands += expect_payment(21863, 75704, 2147483647, True)
commands += expect_payment(21864, 0, 2147483647, True)

# Pre-upgrade mb_xp_credit is a LEVEL debt; it must never become a point debt.
commands += ['data modify storage mysterybox:config price_points set value 95',
             'scoreboard players set #price mb 95',
             'experience set @s 10 levels',
             'experience set @s 12 points',
             'scoreboard players set @s mb_xp_credit 7',
             'scoreboard players operation @s mb_xp_due = #xp_clock mb',
             'scoreboard players add @s mb_xp_due 4',
             'function mysterybox:economy/tick',
             'execute store result score #can_pay mbcheck run function mysterybox:economy/check',
             'execute unless score #can_pay mbcheck matches 0 run scoreboard players add #errors mbcheck 1']
commands += expect_xp(10, 12)
commands += ['scoreboard players operation @s mb_xp_due = #xp_clock mb',
             'function mysterybox:economy/tick',
             'execute store result score #levels mbcheck run experience query @s levels',
             'execute unless score #levels mbcheck matches 17 run scoreboard players add #errors mbcheck 1',
             'execute if score @s mb_xp_credit matches 1.. run scoreboard players add #errors mbcheck 1',
             'function mysterybox:economy/tick',
             'execute store result score #levels mbcheck run experience query @s levels',
             'execute unless score #levels mbcheck matches 17 run scoreboard players add #errors mbcheck 1',
             'execute store result score #can_pay mbcheck run function mysterybox:economy/check',
             'execute unless score #can_pay mbcheck matches 1 run scoreboard players add #errors mbcheck 1']
commands += ['execute store result storage mbcheck:results economy_errors int 1 run scoreboard players get #errors mbcheck',
             'tellraw @s [{"text":"XP-point/duplicate-purchase/teddy-refund checks: "},{"score":{"name":"#errors","objective":"mbcheck"}},{"text":" errors"}]'] + restore + [
                'function mbcheck:restore_xp with storage mbcheck:state saved_xp']
function('economy', commands)

# A bounded, air-only fixture; never overwrite terrain or the real box.
fixture_clear = ' '.join(f'if block ~{x} ~{y} ~{z} minecraft:air'
                         for x in range(-2, 3) for y in range(-1, 3) for z in range(-1, 2))
function('placement', [
    'execute unless dimension minecraft:overworld run return 0',
    'execute unless entity @s[gamemode=creative] run return 0',
    f'execute align xyz {fixture_clear} run return run function mbcheck:placement_fixture',
    'tellraw @s {text:"Placement fixture needs an empty 5x4x3 air volume around your feet; no blocks changed.",color:"red"}',
])
placement = setup + [
    'execute store result storage mbcheck:state saved_mode int 1 run scoreboard players get #mode mb',
    'scoreboard players set #mode mb 2',
    'scoreboard players set #good mb 0',
    'function mysterybox:placement/check',
    'execute unless score #good mb matches 0 run scoreboard players add #errors mbcheck 1',
    'fill ~-1 ~-1 ~ ~1 ~-1 ~ minecraft:stone',
    'fill ~-1 ~ ~-1 ~1 ~1 ~-1 minecraft:stone',
    'fill ~-1 ~ ~1 ~1 ~1 ~1 minecraft:stone',
    'fill ~-1 ~2 ~ ~1 ~2 ~ minecraft:stone',
    'scoreboard players set #mode mb 1',
    'scoreboard players set #good mb 0',
    'function mysterybox:placement/check',
    'execute unless score #good mb matches 1 run scoreboard players add #errors mbcheck 1',
]
for x in (-1, 0, 1):
    placement += [
        f'setblock ~{x} ~-1 ~ minecraft:air',
        'scoreboard players set #good mb 0',
        'function mysterybox:placement/check',
        'execute unless score #good mb matches 0 run scoreboard players add #errors mbcheck 1',
        f'setblock ~{x} ~-1 ~ minecraft:stone',
    ]
for y in (0, 1):
    placement += [
        f'setblock ~ ~{y} ~ minecraft:stone',
        'scoreboard players set #good mb 0',
        'function mysterybox:placement/check',
        'execute unless score #good mb matches 0 run scoreboard players add #errors mbcheck 1',
        f'setblock ~ ~{y} ~ minecraft:air',
    ]
placement += [
    'fill ~-2 ~-1 ~-1 ~2 ~2 ~1 minecraft:air',
    'execute store result score #mode mb run data get storage mbcheck:state saved_mode',
    'scoreboard players set #good mb 0',
    'execute store result storage mbcheck:results placement_errors int 1 run scoreboard players get #errors mbcheck',
    'tellraw @s [{text:"Grounded 3x2 placement checks: "},{score:{name:"#errors",objective:"mbcheck"}},{text:" errors"}]',
]
function('placement_fixture', placement)
files['pack.mcmeta'] = json.dumps({'pack': {'min_format': [121,0], 'max_format': [121,0], 'description': 'Mystery Box opt-in destructive test-world checks'}})
output = ROOT/'dist/mysterybox-checks-26.3.zip'
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
    archive.write(ROOT/'LICENSE', 'LICENSE')
    for name, contents in files.items():
        archive.writestr(name, contents)
print(output)
