scoreboard players operation #edge_cx mb = #old_cx mb
scoreboard players remove #edge_cx mb 1
execute if score #cx mb = #edge_cx mb if score #cz mb = #old_cz mb if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{left_owned:1b}}}] run function mysterybox:collision/transfer_left
scoreboard players add #edge_cx mb 2
execute if score #cx mb = #edge_cx mb if score #cz mb = #old_cz mb if entity @e[tag=mysterybox.anchor,nbt={data:{collision:{right_owned:1b}}}] run function mysterybox:collision/transfer_right
