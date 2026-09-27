execute store result storage mysterybox:economy points int 1 run scoreboard players get @s mb_xp_pt_credit
execute store result score #xp_refunded mb run function mysterybox:economy/add_points with storage mysterybox:economy
execute unless score #xp_refunded mb matches 1 run return 0
tellraw @s [{text:"Teddy! Refunded ",color:"gold"},{score:{name:"@s",objective:"mb_xp_pt_credit"},color:"yellow"},{text:" XP points."}]
scoreboard players reset @s mb_xp_pt_credit
execute unless score @s mb_xp_credit matches 1.. run scoreboard players reset @s mb_xp_due
return 1
