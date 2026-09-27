execute if score #bear mb matches 0 run function mysterybox:reward/drop
scoreboard players set #state mb 3
scoreboard players set #timer mb 0
data merge entity @e[tag=mysterybox.lid,limit=1] {start_interpolation:0,interpolation_duration:20,transformation:{left_rotation:[0f,0f,0f,1f]}}
data merge entity @e[tag=mysterybox.shine,limit=1] {transformation:{scale:[0f,0f,0f]}}
kill @e[tag=mysterybox.reward]
function mysterybox:sound/closing with storage mysterybox:config
