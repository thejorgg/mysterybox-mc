execute unless entity @s[type=player,gamemode=!spectator] run return 0
execute unless score #state mb matches 0 run return run tellraw @s {text:"The mystery box is busy.",color:"gray"}
execute store result score #price mb run data get storage mysterybox:config price_points
execute store result score #chance mb run data get storage mysterybox:config teddy_basis_points
execute store result score #mending_chance mb run data get storage mysterybox:config mending_basis_points
execute store result score #minimum mb run data get storage mysterybox:config enchant_level_min
execute store result score #maximum mb run data get storage mysterybox:config enchant_level_max
execute unless score #chance mb matches 0..10000 run return run function mysterybox:config_error
execute unless score #mending_chance mb matches 0..10000 run return run function mysterybox:config_error
execute unless score #minimum mb matches 1..30 run return run function mysterybox:config_error
execute unless score #maximum mb matches 1..30 run return run function mysterybox:config_error
execute if score #minimum mb > #maximum mb run return run function mysterybox:config_error
execute unless data storage mysterybox:config {binding_curse:0} unless data storage mysterybox:config {binding_curse:1} run return run function mysterybox:config_error
execute unless data storage mysterybox:config {vanishing_curse:0} unless data storage mysterybox:config {vanishing_curse:1} run return run function mysterybox:config_error
execute store result score #loot_valid mb run function mysterybox:reward/select_mode
execute unless score #loot_valid mb matches 1 run return run function mysterybox:config_error
execute store result score #can_pay mb run function mysterybox:economy/check
execute unless score #can_pay mb matches 1 run return 0
execute store result score #charged mb run function mysterybox:economy/charge
execute unless score #charged mb matches 1 run return 0
scoreboard players set #state mb 1
scoreboard players set #timer mb 0
scoreboard players set #bear mb 0
execute store result score #roll mb run random value 1..10000
execute if score #roll mb <= #chance mb if data storage mysterybox:config {relocate:1} run scoreboard players set #bear mb 1
execute if score #bear mb matches 1 run function mysterybox:economy/queue_teddy
summon item_display ~ ~ ~ {Tags:["mysterybox.all","mysterybox.reward"],billboard:"vertical",transformation:{translation:[0f,0f,0f],scale:[0.8f,0.8f,0.8f],left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f]},item:{id:"minecraft:paper",count:1}}
function mysterybox:reward/draw with storage mysterybox:runtime
execute if score #bear mb matches 0 run function mysterybox:reward/prepare
execute if score #bear mb matches 1 run data modify storage mysterybox:runtime reward set value {id:"minecraft:paper",count:1,components:{"minecraft:item_model":"mysterybox:teddy"}}
data merge entity @e[tag=mysterybox.lid,limit=1] {start_interpolation:0,interpolation_duration:20,transformation:{left_rotation:[0.79335334f,0f,0f,0.60876143f]}}
data merge entity @e[tag=mysterybox.shine,limit=1] {transformation:{scale:[1f,1f,1f]}}
function mysterybox:sound/opening with storage mysterybox:config
