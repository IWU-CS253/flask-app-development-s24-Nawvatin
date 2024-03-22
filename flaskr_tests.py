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

    def test_delete_entry(self):
        with app.app_context():
            # Insert a test entry into the database
            db = get_db()
            db.execute("INSERT INTO entries (title, category, text) VALUES (?, ?, ?)",
                       ["Test Title", "Test Category", "Test Text"])
            db.commit()

            # Retrieve the ID of the test entry
            entry_id = db.execute("SELECT id FROM entries WHERE title=?", ["Test Title"]).fetchone()['id']

            # Send a POST request to delete the test entry
            response = self.app.post('/delete', data={'id': entry_id})

            # Check if the entry was deleted
            self.assertEqual(response.status_code, 302)  # Redirect status code
            self.assertIn(b'Entry deleted', response.data)  # Check flash message

            # Check if the entry is no longer in the database
            entry = db.execute("SELECT * FROM entries WHERE id=?", [entry_id]).fetchone()
            self.assertIsNone(entry)


if __name__ == '__main__':
    unittest.main()