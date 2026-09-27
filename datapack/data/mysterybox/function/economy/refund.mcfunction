execute unless entity @s[type=player] run return 0
execute unless score @s mb_xp_due <= #xp_clock mb run return 0
execute if score @s mb_xp_pt_credit matches 1.. run return run function mysterybox:economy/refund_points
execute if score @s mb_xp_credit matches 1.. run return run function mysterybox:economy/refund_legacy_levels
return 0
