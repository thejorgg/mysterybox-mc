summon item ~ ~1.62 ~ {Tags:["mysterybox.drop_pending"],Item:{id:"minecraft:paper",count:1},PickupDelay:10s,Motion:[0d,0.12d,-0.12d]}
data modify entity @e[type=item,tag=mysterybox.drop_pending,limit=1] Item set from storage mysterybox:runtime reward
execute if data storage mysterybox:runtime reward{id:"minecraft:bow"} run function mysterybox:reward/arrows
execute if data storage mysterybox:runtime reward{id:"minecraft:crossbow"} run function mysterybox:reward/arrows
execute if data storage mysterybox:runtime reward{id:"minecraft:tnt"} run summon item ~ ~1.62 ~ {Tags:["mysterybox.drop_pending"],Item:{id:"minecraft:flint_and_steel",count:1},PickupDelay:10s,Motion:[0.08d,0.12d,-0.12d]}
execute if data storage mysterybox:runtime {binding_curse:1} as @e[type=item,tag=mysterybox.drop_pending] run data modify entity @s Item.components."minecraft:enchantments"."minecraft:binding_curse" set value 1
execute if data storage mysterybox:runtime {vanishing_curse:1} as @e[type=item,tag=mysterybox.drop_pending] run data modify entity @s Item.components."minecraft:enchantments"."minecraft:vanishing_curse" set value 1
tag @e[type=item,tag=mysterybox.drop_pending] remove mysterybox.drop_pending
