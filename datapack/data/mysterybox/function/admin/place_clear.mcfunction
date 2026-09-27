function mysterybox:admin/remove
data remove storage mysterybox:runtime disabled
execute store success score #forced mb run forceload query ~ ~
execute if score #forced mb matches 0 run forceload add ~ ~
summon marker ~ ~ ~ {Tags:["mysterybox.all","mysterybox.anchor"],data:{owned_chunk:0b}}
execute if score #forced mb matches 0 run data modify entity @e[tag=mysterybox.anchor,limit=1] data.owned_chunk set value 1b
data modify storage mysterybox:runtime initialized set value 1b
function mysterybox:box/spawn
