execute store result storage mysterybox:economy levels int 1 run scoreboard players get @s mb_xp_credit
execute store result score #xp_refunded mb run function mysterybox:economy/add_levels with storage mysterybox:economy
execute unless score #xp_refunded mb matches 1 run return 0
tellraw @s [{text:"Teddy! Refunded ",color:"gold"},{score:{name:"@s",objective:"mb_xp_credit"},color:"yellow"},{text:" XP levels from your earlier purchase."}]
scoreboard players reset @s mb_xp_credit
execute unless score @s mb_xp_pt_credit matches 1.. run scoreboard players reset @s mb_xp_due
return 1
