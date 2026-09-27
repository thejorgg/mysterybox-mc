execute unless entity @s[type=player] run return 0
execute unless dimension minecraft:overworld run return run tellraw @s {"text":"Run the sound preview in the Overworld.","color":"red"}
kill @e[type=marker,tag=mysterybox.music_preview]
summon marker ~ ~ ~ {Tags:["mysterybox.music_preview"]}
scoreboard players set @e[type=marker,tag=mysterybox.music_preview] mb_music 0
function mysterybox:sound/opening with storage mysterybox:config
tellraw @s {"text":"Playing the mystery-box weapon sounds here. No XP points charged.","color":"gold"}
