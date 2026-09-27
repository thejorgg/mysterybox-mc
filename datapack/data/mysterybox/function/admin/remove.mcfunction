execute in minecraft:overworld at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:collision/remove
execute in minecraft:overworld at @e[tag=mysterybox.anchor,nbt={data:{owned_chunk:1b}},limit=1] run forceload remove ~ ~
execute if score #phase mb matches 1 in minecraft:overworld run function mysterybox:placement/reject with storage mysterybox:runtime target
execute in minecraft:overworld run kill @e[tag=mysterybox.all]
data modify storage mysterybox:runtime disabled set value 1b
data remove storage mysterybox:runtime initialized
data remove storage mysterybox:runtime boot_requested
scoreboard players set #state mb 0
scoreboard players set #phase mb 0
