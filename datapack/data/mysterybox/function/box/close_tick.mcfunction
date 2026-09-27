scoreboard players add #timer mb 1
execute unless score #timer mb matches 20.. run return 0
scoreboard players set #state mb 0
execute if score #bear mb matches 1 run function mysterybox:placement/start
