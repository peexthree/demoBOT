import unittest
import bot.ai_utils as ai_utils

class TestAiUtils(unittest.TestCase):
    def test_models_exist(self):
        self.assertTrue(len(ai_utils.GEMINI_MODELS) > 0)
        self.assertIn("gemini-2.5-flash", ai_utils.GEMINI_MODELS)
        self.assertIn("gemini-2.5-pro", ai_utils.GEMINI_MODELS)

if __name__ == '__main__':
    unittest.main()
