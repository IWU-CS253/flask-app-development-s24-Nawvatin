import os
import app as flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    def test_show_entries(self):
        with app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'show_entries.html', response.data)
            self.assertTrue(b'entries' in response.data)

    def test_close_db(self):
        with app.app_context():
            g = type('G', (object,), {'sqlite_db': type('SQLiteDB', (object,), {'close': lambda self: None})})()
            close_db(None)
            self.assertTrue(hasattr(g.sqlite_db, 'close'))
            self.assertTrue(callable(g.sqlite_db.close))

if __name__ == '__main__':
    unittest.main()
