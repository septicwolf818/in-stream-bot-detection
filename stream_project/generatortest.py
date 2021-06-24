import unittest
from .generator import Events, BotEvents, UserEvents, main

class GeneratorTest(unittest.TestCase):
    def test_user_less_than_twenty_events(self):
        for _ in range(100):
            events_str = UserEvents("127.0.0.1").generate_events()
            self.assertLessEqual(len(events_str),20)

    def test_bot_more_than_twenty_events(self):
        for _ in range(100):
            events_str = BotEvents("127.8.0.1").generate_events()
            self.assertGreaterEqual(len(events_str),21)


    def startTest(self):
        unittest.main()
