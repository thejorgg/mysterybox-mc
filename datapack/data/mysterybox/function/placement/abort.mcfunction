scoreboard players set #state mb 0
tellraw @a {text:"Mystery box: no clear destination found within 16–64 blocks. The existing box has not moved.",color:"yellow"}
execute if score #crate mb matches 0 run tellraw @a {text:"No suitable first spawn was found. An operator can use /function mysterybox:admin/place at a chosen Overworld location.",color:"yellow"}
