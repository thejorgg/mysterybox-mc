scoreboard players add #attempts mb 1
execute store result score #dx mb run random value -64..64
execute store result score #dz mb run random value -64..64
scoreboard players operation #distance mb = #dx mb
scoreboard players operation #distance mb *= #dx mb
scoreboard players operation #square mb = #dz mb
scoreboard players operation #square mb *= #dz mb
scoreboard players operation #distance mb += #square mb
execute unless score #distance mb matches 256..4096 run return 0
execute store result score #x mb run data get entity @e[tag=mysterybox.anchor,limit=1] Pos[0]
execute store result score #z mb run data get entity @e[tag=mysterybox.anchor,limit=1] Pos[2]
scoreboard players operation #x mb += #dx mb
scoreboard players operation #z mb += #dz mb
scoreboard players operation #cx mb = #x mb
scoreboard players operation #cz mb = #z mb
scoreboard players operation #cx mb /= #sixteen mb
scoreboard players operation #cz mb /= #sixteen mb
execute store result score #old_cx mb run data get entity @e[tag=mysterybox.anchor,limit=1] Pos[0] 0.0625
execute store result score #old_cz mb run data get entity @e[tag=mysterybox.anchor,limit=1] Pos[2] 0.0625
execute if score #cx mb = #old_cx mb if score #cz mb = #old_cz mb run return 0
execute unless score #x mb matches -29999980..29999980 run return 0
execute unless score #z mb matches -29999980..29999980 run return 0
execute store result storage mysterybox:runtime target.x int 1 run scoreboard players get #x mb
execute store result storage mysterybox:runtime target.z int 1 run scoreboard players get #z mb
execute store result storage mysterybox:runtime target.y int 1 run random value -63..318
function mysterybox:placement/request with storage mysterybox:runtime target
