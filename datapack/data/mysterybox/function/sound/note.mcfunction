$scoreboard players set #note_volume mb $(volume)
scoreboard players operation #note_volume mb *= #music_volume mb
execute if score #note_volume mb matches 0 run return 0
execute store result storage mysterybox:runtime note.volume double 0.0001 run scoreboard players get #note_volume mb
$data modify storage mysterybox:runtime note.pitch set value $(pitch)
$data modify storage mysterybox:runtime note.sound set value "$(sound)"
function mysterybox:sound/play_note with storage mysterybox:runtime note
