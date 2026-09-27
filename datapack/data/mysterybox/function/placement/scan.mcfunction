function mysterybox:placement/check
execute if score #good mb matches 1 run return 1
scoreboard players remove #depth mb 1
execute store result score #height mb run data get entity @s Pos[1]
execute unless score #height mb matches -62..318 run return 0
tp @s ~ ~-1 ~
execute if score #depth mb matches 1.. at @s run function mysterybox:placement/scan
