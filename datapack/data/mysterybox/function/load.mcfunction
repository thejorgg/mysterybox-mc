scoreboard objectives add mb dummy
scoreboard objectives add mb_music dummy
function mysterybox:economy/load
scoreboard players set #sixteen mb 16
scoreboard players set #four mb 4
execute unless score #state mb matches 0.. run scoreboard players set #state mb 0
function mysterybox:defaults
execute in minecraft:overworld run data remove entity @e[tag=mysterybox.anchor,limit=1] data.collision_blocked
