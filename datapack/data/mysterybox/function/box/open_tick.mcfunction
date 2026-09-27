scoreboard players add #timer mb 1
execute if score #timer mb matches 2 run data merge entity @e[tag=mysterybox.reward,limit=1] {start_interpolation:0,interpolation_duration:75,transformation:{translation:[0f,1.62f,0f]}}
scoreboard players operation #frame mb = #timer mb
scoreboard players operation #frame mb %= #four mb
execute if score #timer mb matches ..76 if score #frame mb matches 0 run function mysterybox:reward/draw with storage mysterybox:runtime
execute if score #timer mb matches 77 run data modify entity @e[tag=mysterybox.reward,limit=1] item set from storage mysterybox:runtime reward
execute if score #timer mb matches 77 run function mysterybox:reward/visual
execute if score #timer mb matches 77 if score #bear mb matches 1 run function mysterybox:sound/teddy_reveal
scoreboard players operation #note_tick mb = #timer mb
execute if score #timer mb matches ..76 if data storage mysterybox:config {melody:1} run function mysterybox:sound/melody
execute if score #timer mb matches 77.. if score #bear mb matches 0 if data storage mysterybox:config {melody:1} run function mysterybox:sound/finished_tick
execute if score #timer mb matches 117.. run function mysterybox:box/finish
