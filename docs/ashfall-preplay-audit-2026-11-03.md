# Golden Sun: Ashfall — Pre-playthrough release audit

**Branch:** `dark-story-rewrite`  
**Audit date:** 3 November 2026  
**Audience:** Creator preparing to begin an end-to-end playthrough  
**Status:** **STATIC SOURCE/DIALOGUE AUDIT COMPLETE; GAMEPLAY ACCEPTANCE NOT COMPLETE**. Do not describe this as a fully tested 10/10 game.

This report is the current pre-play authority alongside `tools/dark_story/CONTINUITY_LEDGER.md` and `docs/ashfall-final-story-acceptance-matrix.md`. Historical reset documents are not a source for the discarded Bloom, awakened/sleeper faction, phantom Ivan voices, custom caravan choice, or harbor-child plots.

## Scope and evidence

- The active dialogue replacement inventory contains **77 TSV files and 4,235 ID/context/text entries**. All four batches were inspected for direct references to discarded plot threads. No surviving *active custom* Bloom/sleeper/harbor-child/ghost storyline appeared in that text search. Matches needing interpretation were (a) Hammet's **original** caravan in Vault, (b) Feizhi's established Psynergy development, (c) Feizhi physically calling to Hsu near the landslide, and (d) a character waking in Babi Palace. Those are not evidence the abandoned custom cosmology was restored.
- The dialogue build passes the canonical ID/context inventory, text-box widths, line/page limits, placeholders, endings, style controls, duplicate IDs and source message-reference checks in `tools/dark_story_rewrite.py`. **This is syntactic data validation, not a full interpretation of every line in its original scene.**
- Against `main`, the branch changes approximately **202 files**, including **19 game-scene C files** and core overworld/menu-related files. Those are a large regression surface. The original route remains the explicit design baseline.
- A complete build on commit `3860ca4178480bc576881807c2ef9fd083e4d852` succeeded, including dialogue validation, automated story contracts, Heart art regeneration, modified ROM compilation, independently compiled baseline, nonempty IPS patch creation, and artifact upload (GitHub Actions run **41678281576**). The memory-cleanup revision resulting from this audit requires its **own** fresh CI result; do not reuse the earlier successful run as proof for it.
- All **28 explicitly defined `FLAG_DARK_*` numeric bit IDs** are unique, including in a check against **1,063 direct numeric `#define` entries in `games/tbs/include/flags.h`**. This does not cover computed macros, temporary flag aliasing or save-state behavior in play.
- `tools/dark_story/check_story_contract.py` cross-checks Ash Jenna field identities, conditional choice callbacks and Tolbi/Lalivero cursor resets, Kegare/Heart loss-retry behavior, persistent flags, 19 custom coda messages and the Garet miner callback. Source-level checks passed in run 41678281576. **They cannot prove encounter accessibility, palette appearance or in-game battle result.**

## Canonical story and chronological verdict

