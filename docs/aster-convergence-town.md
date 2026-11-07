# Aster — convergence town (experimental)

Status: DESIGN / IMPLEMENTATION SPEC ONLY. Not yet a playable map. Do not merge until the entry, scene, map, dialogue, and CI checks pass.

## Placement
Candidate: unoccupied accessible land east of Vault, near Goma foothills. Exact world-map coordinates MUST be checked against world geometry, existing actors and contacts, encounter zones, and entrances before writing code. Do not use Suhalla.

## Narrative
Aster is a real town displaced from Ash Jenna's Weyard, not an illusion. Its people disagree on whether Ash Jenna saved them or harmed them. The town's memories periodically collide with those of Isaac's world. Convergence is not automatically Ash Jenna's doing; her role remains a mystery until supported by the established story.

## Prototype layout
Small plaza with well, four exterior buildings (inn, shop, elder's home, closed house), and a northern overlook. Six NPCs initially. Existing tile art only. First milestone: enter town, walk with correct collision, speak to one NPC, exit to original world-map location.

## Dialogue corruption rules
The corruption is deliberate *in-world* and must never resemble a broken text encoding or bad build.
- Most lines are grammatical, human and grounded; no corruption in every exchange.
- Occasional short interruptions overwrite a few words with a conflicting memory or an alternate-world sentence.
- Display glitch as two separate valid text lines or a controlled scene/message swap; do NOT inject invalid control codes, unescaped characters, or unsupported glyphs.
- Keep every displayed dialogue line within the 27-character project limit (verify with actual message parser).
- Mind Read can reveal contradictory memories, but never assert the character knows about other worlds unless earned by the story.
- Do not alter original NPC dialogue outside Aster.

## Sample dialogue (line lengths <= 27)
Innkeeper:
  "Rooms are open tonight."
  "If you're from Vale, then—"
  "No. Vale burned years ago."
  "..."
  "Forgive me. I feel ill."

Well-side child:
  "A woman came here before."
  "She looked like your friend."
  "Her eye was red. I think."
  "No... both eyes were blue."

Elder:
  "The road was east of us."
  "Yesterday it ran north."
  "Don't tell the others yet."

Mind Read, innkeeper:
  "I saw the fire myself."
  "But Vale is still there..."
  "How can both be true?"

## Implementation checkpoints
1. Verify exact empty world-map coordinates and available actor/trigger slots in games/tbs/src/scene/world_map.c.
2. Identify a safe reusable map/scene resource strategy; avoid overwriting active scenes.
3. Implement world-map entrance with gated story flag and reverse exit.
4. Build a small collision-tested town map using existing metatiles.
5. Implement one NPC with deterministic glitch event; test message line width and event state.
6. Build with CI, then emulator test: first entry, re-entry, save/load, encounter return, and late-game progression.
7. Add remaining NPCs, inn/shop and story beats only after prototype passes.

## QA acceptance
- Main dark-story-rewrite branch unchanged until experimental build is verified.
- No existing world-map icon or contact overwritten.
- No softlocks, black screens, displaced party spawns, broken text, or changed vanilla dialogue.
- Glitch effects are authored story moments, not runtime corruption.
