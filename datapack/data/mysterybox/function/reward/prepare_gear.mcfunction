function mysterybox:reward/enchant with storage mysterybox:config
data remove entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:mending"
data remove entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:binding_curse"
data remove entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:vanishing_curse"
execute store result score #enchanted mb run data get entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"
execute if score #enchanted mb matches 0 run function mysterybox:reward/fallback_enchant
execute if items entity @e[tag=mysterybox.reward,limit=1] contents #minecraft:enchantable/durability run function mysterybox:reward/mending
execute store result score #binding_roll mb run random value 1..10000
execute store result score #vanishing_roll mb run random value 1..10000
function mysterybox:reward/random_curses
execute if data storage mysterybox:runtime {loot_mode:"godmode"} run function mysterybox:reward/max_enchantments
