execute if score #attempts mb matches 128.. run return run function mysterybox:placement/abort
execute if score #phase mb matches 0 run return run function mysterybox:placement/candidate
execute if score #phase mb matches 1 run function mysterybox:placement/wait with storage mysterybox:runtime target
