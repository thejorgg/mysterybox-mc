execute unless data storage mysterybox:runtime boot_requested run function mysterybox:initialize_request
execute unless loaded ~ ~ ~ run return 0
execute align xz positioned ~0.5 ~ ~0.5 run summon marker ~ ~ ~ {Tags:["mysterybox.all","mysterybox.anchor"],data:{owned_chunk:0b}}
data modify entity @e[type=marker,tag=mysterybox.anchor,limit=1] data.owned_chunk set from storage mysterybox:runtime boot_owned
data modify storage mysterybox:runtime initialized set value 1b
scoreboard players set #crate mb 0
scoreboard players set #state mb 0
scoreboard players set #good mb 0
scoreboard players set #mode mb 0
execute as @e[type=marker,tag=mysterybox.anchor,limit=1] at @s positioned over world_surface run tp @s ~ ~ ~
execute at @e[type=marker,tag=mysterybox.anchor,limit=1] run function mysterybox:placement/check
execute if score #good mb matches 1 at @e[type=marker,tag=mysterybox.anchor,limit=1] run function mysterybox:box/spawn
execute if score #good mb matches 0 run function mysterybox:placement/start
