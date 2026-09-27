scoreboard players operation #xp_factor mb = #xp_levels mb
scoreboard players operation #xp_factor mb *= #xp_five mb
scoreboard players remove #xp_factor mb 81
scoreboard players operation #balance mb = #xp_levels mb
scoreboard players operation #balance mb *= #xp_factor mb
scoreboard players operation #balance mb /= #xp_two mb
scoreboard players add #balance mb 360