| Order | Location / arc | Static audit result | Required playthrough check |
| --- | --- | --- | --- |
| 01 | Stormy Vale, three-year opening | Distinct storm/daytime event states, originals' loss and the silent watcher distinguished in source audit. No identity invented for the watcher. | Boulder, family, river and plaza sequence; no early-knowledge dialogue; A-button menu on first available world map. |
| 02 | Sol Sanctum and eruption | Actor/flag notes preserve Stars, hostage-taking, mandatory eruption and Vale departure. | Each puzzle, retreat lock, Jenna/Kraden/Felix departure and first map menu opening. |
| 03 | Vault / Bilibin / Kolima / Tret | Original Kolima curse and Mercury-victory flags explicitly independent. Heart is an **optional**, unrelated Kolima antagonist. | Kolima curse before and after Tret cure, Jill at the river before/after Mercury, Heart loss/retry/win, all NPC/Mind Read responses. |
| 04 | Imil / Mercury Lighthouse | The new Isaac–Mia confrontation, Saturos battle, solo Mia–Menardi sequence and subsequent party reassembly are explicitly routed in `mercury_lighthouse_aerie.c` and `world_map.c`. | **High risk:** every duel result and retry, hostages' appearance, solo Mia, return to four members, Saturos flag, save/reload, world map A-menu before and after. |
| 05 | Fuchin / Mogall / Xian | Original road order, Ki/Force, Feizhi's established Psynergy and Hsu search retained. `I can't hear Hsu` is a physical shout/search near the boulders, not fabricated telepathy or Ivan's phantom voices. | Fuchin path, Feh's demonstration, landslide, optional Mind Read and Hsu rescue timing. |
| 06 | Altin / Altin Peak / Lama Temple | Flood and drain states separated. Optional miner rescue: yes/no, then separately stay yes/no; Garet's conditional callback correct. Psynergy Stone and Reveal lore remains canonical. | Flood levels/shop access, miner refusal/retry/reward only once, N203 callback only after stay, save/reload. |
| 07 | Lamakan Desert | Manticore defeat triggers Mia's one-time emotional aftermath then Ash Jenna's hostile revelation. Isaac accepts or refuses *investigating*, never approves violence. Ash Jenna is evil from the creator's sprite animation. | **High risk:** Manticore defeat/retry, hot-weather rendering, early Ash Jenna glimpse present/absent, both answers and persistent flags. |
| 08 | Kalay / Karagol / Tolbi / Colosso | Original festival progression and sea crossing preserved. Ash Jenna appears **after Colosso and Lamakan**, not earlier. Kegare appears after Colosso as an independent optional fight. Tide Shard kindness content is unrelated. | Tolbi pre/post Colosso, Babi rescue, Ash Jenna accepted/refused dialogue, Kegare before/after Ash Jenna with retry. |
| 09 | Suhalla / Babi Lighthouse / Lalivero / Venus | Iodem, injured soldiers, Sheba's capture, lighthouse and two Adept antagonists follow established event/state progression. | Suhalla checkpoint choices, Venus boss/fall, character presence, return route, no character knowing Felix and Sheba survive prematurely. |
| 10 | Post-Venus Lalivero, Black Orb, ship and ending | Optional **hostile** Ash Jenna encounter only if met in Tolbi; acceptance/refusal callback; no redemption. Original Jenna/Kraden ending, ship and Alex's Felix/Sheba reveal left intact. | **High risk:** Black Orb before/after coda, both coda choices, leave/re-enter, three ship Yes/No replies, completed original ending. |

## Concrete issues and dispositions

### PREPLAY FIX — dormant global tint allocated extra scene memory

The ash-tint feature was **disabled** in `scene_manager.c`, but `PaletteFade_Initialize` still allocated and zero-filled an additional `(COLOR_MAX + 1) * sizeof(u16)` bytes (~898 bytes) in the palette-fade heap on every scene. No current scene schedules `PaletteFade_KeepAshTint`. The audit removes this dormant frame task and restores the game's original `sizeof(*work)` allocation. It also corrects stale documentation claiming grey tint was actively applied everywhere and adds a contract preventing the old allocation returning unnoticed.

**Reasoning:** Removing unused, extra EWRAM reduces pressure on the world-map/menu memory path. **This is not proof that the reported A-button world-map freeze is fixed.** The freeze may have another cause; runtime reproduction is required.

### OPEN, HIGH PRIORITY — pressing A on the world map

The creator previously reported normal movement working but an A-button press freezing the world map, while entering a town sometimes avoided the behavior. This has **not** been reproduced or resolved in an emulator by this audit.

Source diff against `main` shows no direct world-map A-button handler modification in `world_map.c`. Its additions are primarily **special Mia-story entrances, actors and cinematics**. The core menu handler is also not among the game files modified by the branch, though overall memory and actor state can still affect it. There is already a diagnostic world-map Djinni-capture workaround in `games/tbs/src/overworld/event_commands/djinni.c`; the audit does not assume that workaround solved the freeze.

**Required before investing in a long run:** on the latest built patch, open the menu on the first normal world map, close and re-open it; repeat after a normal battle, after a Djinni capture (if applicable), on re-entering the world map from a town, and after the Mercury/Mia transition. Record *exactly when* A stops working. If reproducible, this is a **release-blocking defect** even if every CI check passes.

### OPEN — custom art fidelity

Ash Jenna is currently the original Jenna field sprite with grey/sinister shading, not the exact evil-Jenna frames from the creator's sprite animation. Kegare uses Mia's existing field sprite on a separate actor slot. The art build confirms Heart's indexed sprite sheet and palette, **not** that field/portrait visuals reproduce the creator's art or appear correctly in all scenes. Visual acceptance remains pending.

### OPEN — gameplay availability, branch flow, and difficulty

The source supplies plausible encounter conditions and retries for Heart and Kegare; without gameplay no claim can be made that the player can approach their placed actors without clipping, that an opponent's defeat/retry always returns to the correct place, that a one-time coda survives save/reload, or that the solo battles are reasonably balanced. A passed patch build cannot certify these.

### DELIBERATE STORY DECISION — no additional invented mythology

The original Golden Sun route, the Star/Alchemy conflict and the consequences to civilians remain the spine. The evil Ash Jenna's loss and Wise One accusation are **her perspective**, not a proven or exonerating world fact. She remains unrepentant, distinct from original Jenna, Heart and Kegare. No revived Bloom/sleeper/caravan/harbor-child/phantom-voices plot is approved.

## Mandatory save/checkpoint strategy for the upcoming playthrough

1. **Test A on the earliest normal world map before committing to the run.** Save separately before leaving Vale and again after entering/exiting Vault or another town. If A freezes, note the location, save type, what was done immediately beforehand and whether B/Start/Select still work.
2. **Preserve a save before Mercury Lighthouse's final confrontation**, a second before the solo Mia–Menardi sequence if possible, and a third immediately after the party rejoins. These are the most invasive custom route changes.
3. **Preserve a save before the Manticore**, then use different saves for Ash Jenna **Yes** and **No**. Record whether the early brief sighting happened. Carry those saves into Tolbi/Lalivero rather than overwriting both.
4. **Keep an untouched save before Colosso's conclusion** to test Kegare in either encounter order and a lost battle without corrupting the main run.
5. **Keep a separate post-Venus save** before Iodem gives the Black Orb. Test the Lalivero Ash Jenna talk before/after Iodem, town re-entry, wharf, and the three independent Yes/No ship dialogue choices.
6. **Record a final save for the original Jenna/Kraden island ending.** Check the moment Alex reveals Felix and Sheba rather than treating knowledge of their survival as available to Isaac earlier.

## Acceptance verdict

**Pre-play static audit:** **PASS WITH DOCUMENTED BLOCKERS.** The dialogue IDs, source-backed character contracts, flag IDs, and previous successful ROM/IPS build provide a coherent and testable starting candidate. The audit's dormant-cache cleanup needs its own successful build result before using that candidate.

**Runtime readiness:** **CONDITIONAL / NOT CERTIFIED.** The unresolved world-map A-button freeze and unplayed high-risk story branches prevent a clean 10/10 or production-release sign-off. The next playthrough is a necessary quality gate, not a formality.

**Do not label any unresolved checkbox as tested.** Record save/reload behavior, actor portraits and sprite collisions, controls and story order from the actual game.

### PREPLAY FIX — Mercury beacon falsely lit by visiting the area

The initial pre-play inspection also found a **real chronology defect** in `Scene_Arrive` (`games/tbs/src/overworld/overworld/sequence_manager.c`). A convenience block set `FLAG_MERCURY_LIGHTHOUSE_LIT` whenever `FLAG_AREA_VISITED(0x13)` was true. That flag becomes true merely from entering Mercury Lighthouse; the player does **not** have to reach the beacon. This incorrectly promoted `WorldState_GetStage()` to the post-Mercury state, potentially causing early rain and any other flag-dependent dialogue/conditions to act as if the beacon were lit.

**Correction:** Removed the visited-area shortcut. `Scene_Arrive` already preserves the Mercury lit flag across area changes, and `MercuryLighthouseAerie_Initialize` sets it during the actual lit-beacon aerie sequence. Therefore the flag now reflects the real story event without a new save bit or alternate route. Added `check_mercury_lighthouse_chronology()` to the automated story contracts. **Game test:** enter/leave the lower Mercury Lighthouse *before* lighting the beacon, then complete the beacon and leave; confirm weather/story flags only advance afterward.

**Old-save caveat:** An older test save produced by the buggy area-visited shortcut may already contain the falsely-set Mercury lit flag. The corrected engine does not retroactively clear that saved bit because doing so mid-beacon could corrupt a legitimate sequence. For meaningful narrative QA, **begin the new playthrough from a fresh save**, not one that may have entered Mercury on an older patch.

### Additional scene-source routing audit

All **19 modified scene C files** were checked for named `Import_EventSetExitRequest` destinations against their actual `SCENE_EXIT` tables; no unmatched **named** exits were found. Scripted battle destinations were enumerated across Mercury, Imil, World Map, Kolima, Tolbi, Lamakan, Altin, Sol Sanctum and Mogall. This is a source-symbol cross-reference only: destination `0`, implicit default exits, party state at the destination and true runtime reachability are not proven by this scan.

The same 19 scene sources were searched for active `FLAG_DARK_*` / `MsgDark*` references to the abandoned custom awakened, Bloom, harbor-child, caravan-choice, phantom voice and sleeper plots. No matching active code identifiers were found. Original-game Hammet caravan events are separate and must stay.

**The combined pre-play changes** include engine palette-memory cleanup *and* the Mercury-visited chronology repair. The newest commit after both changes must pass its own dialogue, story-contract, compiler and IPS workflow before its patch is considered the recommended playtest build.


### OPEN, HIGH GAMEPLAY IMPACT — Mercury scripted solo levels and full inventory

In `MercuryLighthouseAerie_SaturosFallsAndMiaRuns`, Isaac's solo-duel preparation uses `MIA_DUEL_ISAAC_LEVEL 14` and the solo Mia vs Menardi transition uses **`MIA_DUEL_MIA_LEVEL 24`** with `Unit_LevelUpTo`. The associated source then reconstructs the party without a corresponding level-restore call. This suggests a **permanent level advantage for Mia** (and potentially Isaac), far above normal Mercury-era progression. The solo Menardi enemy is explicitly level 24, HP 600, ATK 120, and the fight has its own scripted formation; the leveling looks intentional for the boss, but its **downstream game balance has not been established**.

`MercuryLighthouseAerie_ArmMia` attempts to add and equip `ITEM_TIDEGLASS_BLADE`, but returns immediately if Mia's inventory has no free slot. That can deprive Mia of the intended duel weapon. **Playtest:** keep at least one inventory slot free before the Mercury confrontation; record Mia/Isaac levels and equipment beforehand and again after reunion. Test whether Menardi remains reasonably winnable, and whether Mia's level makes Kolima/Altin fights trivial afterward. A balance redesign requires actual combat testing; do not silently nerf the boss or erase player inventory to work around it.

This risk is separate from the game-breaking world-map A-menu freeze. Neither can be signed off by compilation or text audit alone.

