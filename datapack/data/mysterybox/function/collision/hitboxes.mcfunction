kill @e[type=interaction,tag=mysterybox.interaction]
kill @e[type=interaction,tag=mysterybox.guard]
summon interaction ~-1 ~ ~ {Tags:["mysterybox.all","mysterybox.interaction"],width:1.02f,height:2.002f,response:1b}
summon interaction ~0 ~ ~ {Tags:["mysterybox.all","mysterybox.interaction"],width:1.02f,height:2.002f,response:1b}
summon interaction ~1 ~ ~ {Tags:["mysterybox.all","mysterybox.interaction"],width:1.02f,height:2.002f,response:1b}
data modify entity @e[tag=mysterybox.anchor,limit=1] data.collision.hitboxes_version set value 2b
