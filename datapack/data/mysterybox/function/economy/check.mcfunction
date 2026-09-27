execute unless entity @s[type=player] run return 0
execute unless score #price mb matches 0.. run return run function mysterybox:economy/config_error
execute store result storage mysterybox:economy price int 1 run scoreboard players get #price mb
execute store result score #xp_price_valid mb run function mysterybox:economy/validate_price with storage mysterybox:economy
execute unless score #xp_price_valid mb matches 1 run return run function mysterybox:economy/config_error
function mysterybox:economy/refund
execute if score @s mb_xp_pt_credit matches 1.. run return run function mysterybox:economy/pending
execute if score @s mb_xp_credit matches 1.. run return run function mysterybox:economy/pending
execute if score #price mb matches 0 run return 1
function mysterybox:economy/balance
execute if score #balance mb < #price mb run return run function mysterybox:economy/insufficient
return 1
