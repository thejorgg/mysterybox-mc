scoreboard players add #waiting mb 1
$execute if loaded $(x) 0 $(z) run return run function mysterybox:placement/probe with storage mysterybox:runtime target
execute if score #waiting mb matches 40.. run function mysterybox:placement/reject with storage mysterybox:runtime target
