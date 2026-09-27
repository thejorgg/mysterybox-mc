execute store result score #music_volume mb run data get storage mysterybox:config finished_volume
execute if score #music_volume mb matches ..0 run return 0
execute if score #music_volume mb matches 101.. run scoreboard players set #music_volume mb 100
execute if score #note_tick mb matches 1 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.88774863,"volume":100}
execute if score #note_tick mb matches 7 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.68179283,"volume":95}
execute if score #note_tick mb matches 13 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.68179283,"volume":90}
execute if score #note_tick mb matches 18 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.0,"volume":85}
execute if score #note_tick mb matches 24 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":0.66741993,"volume":65}
execute if score #note_tick mb matches 24 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":0.89089872,"volume":90}
