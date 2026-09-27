summon item_display ~ ~ ~ {"Tags":["mysterybox.all","mysterybox.part","mysterybox.body"],"item":{"id":"minecraft:paper","count":1,"components":{"minecraft:item_model":"mysterybox:body"}},"transformation":{"translation":[0,0,0],"scale":[1,1,1],"left_rotation":[0.0,0.0,0.0,1.0],"right_rotation":[0.0,1.0,0.0,0.0]},"view_range":2}
summon item_display ~ ~ ~ {"Tags":["mysterybox.all","mysterybox.part","mysterybox.lid"],"item":{"id":"minecraft:paper","count":1,"components":{"minecraft:item_model":"mysterybox:lid"}},"transformation":{"translation":[0,0.875,0.5],"scale":[1,1,1],"left_rotation":[0.0,0.0,0.0,1.0],"right_rotation":[0.0,1.0,0.0,0.0]},"view_range":2}
summon item_display ~ ~ ~ {"Tags":["mysterybox.all","mysterybox.part","mysterybox.shine"],"item":{"id":"minecraft:paper","count":1,"components":{"minecraft:item_model":"mysterybox:shine"}},"transformation":{"translation":[0,0.5625,0],"scale":[0,0,0],"left_rotation":[0.0,0.0,0.0,1.0],"right_rotation":[0.0,1.0,0.0,0.0]},"view_range":2,"brightness":{"block":15,"sky":15}}
scoreboard players set #crate mb 1
scoreboard players set #state mb 0
data modify storage mysterybox:runtime position set from entity @e[tag=mysterybox.anchor,limit=1] Pos
function mysterybox:collision/install
function mysterybox:box/beam_spawn
