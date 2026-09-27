function mysterybox:economy/tick
execute in minecraft:overworld as @e[type=marker,tag=mysterybox.music_preview] at @s run function mysterybox:sound/preview_tick
execute if data storage mysterybox:runtime {disabled:1b} run return 0
execute unless data storage mysterybox:runtime {initialized:1b} run function mysterybox:initialize
execute in minecraft:overworld at @e[type=marker,tag=mysterybox.anchor,limit=1] run function mysterybox:box/tick
