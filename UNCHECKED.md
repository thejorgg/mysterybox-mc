# Deferred verification

## UC-20260927-01 — Audible opening melody and musical fidelity

- **Recorded:** 2026-09-27
- **Status:** NOT RUN — final listening judgment for the revised 23+6-note arrangement and overlapping dragon/echo laugh remains with the user. Native playback dispatch was exercised successfully.
- **Request:** Leave the recording-derived melody wired, with manually editable notes and volumes.
- **Affected paths:** `source/opening_melody.csv`, `source/finished_melody.csv`, `source/teddy_audio.json`, `tools/melody.py`, `tools/build_teddy_audio.py`, `tools/build_datapack.py`, and generated `mysterybox:sound/*` functions.
- **Surface:** Minecraft Java 26.3, Modrinth `Mystery Box Model Check`, world `Mystery Box Asset Preview`, normal desktop. OpenAL now initializes successfully; the earlier Waymux audio failure is historical.
- **Safety:** Use the disposable world and installed resource pack. Previews cost no XP; teddy outcomes broadcast to every online player, including other dimensions. Warn other players before previewing. Do not change unrelated system audio or worlds.

### Steps and expected outputs

1. Enable Minecraft Master and Blocks volume; run `/function mysterybox:sound/preview` in the Overworld. Expect about 3.85 seconds of opening music, then the separate two-second weapon ending, without charging XP or opening the box.
2. Compare `melody_volume` and `finished_volume` at 100, 50, and 0. Each must affect only its own phase, not pitch/timing.
3. Run `/function mysterybox:sound/preview_teddy`. At reveal, expect the full dragon growl, then a higher-pitched witch laugh **2.25 seconds later** with voices offset 0/33/66 ms. The louder laugh overlaps the final 0.75 seconds of the growl and continues briefly afterward; no weapon ending. Compare `dragon_volume` and `teddy_volume` independently. Compare the score against `jLhPToHJ7gM`; judge musical resemblance rather than full piano timbre/polyphony.
4. Edit one CSV row's `volume_percent`, rebuild, replace the installed datapack ZIP, and `/reload`. Expect only that note's authored volume to change. Follow README instructions for note names, timing, and cents.
5. Restore the preferred master volume and score; do not overwrite another listener's edits.

### Existing evidence and limits

- CSV conversion/range checks passed, including F#3/F#4/F#5 pitch mapping and invalid-note/volume rejection.
- The game executed the preview through completion. Native storage showed volume `0.3` for a 60% note at a 50% master setting.
- Real box interaction, animation, reward, and teddy relocation were exercised separately.
- No audible playback or subjective transcription fidelity is claimed. The source recording is not redistributed.

### Checking-agent plan requirement

Before a future agent executes this check, append a short plan here covering scope, current evidence, permissions/runtime ownership, ordered actions, acceptance evidence, and restoration. This entry alone does not authorize application control or system-audio changes.

### Verification history

- 2026-09-27: listening deferred to the user. Playback dispatch and numeric volume scaling passed; audible output remains unchecked.

### Revised-reference verification plan — 2026-09-27

- Scope: new `jLhPToHJ7gM` score, shorter roll, weapon-only finished phrase, distinct teddy sound, and independent volume controls. Do not alter payment/enchanting rules.
- Evidence: user reports the old score only partly resembles the tune and includes unwanted notes. The normal desktop client now initializes OpenAL successfully; no Waymux use.
- Safety: use only the existing `Mystery Box Model Check` instance and its disposable preview world; direct desktop control is authorized. Preserve custom configuration and do not access unrelated windows/audio.
- Execute: rebuild/install the score and generator together; run both free previews and exercise weapon/teddy timeline boundaries in the native game.
- Acceptance: roll ends at the musical boundary; finished notes run only for weapons; teddy uses the verified vanilla witch celebration event; no extra old hold; independent volume arithmetic/muting works.
- Evidence: native game logs/state and targeted game-window captures establish command execution and transitions. User listening remains the final authority on musical fidelity; do not claim a note-perfect sound match.
- Restoration: restore temporary configuration, remove only temporary test probes, and leave the revised packs installed for the user's comparison.

