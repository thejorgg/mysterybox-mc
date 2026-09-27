execute if data storage mysterybox:config {loot_mode:"all"} run data modify storage mysterybox:config loot_mode set value "default"
execute if data storage mysterybox:config {teddy_basis_points:1000} run data modify storage mysterybox:config teddy_basis_points set value 400
execute if data storage mysterybox:runtime {loot_table:"mysterybox:all_gear"} run data modify storage mysterybox:runtime loot_table set value "mysterybox:weapons_armor"
data modify storage mysterybox:runtime loot_sets_v1 set value 1b
