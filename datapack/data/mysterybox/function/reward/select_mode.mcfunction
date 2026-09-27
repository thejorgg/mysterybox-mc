execute if data storage mysterybox:config {loot_mode:"default"} run return run function mysterybox:reward/mode_combat
execute if data storage mysterybox:config {loot_mode:"combat"} run return run function mysterybox:reward/mode_combat
execute if data storage mysterybox:config {loot_mode:"weapons"} run return run function mysterybox:reward/mode_weapons
execute if data storage mysterybox:config {loot_mode:"weapons_armor"} run return run function mysterybox:reward/mode_weapons_armor
execute if data storage mysterybox:config {loot_mode:"weapons_tools"} run return run function mysterybox:reward/mode_weapons_tools
execute if data storage mysterybox:config {loot_mode:"extended"} run return run function mysterybox:reward/mode_extended
execute if data storage mysterybox:config {loot_mode:"extra"} run return run function mysterybox:reward/mode_extra
execute if data storage mysterybox:config {loot_mode:"godmode"} run return run function mysterybox:reward/mode_godmode
return 0
