execute store result score #mending_chance mb run data get storage mysterybox:runtime mending_basis_points
execute unless score #mending_chance mb matches 1..10000 run return 0
execute store result score #mending_roll mb run random value 1..10000
execute if score #mending_roll mb <= #mending_chance mb run function mysterybox:reward/add_mending
