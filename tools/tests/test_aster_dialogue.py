"""Static validation for Aster's text and trigger wiring.

Checks all six editions and the project's 27-character displayed-line limit.
Run: python3 -m unittest tools.tests.test_aster_dialogue
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LANGUAGES = ("en", "de", "es", "fr", "it", "ja")
NAMES = (
    "MsgAsterInnkeeperWelcome",
    "MsgAsterInnkeeperMindRead",
    "MsgAsterElderWelcome",
    "MsgAsterElderMindRead",
)

class TestAsterDialogue(unittest.TestCase):
    def test_six_catalogs_have_all_messages_with_valid_widths(self):
        for lang in LANGUAGES:
            with self.subTest(language=lang):
                po = (ROOT / "games/tbs/text" / (lang + ".po")).read_text(
                    encoding="utf-8"
                )
                for name in NAMES:
                    with self.subTest(message=name):
                        marker = 'msgctxt "' + name + '"\\n'
                        self.assertEqual(po.count(marker), 1)
                        section = po.split(marker, 1)[1].split("\\n\\n", 1)[0]
                        rows = section.splitlines()
                        self.assertTrue(rows[0].startswith('msgid "'))
                        self.assertEqual(rows[1], 'msgstr ""')
                        text = "".join(json.loads(row) for row in rows[2:])
                        self.assertTrue(text.endswith("{end_wait}"))
                        text = text.replace("{page_break}", "\\n")
                        text = text.replace("{end_wait}", "")
                        for line in text.split("\\n"):
                            self.assertLessEqual(
                                len(line), 27, f"{lang}/{name}: {line!r}"
                            )
                self.assertIn('msgctxt "MsgAsterInnkeeperWelcome"', po)

    def test_scene_uses_messages_for_talk_and_mind_read(self):
        scene = (ROOT / "games/tbs/src/scene/aster.c").read_text(
            encoding="utf-8"
        )
        for name in NAMES:
            with self.subTest(name=name):
                self.assertEqual(scene.count("MSGNO(" + name + ")"), 1)
        self.assertEqual(scene.count("TRIGGER_TALK,"), 2)
        self.assertEqual(scene.count("PSYNERGY_ON_ACTOR(ABILITY_MIND_READ)"), 2)

if __name__ == "__main__":
    unittest.main()
