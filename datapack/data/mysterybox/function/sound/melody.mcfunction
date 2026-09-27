execute store result score #music_volume mb run data get storage mysterybox:config melody_volume
execute if score #music_volume mb matches ..0 run return 0
execute if score #music_volume mb matches 101.. run scoreboard players set #music_volume mb 100
execute if score #note_tick mb matches 1 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":90}
execute if score #note_tick mb matches 3 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.49830708,"volume":90}
execute if score #note_tick mb matches 7 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":85}
execute if score #note_tick mb matches 8 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.12246205,"volume":95}
execute if score #note_tick mb matches 17 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":85}
execute if score #note_tick mb matches 19 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.49830708,"volume":70}
execute if score #note_tick mb matches 19 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.58740105,"volume":75}
execute if score #note_tick mb matches 26 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.05946309,"volume":70}
execute if score #note_tick mb matches 26 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.12246205,"volume":75}
execute if score #note_tick mb matches 32 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":90}
execute if score #note_tick mb matches 36 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.41421356,"volume":85}
execute if score #note_tick mb matches 38 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":85}
execute if score #note_tick mb matches 39 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.41421356,"volume":80}
execute if score #note_tick mb matches 40 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":85}
execute if score #note_tick mb matches 43 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":0.89089872,"volume":90}
execute if score #note_tick mb matches 48 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.12246205,"volume":90}
execute if score #note_tick mb matches 50 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":80}
execute if score #note_tick mb matches 51 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.49830708,"volume":95}
execute if score #note_tick mb matches 56 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":85}
execute if score #note_tick mb matches 57 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.12246205,"volume":75}
execute if score #note_tick mb matches 60 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.78179744,"volume":95}
execute if score #note_tick mb matches 66 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.33483985,"volume":85}
execute if score #note_tick mb matches 70 run function mysterybox:sound/note {"sound":"minecraft:block.note_block.harp","pitch":1.78179744,"volume":100}
