import unittest
import datetime

from src import app, db
from src.models import Page, Matches
from src.utils.utils import get_degree


def CreatePage(url1):
    page = Page(
        url=url1,
        queried=1,
    )
    db.session.add(page)
    db.session.commit()
    return page


def CreateMatch():
    m1 = Matches(
        url1=CreatePage("TESTURL1"),
        url2=CreatePage("TESTURL2"),
        degrees=33,
        last=datetime.datetime.now(),
    )

    m2 = Matches(
        url1=CreatePage("TESTURL3"),
        url2=CreatePage("TESTURL4"),
        degrees=33,
        last=datetime.datetime.now(),
    )

    db.session.add(m1, m2)
    db.session.commit()


#################################################
# Tests                                         #
#################################################


class UtilsTests(unittest.TestCase):
    "Tests for funcitons contained in Utils"

    def setUp(self):
        """Executed prior to each test."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_adjacent_query(self):
        """TESTS a query that is stored in database"""
        response = get_degree(
            "https://en.wikipedia.org/wiki/Adolf_Hitler",
            "https://en.wikipedia.org/wiki/Dictator",
        )
        self.assertNotEqual(response, None)
        self.assertEqual(response.cached, False)
        self.assertEqual(response.degree, 1)

    def test_stored_query(self):
        """TESTS a query that should return 1"""
        CreateMatch()
        response = get_degree("TESTURL1", "TESTURL2")
        self.assertNotEqual(response, None)
        self.assertEqual(response.cached, True)
        self.assertEqual(response.degree, 33)

    def test_long_query(self):
        """TESTS a deep query"""
        response = get_degree(
            "https://en.wikipedia.org/wiki/Adolf_Hitler",
            "https://en.wikipedia.org/wiki/Regional_Italian",
        )
        self.assertNotEqual(response, None)
        self.assertEqual(response.cached, False)
        self.assertEqual(response.degree, 8)

    def test_dead_end(self):
        """TESTS a query with no links to follow"""
        response = get_degree(
            ("https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources" +
                "/Noticeboard"),
            "https://en.wikipedia.org/wiki/Regional_Italian",
        )
        self.assertNotEqual(response, None)
        self.assertEqual(response.cached, False)
        self.assertEqual(response.degree, None)
        self.assertTrue(response.dead)
