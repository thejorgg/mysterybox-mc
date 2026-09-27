execute if score #crate mb matches 1 unless entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] run function mysterybox:collision/upgrade
execute if score #crate mb matches 1 if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] unless entity @e[tag=mysterybox.anchor,nbt={data:{collision:{hitboxes_version:2b}}}] run function mysterybox:collision/hitboxes
execute if score #crate mb matches 1 unless entity @e[tag=mysterybox.anchor,nbt={data:{segmented_beams:4b}}] run function mysterybox:box/beam_spawn
execute if score #crate mb matches 1 if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] run function mysterybox:light/install
execute as @e[type=interaction,tag=mysterybox.interaction] if data entity @s interaction on target run function mysterybox:purchase
execute as @e[type=interaction,tag=mysterybox.interaction] run data remove entity @s interaction
execute if score #state mb matches 3 run function mysterybox:box/close_tick
execute if score #state mb matches 1 run function mysterybox:box/open_tick
execute if score #state mb matches 2 run function mysterybox:placement/tick
