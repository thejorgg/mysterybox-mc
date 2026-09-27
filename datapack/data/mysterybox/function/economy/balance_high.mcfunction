scoreboard players operation #xp_factor mb = #xp_levels mb
scoreboard players operation #xp_factor mb *= #xp_nine mb
scoreboard players remove #xp_factor mb 325
scoreboard players operation #balance mb = #xp_levels mb
scoreboard players operation #balance mb /= #xp_two mb
scoreboard players operation #balance mb *= #xp_factor mb
scoreboard players operation #xp_odd mb = #xp_levels mb
scoreboard players operation #xp_odd mb %= #xp_two mb
execute if score #xp_odd mb matches 1 run scoreboard players operation #xp_factor mb /= #xp_two mb
execute if score #xp_odd mb matches 1 run scoreboard players operation #balance mb += #xp_factor mb
scoreboard players add #balance mb 2220
