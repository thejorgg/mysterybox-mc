scoreboard players add #xp_clock mb 1
execute if score #xp_clock mb matches 1000000.. run function mysterybox:economy/rebase_clock
execute as @a[scores={mb_xp_pt_credit=1..}] if score @s mb_xp_due <= #xp_clock mb run function mysterybox:economy/refund
execute as @a[scores={mb_xp_credit=1..}] if score @s mb_xp_due <= #xp_clock mb run function mysterybox:economy/refund
