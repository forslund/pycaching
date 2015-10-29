#!/usr/bin/env python3

import unittest
import unittest.mock as mock
from datetime import date
from pycaching.errors import ValueError
from pycaching.enums import Type, Size, LogType
from pycaching import Cache
from pycaching import Geocaching
from pycaching import Point
from pycaching import Trackable
from pycaching import Log

from test.test_geocaching import _username, _password


class TestProperties(unittest.TestCase):

    def setUp(self):
        self.gc = Geocaching()
        self.c = Cache(self.gc, "GC12345", name="Testing", type=Type.traditional, location=Point(), state=True,
                       found=False, size=Size.micro, difficulty=1.5, terrain=5, author="human", hidden=date(2000, 1, 1),
                       attributes={"onehour": True, "kids": False, "available": True}, summary="text",
                       description="long text", hint="rot13", favorites=0, pm_only=False,
                       log_page_url="/seek/log.aspx?ID=1234567&lcn=1")

    def test___str__(self):
        self.assertEqual(str(self.c), "GC12345")

    def test___eq__(self):
        self.assertEqual(self.c, Cache(self.gc, "GC12345"))

    def test_geocaching(self):
        with self.assertRaises(ValueError):
            Cache(None, "GC12345")

    def test_wp(self):
        self.assertEqual(self.c.wp, "GC12345")

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.wp = "xxx"

    def test_name(self):
        self.assertEqual(self.c.name, "Testing")

    def test_type(self):
        self.assertEqual(self.c.type, Type.traditional)

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.type = "xxx"

    def test_location(self):
        self.assertEqual(self.c.location, Point())

        with self.subTest("automatic str conversion"):
            self.c.location = "S 36 51.918 E 174 46.725"
            self.assertEqual(self.c.location, Point.from_string("S 36 51.918 E 174 46.725"))

        with self.subTest("filter invalid string"):
            with self.assertRaises(ValueError):
                self.c.location = "somewhere"

        with self.subTest("filter invalid types"):
            with self.assertRaises(ValueError):
                self.c.location = None

    def test_state(self):
        self.assertEqual(self.c.state, True)

    def test_found(self):
        self.assertEqual(self.c.found, False)

    def test_size(self):
        self.assertEqual(self.c.size, Size.micro)

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.size = "xxx"

    def test_difficulty(self):
        self.assertEqual(self.c.difficulty, 1.5)

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.difficulty = 10

    def test_terrain(self):
        self.assertEqual(self.c.terrain, 5)

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.terrain = -1

    def test_author(self):
        self.assertEqual(self.c.author, "human")

    def test_hidden(self):
        self.assertEqual(self.c.hidden, date(2000, 1, 1))

        with self.subTest("automatic str conversion"):
            self.c.hidden = "1/30/2000"
            self.assertEqual(self.c.hidden, date(2000, 1, 30))

        with self.subTest("filter invalid string"):
            with self.assertRaises(ValueError):
                self.c.hidden = "now"

        with self.subTest("filter invalid types"):
            with self.assertRaises(ValueError):
                self.c.hidden = None

    def test_attributes(self):
        self.assertEqual(self.c.attributes, {"onehour": True, "kids": False, "available": True})

        with self.subTest("filter unknown"):
            self.c.attributes = {attr: True for attr in ["onehour", "xxx"]}
            self.assertEqual(self.c.attributes, {"onehour": True})

        with self.subTest("filter invalid"):
            with self.assertRaises(ValueError):
                self.c.attributes = None

    def test_summary(self):
        self.assertEqual(self.c.summary, "text")

    def test_description(self):
        self.assertEqual(self.c.description, "long text")

    def test_hint(self):
        self.assertEqual(self.c.hint, "rot13")

    def test_favorites(self):
        self.assertEqual(self.c.favorites, 0)

    def test_pm_only(self):
        self.assertEqual(self.c.pm_only, False)

    def test_log_page_url(self):
        self.assertEqual(self.c.log_page_url, "/seek/log.aspx?ID=1234567&lcn=1")


class TestMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gc = Geocaching()
        cls.gc.login(_username, _password)
        cls.c = Cache(cls.gc, "GC1PAR2")
        cls.c.load()

    def test_load_logbook(self):
        log_authors = list(map(lambda log: log.author, self.c.load_logbook(limit=200)))  # limit over 100 tests pagging
        for expected_author in ["Dudny-1995", "Sopdet Reviewer", "donovanstangiano83"]:
            self.assertIn(expected_author, log_authors)

    @mock.patch.object(Cache, '_load_log_page')
    @mock.patch.object(Geocaching, '_request')
    def test_post_log(self, mock_request, mock_load_log_page):
        mock_load_log_page.return_value = (
                {"temporarily disable listing": "22",
                 "archive": "5",
                 "write note": "4",
                 "didn't find it": "3",
                 "- select type of log -": "-1",
                 "update coordinates": "4",
                 "needs maintenance": "45",
                 "owner maintenance": "46"},
                {})
        with self.subTest("invalid log type"):
            l = Log(text="Test log.", visited=date.today(), type = LogType.found_it)
            with self.assertRaises(ValueError):
                self.c.post_log(l)

        with self.subTest("valid log type"):
            l = Log(text="Test log.", visited=date.today(), type = LogType.didnt_find_it)
            self.assertFalse(self.gc._request.called)
            self.c.post_log(l)
            self.assertTrue(self.gc._request.called)

        with self.subTest("empty log text"):
            l = Log(text="", visited=date.today(), type = LogType.note)
            with self.assertRaises(ValueError):
                self.c.post_log(l)
