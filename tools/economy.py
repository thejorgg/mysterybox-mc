"""Generate buyer-owned point payments and persistent, reveal-time teddy refunds.

Call economy/load after creating the mb objective, and economy/tick before the
main tick's disabled guard. Purchase captures config.price_points in #price mb,
checks all config, requires economy/check to return 1, then calls economy/charge.
After the teddy roll, call economy/queue_teddy as the same buyer when #bear is 1.
None of these functions change the executor or need a held item.
"""

CLOCK_SPAN = 1_000_000


def register(function, reveal_tick):
    if type(reveal_tick) is not int or not 1 < reveal_tick < CLOCK_SPAN:
        raise ValueError('reveal_tick must be an integer from 2 to 999999')

    function('economy/load', f'''
        scoreboard objectives add mb_xp_credit dummy
        scoreboard objectives add mb_xp_pt_credit dummy
        scoreboard objectives add mb_xp_due dummy
        scoreboard players add #xp_clock mb 0
        scoreboard players set #xp_span mb {CLOCK_SPAN}
        scoreboard players set #xp_zero mb 0
        scoreboard players set #xp_two mb 2
        scoreboard players set #xp_five mb 5
        scoreboard players set #xp_nine mb 9
    ''')
    function('economy/tick', f'''
        scoreboard players add #xp_clock mb 1
        execute if score #xp_clock mb matches {CLOCK_SPAN}.. run function mysterybox:economy/rebase_clock
        execute as @a[scores={{mb_xp_pt_credit=1..}}] if score @s mb_xp_due <= #xp_clock mb run function mysterybox:economy/refund
        execute as @a[scores={{mb_xp_credit=1..}}] if score @s mb_xp_due <= #xp_clock mb run function mysterybox:economy/refund
    ''')
    # Wildcard score operations include offline holders. Clamp expired deadlines
    # at zero so years of absence cannot wrap one into a future signed-int date.
    function('economy/rebase_clock', f'''
        scoreboard players remove #xp_clock mb {CLOCK_SPAN}
        scoreboard players operation * mb_xp_due -= #xp_span mb
        scoreboard players operation * mb_xp_due > #xp_zero mb
    ''')
    function('economy/check', '''
        execute unless entity @s[type=player] run return 0
        execute unless score #price mb matches 0.. run return run function mysterybox:economy/config_error
        execute store result storage mysterybox:economy price int 1 run scoreboard players get #price mb
        execute store result score #xp_price_valid mb run function mysterybox:economy/validate_price with storage mysterybox:economy
        execute unless score #xp_price_valid mb matches 1 run return run function mysterybox:economy/config_error
        function mysterybox:economy/refund
        execute if score @s mb_xp_pt_credit matches 1.. run return run function mysterybox:economy/pending
        execute if score @s mb_xp_credit matches 1.. run return run function mysterybox:economy/pending
        execute if score #price mb matches 0 run return 1
        function mysterybox:economy/balance
        execute if score #balance mb < #price mb run return run function mysterybox:economy/insufficient
        return 1
    ''')
    # Query current XP only: XpTotal can differ from the spendable level/bar
    # balance. The piecewise native total-to-level formula is exact at 16/17
    # and 31/32. Clamp above the signed scoreboard maximum before arithmetic.
    function('economy/balance', '''
        execute store result score #xp_levels mb run experience query @s levels
        execute store result score #xp_bar mb run experience query @s points
        execute if score #xp_levels mb matches 21864.. run return run scoreboard players set #balance mb 2147483647
        execute if score #xp_levels mb matches ..16 run function mysterybox:economy/balance_low
        execute if score #xp_levels mb matches 17..31 run function mysterybox:economy/balance_mid
        execute if score #xp_levels mb matches 32.. run function mysterybox:economy/balance_high
        scoreboard players set #xp_headroom mb 2147483647
        scoreboard players operation #xp_headroom mb -= #balance mb
        execute if score #xp_bar mb >= #xp_headroom mb run return run scoreboard players set #balance mb 2147483647
        scoreboard players operation #balance mb += #xp_bar mb
    ''')
    function('economy/balance_low', '''
        scoreboard players operation #xp_factor mb = #xp_levels mb
        scoreboard players add #xp_factor mb 6
        scoreboard players operation #balance mb = #xp_levels mb
        scoreboard players operation #balance mb *= #xp_factor mb
    ''')
    function('economy/balance_mid', '''
        scoreboard players operation #xp_factor mb = #xp_levels mb
        scoreboard players operation #xp_factor mb *= #xp_five mb
        scoreboard players remove #xp_factor mb 81
        scoreboard players operation #balance mb = #xp_levels mb
        scoreboard players operation #balance mb *= #xp_factor mb
        scoreboard players operation #balance mb /= #xp_two mb
        scoreboard players add #balance mb 360
    ''')
    # At odd levels the second factor is even; divide it before multiplying
    # to avoid an intermediate 32-bit overflow near the 2.1-billion-point cap.
    function('economy/balance_high', '''
        scoreboard players operation #xp_factor mb = #xp_levels mb
        scoreboard players operation #xp_factor mb *= #xp_nine mb
        scoreboard players remove #xp_factor mb 325
        scoreboard players operation #balance mb = #xp_levels mb
        scoreboard players operation #balance mb /= #xp_two mb
        scoreboard players operation #balance mb *= #xp_factor mb
        scoreboard players operation #xp_odd mb = #xp_levels mb
        scoreboard players operation #xp_odd mb %= #xp_two mb
        execute if score #xp_odd mb matches 1 run scoreboard players operation #xp_factor mb /= #xp_two mb
        execute if score #xp_odd mb matches 1 run scoreboard players operation #balance mb += #xp_factor mb
        scoreboard players add #balance mb 2220
    ''')
    # Match a generated integer, not an untrusted macro argument: data get alone
    # would silently truncate a float or treat a string's length as the price.
    function('economy/validate_price', '''
        $execute if data storage mysterybox:config {price_points:$(price)} run return 1
        return 0
    ''')
    function('economy/config_error', '''
        tellraw @s {text:"Mystery box price_points must be a nonnegative integer. No XP points were taken. An operator can repair it with /data modify storage mysterybox:config price_points set value 10.",color:"red"}
        return 0
    ''')
    function('economy/insufficient', '''
        tellraw @s [{text:"You need ",color:"red"},{score:{name:"#price",objective:"mb"}},{text:" XP points to open the mystery box. No points were taken."}]
        return 0
    ''')
    function('economy/pending', '''
        tellraw @s {text:"Your previous teddy refund is still pending. Try again after its reveal; no XP points were taken.",color:"gold"}
        return 0
    ''')
    function('economy/charge', '''
        execute store result storage mysterybox:economy points int -1 run scoreboard players get #price mb
        return run function mysterybox:economy/add_points with storage mysterybox:economy
    ''')
    function('economy/add_points', '$return run experience add @s $(points) points')
    # Purchase advances the open timer to 1 in the same tick: the remaining wait
    # until reveal is reveal_tick - 1. A queued amount is never reread from config
    # or overwritten; check() blocks a new payment while that buyer has a debt.
    function('economy/queue_teddy', f'''
        execute unless entity @s[type=player] run return 0
        execute unless score #price mb matches 1.. run return 0
        execute if score @s mb_xp_pt_credit matches 1.. run return 0
        execute if score @s mb_xp_credit matches 1.. run return 0
        scoreboard players operation @s mb_xp_pt_credit = #price mb
        scoreboard players operation @s mb_xp_due = #xp_clock mb
        scoreboard players add @s mb_xp_due {reveal_tick - 1}
        return 1
    ''')
    # mb_xp_credit predates point prices and holds LEVEL debts in existing
    # worlds. Keep that objective until its last offline buyer receives a refund.
    function('economy/refund', '''
        execute unless entity @s[type=player] run return 0
        execute unless score @s mb_xp_due <= #xp_clock mb run return 0
        execute if score @s mb_xp_pt_credit matches 1.. run return run function mysterybox:economy/refund_points
        execute if score @s mb_xp_credit matches 1.. run return run function mysterybox:economy/refund_legacy_levels
        return 0
    ''')
    function('economy/refund_points', '''
        execute store result storage mysterybox:economy points int 1 run scoreboard players get @s mb_xp_pt_credit
        execute store result score #xp_refunded mb run function mysterybox:economy/add_points with storage mysterybox:economy
        execute unless score #xp_refunded mb matches 1 run return 0
        tellraw @s [{text:"Teddy! Refunded ",color:"gold"},{score:{name:"@s",objective:"mb_xp_pt_credit"},color:"yellow"},{text:" XP points."}]
        scoreboard players reset @s mb_xp_pt_credit
        execute unless score @s mb_xp_credit matches 1.. run scoreboard players reset @s mb_xp_due
        return 1
    ''')
    function('economy/refund_legacy_levels', '''
        execute store result storage mysterybox:economy levels int 1 run scoreboard players get @s mb_xp_credit
        execute store result score #xp_refunded mb run function mysterybox:economy/add_levels with storage mysterybox:economy
        execute unless score #xp_refunded mb matches 1 run return 0
        tellraw @s [{text:"Teddy! Refunded ",color:"gold"},{score:{name:"@s",objective:"mb_xp_credit"},color:"yellow"},{text:" XP levels from your earlier purchase."}]
        scoreboard players reset @s mb_xp_credit
        execute unless score @s mb_xp_pt_credit matches 1.. run scoreboard players reset @s mb_xp_due
        return 1
    ''')
    function('economy/add_levels', '$return run experience add @s $(levels) levels')
