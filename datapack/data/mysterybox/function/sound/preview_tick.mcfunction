scoreboard players add @s mb_music 1
scoreboard players operation #note_tick mb = @s mb_music
execute if score @s mb_music matches ..76 run function mysterybox:sound/melody
execute if score @s mb_music matches 77 if entity @s[tag=mysterybox.preview_teddy] run function mysterybox:sound/teddy_reveal
execute if score @s mb_music matches 77.. unless entity @s[tag=mysterybox.preview_teddy] run function mysterybox:sound/finished_tick
execute if score @s mb_music matches 117.. run function mysterybox:sound/closing with storage mysterybox:config
execute if score @s mb_music matches 117.. run kill @s
