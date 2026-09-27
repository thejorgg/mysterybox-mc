execute if entity @e[tag=mysterybox.anchor,nbt={data:{collision_blocked:1b}}] run return 0
function mysterybox:collision/check
execute if score #clear_base mb matches 1 run return run function mysterybox:collision/install
tellraw @a {"text":"Mystery box collision upgrade blocked: its 3x1 base and row above must be empty. Clear the obstruction and /reload, or use admin/place at a clear location. No terrain was overwritten.","color":"yellow"}
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision_blocked set value 1b
