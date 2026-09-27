function mysterybox:collision/check
execute unless score #clear_base mb matches 1 run return 0
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.left_owned set value 0b
execute store success score #edge_forced mb run forceload query ~-1 ~
execute if score #edge_forced mb matches 0 store success entity @e[tag=mysterybox.anchor,limit=1] data.collision.left_owned byte 1 run forceload add ~-1 ~
execute store success score #edge_forced mb run forceload query ~-1 ~
execute unless score #edge_forced mb matches 1 run return 0
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.right_owned set value 0b
execute store success score #edge_forced mb run forceload query ~1 ~
execute if score #edge_forced mb matches 0 store success entity @e[tag=mysterybox.anchor,limit=1] data.collision.right_owned byte 1 run forceload add ~1 ~
execute store success score #edge_forced mb run forceload query ~1 ~
execute unless score #edge_forced mb matches 1 run return 0
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.left set value "minecraft:air"
execute if block ~-1 ~ ~ minecraft:cave_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.left set value "minecraft:cave_air"
execute if block ~-1 ~ ~ minecraft:void_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.left set value "minecraft:void_air"
setblock ~-1 ~ ~ minecraft:barrier
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.center set value "minecraft:air"
execute if block ~0 ~ ~ minecraft:cave_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.center set value "minecraft:cave_air"
execute if block ~0 ~ ~ minecraft:void_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.center set value "minecraft:void_air"
setblock ~0 ~ ~ minecraft:barrier
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.right set value "minecraft:air"
execute if block ~1 ~ ~ minecraft:cave_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.right set value "minecraft:cave_air"
execute if block ~1 ~ ~ minecraft:void_air run data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.right set value "minecraft:void_air"
setblock ~1 ~ ~ minecraft:barrier
function mysterybox:collision/hitboxes
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.active set value 1b
function mysterybox:light/install
data remove entity @e[tag=mysterybox.anchor,limit=1] data.collision_blocked
