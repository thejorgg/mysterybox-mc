$summon marker $(x) $(y) $(z) {Tags:["mysterybox.probe"]}
execute if score #mode mb matches 0 as @e[tag=mysterybox.probe,limit=1] at @s positioned over world_surface run tp @s ~ ~ ~
scoreboard players set #good mb 0
scoreboard players set #depth mb 64
execute unless score #mode mb matches 1 run scoreboard players set #depth mb 1
execute as @e[tag=mysterybox.probe,limit=1] at @s run function mysterybox:placement/scan
execute if score #good mb matches 1 run function mysterybox:placement/accept
execute if score #good mb matches 0 run function mysterybox:placement/reject with storage mysterybox:runtime target
