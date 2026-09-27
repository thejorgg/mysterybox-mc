scoreboard players set #state mb 2
scoreboard players set #phase mb 0
scoreboard players set #attempts mb 0
execute store result score #mode mb run data get storage mysterybox:config placement
execute unless score #mode mb matches 0 run scoreboard players set #mode mb 1
