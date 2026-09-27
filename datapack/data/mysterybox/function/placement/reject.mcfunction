kill @e[tag=mysterybox.probe]
$execute if score #candidate_owned mb matches 1 run forceload remove $(x) $(z)
scoreboard players set #phase mb 0
