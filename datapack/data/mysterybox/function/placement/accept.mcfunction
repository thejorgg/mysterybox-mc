function mysterybox:sound/moving with storage mysterybox:config
function mysterybox:collision/transfer
function mysterybox:collision/remove
function mysterybox:box/beam_remove
execute if entity @e[tag=mysterybox.anchor,nbt={data:{owned_chunk:1b}}] run forceload remove ~ ~
execute as @e[tag=mysterybox.all] run tp @s @e[tag=mysterybox.probe,limit=1]
data modify entity @e[tag=mysterybox.anchor,limit=1] data.owned_chunk set value 0b
execute if score #candidate_owned mb matches 1 run data modify entity @e[tag=mysterybox.anchor,limit=1] data.owned_chunk set value 1b
data modify storage mysterybox:runtime position set from entity @e[tag=mysterybox.anchor,limit=1] Pos
kill @e[tag=mysterybox.probe]
scoreboard players set #state mb 0
scoreboard players set #phase mb 0
execute if score #crate mb matches 1 at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:box/beam_spawn
execute if score #crate mb matches 0 at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:box/spawn
execute at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:sound/moving with storage mysterybox:config
execute unless entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] at @e[tag=mysterybox.anchor,limit=1] run function mysterybox:collision/install
