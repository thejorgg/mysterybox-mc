execute unless data storage mysterybox:config price_points run data modify storage mysterybox:config price_points set value 10
execute unless data storage mysterybox:config teddy_basis_points run data modify storage mysterybox:config teddy_basis_points set value 400
execute unless data storage mysterybox:config relocate run data modify storage mysterybox:config relocate set value 1
execute unless data storage mysterybox:config placement run data modify storage mysterybox:config placement set value 1
execute unless data storage mysterybox:config loot_mode run data modify storage mysterybox:config loot_mode set value "default"
execute unless data storage mysterybox:config binding_curse run data modify storage mysterybox:config binding_curse set value 0
execute unless data storage mysterybox:config vanishing_curse run data modify storage mysterybox:config vanishing_curse set value 0
execute unless data storage mysterybox:config mending_basis_points run data modify storage mysterybox:config mending_basis_points set value 670
execute unless data storage mysterybox:config enchant_level_min run data modify storage mysterybox:config enchant_level_min set value 1
execute unless data storage mysterybox:config enchant_level_max run data modify storage mysterybox:config enchant_level_max set value 30
execute unless data storage mysterybox:config opening_sound run data modify storage mysterybox:config opening_sound set value "minecraft:block.chest.open"
execute unless data storage mysterybox:config closing_sound run data modify storage mysterybox:config closing_sound set value "minecraft:block.chest.close"
execute unless data storage mysterybox:config teddy_sound run data modify storage mysterybox:config teddy_sound set value "mysterybox:teddy_laugh"
execute unless data storage mysterybox:config dragon_sound run data modify storage mysterybox:config dragon_sound set value "minecraft:entity.ender_dragon.growl"
execute unless data storage mysterybox:config moving_sound run data modify storage mysterybox:config moving_sound set value "minecraft:entity.enderman.teleport"
execute unless data storage mysterybox:config melody run data modify storage mysterybox:config melody set value 1
execute unless data storage mysterybox:config melody_volume run data modify storage mysterybox:config melody_volume set value 100
execute unless data storage mysterybox:config finished_volume run data modify storage mysterybox:config finished_volume set value 100
execute unless data storage mysterybox:config teddy_volume run data modify storage mysterybox:config teddy_volume set value 70
execute unless data storage mysterybox:config dragon_volume run data modify storage mysterybox:config dragon_volume set value 70
execute unless data storage mysterybox:config opening_volume run data modify storage mysterybox:config opening_volume set value 70
execute unless data storage mysterybox:config closing_volume run data modify storage mysterybox:config closing_volume set value 70
execute unless data storage mysterybox:config moving_volume run data modify storage mysterybox:config moving_volume set value 70
execute if data storage mysterybox:config {teddy_sound:"minecraft:entity.ghast.warn"} run data modify storage mysterybox:config teddy_sound set value "mysterybox:teddy_laugh"
execute if data storage mysterybox:config {teddy_sound:"minecraft:entity.witch.celebrate"} run data modify storage mysterybox:config teddy_sound set value "mysterybox:teddy_laugh"
data remove storage mysterybox:config price
data remove storage mysterybox:config price_levels
data remove storage mysterybox:config reward_sound
execute if data storage mysterybox:config {placement:2} run data modify storage mysterybox:config placement set value 1
execute unless data storage mysterybox:runtime {loot_sets_v1:1b} run function mysterybox:config/loot_upgrade
execute unless data storage mysterybox:runtime {separate_curses_v1:1b} run function mysterybox:config/curse_upgrade
execute unless data storage mysterybox:runtime {price_ten_v1:1b} run function mysterybox:config/price_upgrade
