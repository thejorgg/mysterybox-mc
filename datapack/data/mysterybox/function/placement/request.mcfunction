$execute store success score #already_forced mb run forceload query $(x) $(z)
scoreboard players set #candidate_owned mb 0
$execute if score #already_forced mb matches 0 store success score #candidate_owned mb run forceload add $(x) $(z)
scoreboard players set #phase mb 1
scoreboard players set #waiting mb 0