### Revised implementation evidence — 2026-09-27

- Scope grew by explicit user request to XP payment, 10% refunded teddy, armor/elytra, any-height relocation, physical base protection, and global overlapping outcome audio. Earlier plan exclusions no longer describe the authorized scope.
- The normal desktop client loaded the revised pack and initialized OpenAL. Both free previews and actual weapon/teddy outcomes were executed; a native click showed the teddy, 20-level refund, and relocation from Y100 to Y−27. User accepted collision blocking.
- The global dragon helper was invoked in the Overworld and native debug output reported playback to the test player in the Nether. The custom laugh uses the same global helper and was also dispatched.
- The 1.059-second laugh OGG was decoded/probed: mono48kHz. The builder authors 1.5× pitch and sample delays0/1584/3168, with descending gains. These facts do not establish subjective echo balance.
- After the user reported an inaudible laugh, the valid OGG was found to be about 15–19 dB quieter than the dragon. The updated asset uses 3× output gain (measured mean −18.2 dBFS, peak −2.5 dBFS) and an independent 45-tick schedule instead of a 5-tick animation-timer trigger.
- Game-only PipeWire capture after the fix contained both actual waveforms: dragon correlation 0.956 and custom laugh 0.871. This establishes audible signal delivery, not a listener's preference for the mix or musical fidelity.
- User listening remains the outstanding acceptance criterion; no note-perfect or perceptual match claimed.

## UC-20260927-02 — Multi-client pending XP refund isolation

- **Recorded:** 2026-09-27
- **Status:** NOT RUN — only one authenticated client was exercised; a second independently authorized player is needed for simultaneous-player/logout acceptance.
- **Request / scope:** 20-level teddy refunds belong to the buyer and must not duplicate or credit another buyer, including across logout/reload.
- **Affected paths:** `tools/economy.py`, generated `mysterybox:economy/*`, per-player `mb_xp_credit` and `mb_xp_due`, persistent `#xp_clock mb`.
- **Preconditions / safety:** Two consenting test players, operator access, a disposable server/world, and one test owner. Do not use real progression or obtain unrelated credentials.

### Steps and expected outputs

1. Save both players' XP/configuration. Force a teddy, let A pay20, and disconnect A before reveal. Keep B online so server time advances.
2. Reload while A is absent; optionally change price and let B complete a different opening. B must never receive A's refund.
3. Reconnect A after the deadline. A receives exactly the original20 levels once, with fractional bar progress preserved. Reconnect/reload again: no second refund.
4. Exercise a pending deadline across clock rebasing and a due refund while the box is administratively disabled. Credits must remain buyer-owned and payable.
5. Restore the saved test configuration/XP and remove only test-owned artifacts.

### Existing evidence and limits

- Single-client native regression checks passed exact delayed refund, changed-price capture, fractional XP preservation, and duplicate-refund rejection.
- Per-player persistent scoreboard ownership is implemented, but real simultaneous clients, an offline buyer returning, and clock-rebase acceptance have not been exercised.

### Checking-agent plan requirement

Before execution, append a short plan covering scope, current evidence, prerequisites and consent, ordered actions, acceptance evidence, and restoration. This ledger grants no additional access.

### Point-price update — 2026-09-27

- New purchases cost **95 XP points**, recorded in `mb_xp_pt_credit`; `mb_xp_credit` holds only outstanding pre-upgrade **level** debts. Both use the persistent buyer-owned `mb_xp_due` deadline.
- For the current multi-client case, A pays 95 points and must receive exactly 95 points once after reconnecting. The earlier fractional-bar-preservation expectation applies only to legacy level debts, not new point purchases.
- The isolated 26.3 single-client economy check reported **0 errors**, covering point debits/refunds, changed-price capture, duplicate rejection, formula boundaries, high balances, and legacy level debts. Actual Survival right-clicks spent 190 → 95 → 0 points.
- Real simultaneous-player/logout delivery remains **NOT RUN**. The existing consent, disposable-server prerequisites, and checking-agent plan requirement still apply. No public dedicated-server resource-pack download/prompt was exercised; README instructions are source-checked setup guidance.

