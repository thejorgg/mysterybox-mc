"""Category-balanced Mystery Box loot tables for the versioned vanilla catalog."""

from collections import Counter
from math import lcm

CATEGORY_WEIGHTS = {'weapons': 50, 'armor': 20, 'tools': 15, 'potions': 10, 'misc': 5}


LOOT_MODES = {
    'default': 'combat',
    'combat': 'combat',
    'weapons': 'weapons',
    'weapons_armor': 'weapons_armor',
    'weapons_tools': 'weapons_tools',
    'extended': 'extended',
    'extra': 'extra',
    'godmode': 'godmode',
}

_POTION_CONTAINERS = ('minecraft:potion', 'minecraft:splash_potion', 'minecraft:lingering_potion')
_GODMODE_UNTIERED = {
    'minecraft:crossbow', 'minecraft:trident', 'minecraft:mace', 'minecraft:elytra',
    'minecraft:brush', 'minecraft:shears', 'minecraft:fishing_rod', 'minecraft:flint_and_steel',
}


def _unique(*groups):
    return list(dict.fromkeys(item for group in groups for item in group))


def gear_items(catalog):
    """Return every enchantable gear candidate once, including shared axes."""
    return _unique(catalog['weapons'], catalog['armor'], catalog['tools'])


def _item(name, count=1):
    entry = {'type': 'minecraft:item', 'name': name, 'weight': 1}
    if count != 1:
        entry['modifier'] = {'type': 'minecraft:set_count', 'count': count}
    return entry


def _potion(container, potion):
    return {
        'type': 'minecraft:item', 'name': container, 'weight': 1,
        'modifier': {
            'type': 'minecraft:set_components',
            'components': {'minecraft:potion_contents': {'potion': potion}},
        },
    }


def _table(entries, categories):
    # Exact integer weights give each category its share regardless of item count.
    # Within a category every distinct item/potion variant remains equally likely.
    counts = Counter(categories.get(entry['name'], 'misc') for entry in entries)
    unit = lcm(*counts.values())
    weighted = [
        dict(entry, weight=CATEGORY_WEIGHTS[category] * unit // counts[category])
        for entry in entries
        for category in (categories.get(entry['name'], 'misc'),)
    ]
    return {'type': 'minecraft:generic', 'pools': [{'rolls': 1, 'entries': weighted}]}


def loot_tables(catalog):
    """Map each canonical mode to its one-roll vanilla loot table."""
    weapons = catalog['weapons']
    armor = catalog['armor']
    tools = catalog['tools']
    categories = {name: 'tools' for name in tools}
    categories.update({name: 'armor' for name in armor})
    categories.update({name: 'weapons' for name in weapons})  # Axes count once.
    categories.update({name: 'potions' for name in _POTION_CONTAINERS})
    potions = [_potion(container, potion)
               for potion in _unique(catalog['potions']) for container in _POTION_CONTAINERS]
    combat_supplies = [_item('minecraft:enchanted_golden_apple', 2),
                       _item('minecraft:golden_apple', 4),
                       _item('minecraft:ender_pearl', 16),
                       _item('minecraft:tnt', 16)]
    extra_supplies = [_item('minecraft:emerald_block', 4),
                      _item('minecraft:shulker_box'),
                      _item('minecraft:wither_skeleton_skull')]
    templates = [_item(name) for name in _unique(catalog['smithing_templates'])]

    combat = [_item(name) for name in _unique(weapons, armor)] + potions + combat_supplies
    extended = [_item(name) for name in gear_items(catalog)] + potions + combat_supplies
    godmode_gear = [name for name in gear_items(catalog)
                    if name.startswith('minecraft:netherite_') or name in _GODMODE_UNTIERED]
    godmode = ([_item(name) for name in godmode_gear]
               + [_item('minecraft:enchanted_golden_apple', 64),
                  _item('minecraft:ender_pearl', 16), _item('minecraft:tnt', 16)]
               + extra_supplies + templates + [_item('minecraft:bedrock', 16)])

    return {
        'weapons': _table([_item(name) for name in _unique(weapons)], categories),
        'combat': _table(combat, categories),
        'weapons_armor': _table([_item(name) for name in _unique(weapons, armor)], categories),
        'weapons_tools': _table([_item(name) for name in _unique(weapons, tools)], categories),
        'extended': _table(extended, categories),
        'extra': _table(extended + extra_supplies + templates, categories),
        'godmode': _table(godmode, categories),
    }
