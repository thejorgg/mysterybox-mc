execute store result score #sound_volume mb run data get storage mysterybox:config closing_volume
execute if score #sound_volume mb matches ..0 run return 0
execute if score #sound_volume mb matches 101.. run scoreboard players set #sound_volume mb 100
execute store result storage mysterybox:runtime sound.volume double 0.01 run scoreboard players get #sound_volume mb
$data modify storage mysterybox:runtime sound.sound set value "$(closing_sound)"
function mysterybox:sound/play_cue with storage mysterybox:runtime sound