## UC-20260927-03 — Dithered segmented beam over water and at distance

- **Recorded:** 2026-09-27
- **Status:** NOT RUN — user requested to perform the reload and visual verification themselves; no game interaction authorized for this change.
- **Scope / surface:** `tools/build_assets.py`, `tools/build_datapack.py`, generated beam texture/model and `box/beam_*` functions; Minecraft 26.3 in the `Mystery Box Model Check` instance.
- **Prerequisites:** Updated datapack and resource ZIPs; `/reload` and F3+T, or a restart. The user owns the running game. Any later agent check requires separate authorization and a disposable world for relocation/removal checks.

### Steps and expected outputs

1. Reload both packs beside the existing box. The old two stretched beams should be replaced by twelve independently positioned 16-block sprites, with no box relocation, XP charge, or terrain edits. Repeating reload must not duplicate sections.
2. Look through the beam toward water from above and below the surface and at several angles. Water must not disappear as a large rectangular sheet; the beam should look pixel-dithered rather than softly translucent.
3. Move above/below the box and turn toward visible sections while the box itself is off-screen. Sections should have their own positions and render bounds. Ordinary terrain occlusion, chunk loading, fog, and server entity-tracking limits still apply.
4. In a disposable world only, relocate/remove the box. All old sections should disappear; a moved box should have twelve sections at its new position, not twelve overlapping at its base.

### Existing evidence and limits

- The user's screenshot establishes the old water artifact. No reproduction or visual confirmation was attempted.
- Automated build/artifact smoke passed: beam alpha contains only 0/255; the vertical pattern repeats without a texture fade seam; the model is a flat double-sided sprite; twelve section origins form two gap-free 96-block runs with 12×16 culling bounds. Both pack ZIPs passed integrity checks. These are artifact checks, not native rendering or command-execution evidence.
- Automated artifact checks do not establish water compositing, native tracking, or migration behavior in a running client.

### Checking-agent plan requirement

Before a later authorized agent run, append a short plan covering scope, evidence, runtime ownership, disposable-world safety, actions, acceptance evidence, and restoration. This record grants no game-control permission.

### Narrower-beam and loot update — 2026-09-27

- User rejected the initial coarse 12-block-wide dithering. The revised beam is 3 blocks wide, uses a 64×384 binary-alpha texture, and reduces both dot size and spacing to one quarter while retaining twelve 16-block sections. Marker version 2 replaces earlier wide sections on the next tick after reload.
- Artifact checks confirm binary alpha, dimensions and unchanged 96-block runs. Visual acceptance of the narrower beam and its water/distance behavior remains **NOT RUN**; reload both packs before applying the steps above.
- Headless Minecraft reward checks reported zero errors for 246 loot outcomes, 37 reward-behavior cases and 160 enchantment samples. These establish serialized components, entity types and command behavior, not client appearance or player-death semantics.

### Final sprite beam, click area and category weights — 2026-09-27

- Supersedes the dotted and spinning rectangular designs above. The beam is a 0.75-wide, double-sided camera-facing sprite: opaque shaft, transparent two-block transition at the box. Six 16-block shaft sections remain in each direction, plus one base sprite. The downward shaft starts three blocks below the box and extends to −99. Spin and proximity fading are removed.
- The Blender preview was inspected. Native saved entity data confirms all 13 sprites, widths, billboarding and positions. These checks do **not** establish client rendering over water or at tracking boundaries. Reload both packs and inspect those surfaces in place; no game-control permission is granted by this record.
- The upper click guards are replaced by three narrow two-block-tall responsive hitboxes. Native data confirms their dimensions and response flags; actual mouse activation across the six front cells remains the user's check.
- Native checks completed 3,500 weighted draws (500 per mode), 47 reward cases and 160 enchantment samples. Reward/enchantment errors were zero; every weighted draw produced an allowed category. Artifact checks prove exact normalized 50:20:15:10:5 category weights.
- Native defaults/migration checks confirmed 10-point new prices, migration of 95→10, and preservation of a custom 37-point price. Earlier checks confirmed separate default-off curse flags, independent 2% eligibility boundaries, and persistence of later customizations.
