# Aster V14 — two-way overworld test acceptance

This document is **not** evidence of a successful ROM build or emulator test.
All code is on the isolated `experiment/aster-v14-native-map-staging` branch.

## What the reversible test actually connects

The native Aster icon (`SPRITE_WORLD_MAP_ASTER`, registered sprite 505)
is temporarily placed at **world X=5696, Z=1504**.

The runtime test **repurposes normal-world actor slot 39 (actor ID 47)**,
the first of three unused origin signposts. It does not insert an actor,
renumber existing actors, or change any existing Vale/Vault sprite.
It temporarily adds test exit kind **115** and a proximity contact
trigger to Aster's **default south entrance**.

Leaving Aster from its south gate takes Isaac to unused world entrance
**98 at X=5696, Z=1536**, 32 pixels south of the icon. The offset is
essential to avoid instantly re-entering on arrival. The source is
patched only during a **local optional smoke build** and is restored
even if compilation fails.

The existing normal story branch does **not** have Aster's icon or
two-way contact active. The site is PROPOSED, not verified.

## Free local steps

In a **separate experimental checkout**, after installing dependencies
per `docs/aster-v14-windows-local-build.md`:

```bash
bash tools/aster_v14_local_smoke.sh --check-only
bash tools/aster_v14_local_smoke.sh --map-only
bash tools/aster_v14_local_smoke.sh --probe-world
```

Use a dedicated temporary `.sav`, **never** an Ashfall story save.
The script uses local `make`, not GitHub Actions or Codespaces.

## In-emulator pass/fail tests

1. **Initial appearance:** Start in a field outside the town, trigger
   the debug `B+L+R+Start` shortcut, and confirm Isaac enters Aster
   without a black screen or broken tiles.
2. **South-gate return:** Walk to the southern exit. Confirm he emerges
   on the world map **south of Aster's icon**; he must NOT immediately
   bounce back into the village.
3. **Vault route:** Walk from this world position toward Vault. Confirm
   continuous traversable ground with no rock/cliff/water softlock.
   Turn around and approach Aster again from outside.
4. **Icon entry:** Aster's dedicated dark-roof icon must render and
   entering its touch radius must transition into Aster at the same
   south entrance, without routing to Vault or another scene.
5. **Repeatability:** Leave again, walk away, re-enter again. Try a
   separate experimental save/load and check that party, Djinn,
   menus and world camera still work.
6. **Early progression:** Test with an early-playthrough experimental
   save near Vale/Vault. Make sure Aster does **not** bypass Flint,
   Hammet's caravan departure, the Vault inn/thieves or the broken
   bridge blocking the Kalay route.
7. **Later progression:** Check approach after Hammet's caravan
   sequence and again on a later playthrough state. The temporary
   actor uses `CONDITION_ALWAYS` deliberately to expose collisions
   in QA; final progression gating has NOT been approved.
8. **Custom story assets:** Inspect woodland, waterbanks and roof
   priority, then talk to all seven NPCs. The 27-char dialogue width
   rule and existing Ashfall events remain separate release tests.

## Stop conditions

Do **not** merge or enable the contact permanently if the site lands on
impassable ground, Isaac clips through rock/water, the screen blacks out,
an unrelated actor/event triggers, an entrance loop occurs, any save
becomes corrupt, or the icon cannot be approached from the Vault path.

If a site is blocked, choose a different **verified walkable** location
and rerun both icon-spacing and real emulator QA. Do not treat an
icon-spacing calculation as proof of walkable overworld terrain.

## Release blockers beyond this two-way smoke test

The map still needs final riverbank/cliff/bridge art and validation,
Sanctum and additional house interiors, correct permanent world
contact/arrival and progression gate, and a full start-to-end
emulator playthrough. A source-level test alone cannot certify these.

## Cost / branch safeguards

This is a source-only, opt-in local experiment. It **never** starts
GitHub Actions or Codespaces; it changes tracked sources in a disposable
checkout only and restores them on completion. GitHub account-level
charges and ChatGPT invoices are only verifiable in private billing
settings, not from this repository.
