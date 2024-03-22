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
        # Create a test entry in the database to delete
        with flaskr.app.app_context():
            db = flaskr.get_db()
            db.execute('INSERT INTO entries (id, title, text, category) VALUES (?, ?, ?, ?)',
                       [1, 'data1', 'data2', 'data3'])
            db.commit()

        # Send a POST request to delete the test entry
        response = self.app.post('/delete', data={'id': 1})
        self.assertEqual(response.status_code, 302)

        # Check if the test entry was deleted from the database
        with flaskr.app.app_context():
            db = flaskr.get_db()
            entry = db.execute('SELECT * FROM entries WHERE id = ?', [1]).fetchone()
            self.assertIsNone(entry)

    def test_edit_entry(self):
        # Create a test entry in the database to edit
        with flaskr.app.app_context():
            db = flaskr.get_db()
            db.execute('INSERT INTO entries (id, title, text, category) VALUES (?, ?, ?, ?)',
                       [1, 'Old Title', 'Old Text', 'Old Category'])
            db.commit()

        # Send a POST request to edit the test entry
        response = self.app.post('/edit/1', data=dict(
            title='Updated Title',
            text='Updated Text',
            category='Updated Category'
        ), follow_redirects=True)

        # Check if the test entry was successfully updated in the database
        with flaskr.app.app_context():
            db = flaskr.get_db()
            entry = db.execute('SELECT * FROM entries WHERE id = ?', [1]).fetchone()
            self.assertIsNotNone(entry)
            self.assertEqual(entry['title'], 'Updated Title')
            self.assertEqual(entry['text'], 'Updated Text')
            self.assertEqual(entry['category'], 'Updated Category')

if __name__ == '__main__':
    unittest.main()