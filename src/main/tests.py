import unittest
import datetime

from src import app, db
from src.models import Page, Matches


def CreatePage(url1):
    page = Page(
        name=url1,
        queried=1,
    )
    db.session.add(page)
    db.session.commit()
    return page


def CreateMatch():
    m1 = Matches(
        name="TESTURL1 => TESTURL2",
        url1=CreatePage("TESTURL1"),
        url2=CreatePage("TESTURL2"),
        degrees=33,
        last=datetime.datetime.now(),
    )

    m2 = Matches(
        name="TESTURL2 => TESTURL4",
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


class MainTests(unittest.TestCase):
    "Tests for the routes conatined in Main.py"

    def setUp(self):
        """Executed prior to each test."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_landing_page(self):
        """TESTS Landing page appears on base route"""
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        res_txt = response.get_data(as_text=True)

        self.assertIn("input", res_txt)
        self.assertIn("button", res_txt)
        self.assertIn("Degrees of Wiki", res_txt)

    def test_recent_querys(self):
        """TESTS Landing page shows recent queries"""
        CreateMatch()

        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        res_txt = response.get_data(as_text=True)

        self.assertIn("TESTURL1", res_txt)
        self.assertIn("TESTURL2", res_txt)

    def test_query_new(self):
        """TESTS new query shows proper response"""
        response = self.app.get(
            "/degree/?url1=Adolf_Hitler&url2=Dictator",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        res_txt = response.get_data(as_text=True)

        self.assertIn("Degrees: 1", res_txt)

    def test_query_cached(self):
        """TESTS query that is stored in database"""
        CreateMatch()

        response = self.app.get(
            "/degree/?url1=TESTURL1&url2=TESTURL2", follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

        res_txt = response.get_data(as_text=True)

        self.assertIn("Degrees: 33", res_txt)
