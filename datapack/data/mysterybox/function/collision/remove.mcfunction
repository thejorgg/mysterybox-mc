execute unless entity @e[tag=mysterybox.anchor,nbt={data:{collision:{active:1b}}}] run return 0
function mysterybox:light/remove
function mysterybox:collision/restore with entity @e[tag=mysterybox.anchor,limit=1] data.collision
kill @e[type=interaction,tag=mysterybox.interaction]
kill @e[type=interaction,tag=mysterybox.guard]
execute if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{left_owned:1b}}}] run forceload remove ~-1 ~
execute if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{right_owned:1b}}}] run forceload remove ~1 ~
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.active set value 0b
