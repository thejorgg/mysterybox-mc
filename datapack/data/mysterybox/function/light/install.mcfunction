execute if data entity @e[tag=mysterybox.anchor,limit=1] data.light_air run return 0
execute unless block ~ ~1 ~ #minecraft:air run return 0
data modify entity @e[tag=mysterybox.anchor,limit=1] data.light_air set value "minecraft:air"
execute if block ~ ~1 ~ minecraft:cave_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.light_air set value "minecraft:cave_air"
execute if block ~ ~1 ~ minecraft:void_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.light_air set value "minecraft:void_air"
setblock ~ ~1 ~ minecraft:light[level=9,waterlogged=false]
