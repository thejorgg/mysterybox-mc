execute if items entity @e[tag=mysterybox.reward,limit=1] contents #mysterybox:gear run function mysterybox:reward/prepare_gear
execute if data storage mysterybox:runtime {binding_curse:1} run data modify entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:binding_curse" set value 1
execute if data storage mysterybox:runtime {vanishing_curse:1} run data modify entity @e[tag=mysterybox.reward,limit=1] item.components."minecraft:enchantments"."minecraft:vanishing_curse" set value 1
data modify storage mysterybox:runtime reward set from entity @e[tag=mysterybox.reward,limit=1] item
