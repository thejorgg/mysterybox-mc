execute unless entity @s[type=player] run return 0
execute unless score #price mb matches 1.. run return 0
execute if score @s mb_xp_pt_credit matches 1.. run return 0
execute if score @s mb_xp_credit matches 1.. run return 0
scoreboard players operation @s mb_xp_pt_credit = #price mb
scoreboard players operation @s mb_xp_due = #xp_clock mb
scoreboard players add @s mb_xp_due 76
return 1
