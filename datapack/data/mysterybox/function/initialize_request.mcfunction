execute store success score #forced mb run forceload query ~ ~
data modify storage mysterybox:runtime boot_owned set value 0b
execute if score #forced mb matches 0 run data modify storage mysterybox:runtime boot_owned set value 1b
execute if score #forced mb matches 0 run forceload add ~ ~
data modify storage mysterybox:runtime boot_requested set value 1b
