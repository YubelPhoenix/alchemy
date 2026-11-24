# Ashfall narrative cohesion pass — 2026-11-24

Author-approved narrative revision based on the integrated main branch.

## Writer-only decisions (spoilers)

- ??? seeks a repeatable, stable passage to a world she lost. She studies this world's Isaac because his Psynergy can stabilize a breach when it interacts with hers. Heart senses weak points. Identity and the ultimate reason for returning remain unrevealed. Her references to Grave Eclipse and thirty years are not a prediction the party can verify.
- Ash Jenna is an unrepentant antagonist. She destroys the wounded Suhalla guards' remaining medicine after the canonical attackers leave. The mandatory guard report establishes the deed even if the optional duel is skipped; she owns the deed at the gate and in her optional Lalivero coda. Do not attribute the original attack to her or make her a member of a formal alliance.
- Sarah's missing relative is Sheba, preserving the connection players enjoy. The precise family relationship and Sheba's origins remain unrevealed. Sarah withholds the girl's name from strangers, then recognizes it in Lalivero. Her final match marks the end of her rumor-driven journey; she will seek the people who raised Sheba. Do not imply she has already found her or knows whether she survived.
- The Rift's ritual mark suggests a previously attempted crossing; ??? explicitly identifies Ash Jenna as another traveler. Kegare remains independent. No party member knows the destination of ??? or Heart.
- After Colosso, Ivan proposes investigating the crossings and Garet suggests asking Vale's elders if they return. At the optional monolith, the party explicitly chooses to investigate before entering. No mandatory backtrack is introduced. The one-time approach uses spare flag 0x8fa.

## Validation still required

Build and emulator replay, including the Suhalla guard report with and without the optional fight, the post-Venus coda, all Sarah encounters including skipped fights, the Vale duel with optional encounters skipped, both Rift pre/post battle scenes and anchor seal, and actual backdrop/encounter difficulty. The text pass does not change enemy stats, event flags, maps, actor positions, or battle mechanics. Review remaining religious terminology and other scene closings across the full game separately.

## Second narrative pass

The Rift can be entered before or after the Vale duel. The throne dialogue now checks the Vale victory flag before referring to the prior encounter or warning, and recognizes Heart by name only if she has been established by a previous completed encounter. Vale's questions work without having fought Heart. ??? is interested in isolating Isaac's power in Vale, while the Rift tests the interaction of his power with hers. The party does not claim to know Dark Dawn events or where the silhouettes are going. The Suhalla guard report makes the loss of medicine matter and Iodem promises to send help. This remains dialogue, not a new inventory or healing mechanic. Scene-level proof and ROM tests remain outstanding.

## Ash Jenna's introduction

The mandatory post-Manticore Lamakan scene, not the optional first sighting, now establishes her name, her claim to be another world's Jenna, her loss, her accusation against the Wise One and her reason for approaching Isaac. The party reacts with disbelief and skepticism. Her claim about the Wise One remains her testimony, not objective cosmology. Both existing opening branches converge before the introduction. No additional trigger, choice, map, or flag is required. The precise details of the destroyed world and how she crossed remain undisclosed.

## Third pass — continuity and build review

The five-turn first Ash Jenna sighting leaves her identity undisclosed but names Isaac. The mandatory introduction supplies her identity and accusation; Tolbi now follows that accusation into the theme of trust. Lalivero refers back to Suhalla without making cruelty a redemption beat. Sarah stays related to Sheba and spars to prepare for an uncertain search at sea. The anchor sustains the breach rather than preventing its spread; sealing it closes the passage, not the rooms. Mia explicitly distinguishes the other world's Alex from her own. The unused N696 was removed, and questions about the silhouettes are only asked when at least one echo event occurred. Source-level backdrop routing in scene_rules.s already maps the Throne Hall to UmbralThroneBackdrop; regular Rift encounters use their separate background. Level 28 encounter pool unchanged pending gameplay verification. Build and emulator validation remain required.
