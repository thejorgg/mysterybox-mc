execute store result score #xp_levels mb run experience query @s levels
execute store result score #xp_bar mb run experience query @s points
execute if score #xp_levels mb matches 21864.. run return run scoreboard players set #balance mb 2147483647
execute if score #xp_levels mb matches ..16 run function mysterybox:economy/balance_low
execute if score #xp_levels mb matches 17..31 run function mysterybox:economy/balance_mid
execute if score #xp_levels mb matches 32.. run function mysterybox:economy/balance_high
scoreboard players set #xp_headroom mb 2147483647
scoreboard players operation #xp_headroom mb -= #balance mb
execute if score #xp_bar mb >= #xp_headroom mb run return run scoreboard players set #balance mb 2147483647
scoreboard players operation #balance mb += #xp_bar mb
