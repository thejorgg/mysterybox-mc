execute unless dimension minecraft:overworld run return run tellraw @s {text:"Place the mystery box in the Overworld.",color:"red"}
scoreboard players set #good mb 0
execute align xyz positioned ~0.5 ~ ~0.5 run function mysterybox:placement/check
execute unless score #good mb matches 1 run return run tellraw @s {"text":"The box needs a clear 3-wide, 2-high space over three solid floor blocks; the current box was not changed.","color":"red"}
execute align xyz positioned ~0.5 ~ ~0.5 run function mysterybox:admin/place_clear
