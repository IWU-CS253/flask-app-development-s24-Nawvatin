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
        # Test when database is not empty
        with flaskr.app.app_context():
            db = flaskr.get_db()
            db.execute('INSERT INTO entries (id, title, text, category) VALUES (?, ?, ?, ?)',
                       [1, 'Test Title', 'Test Text', 'Test Category'])
            db.commit()

        rv = self.app.get('/')
        assert b'No entries here so far' not in rv.data
        assert b'Test Title' in rv.data
        assert b'Test Text' in rv.data
        assert b'Test Category' in rv.data

        # Test when database is empty
        with flaskr.app.app_context():
            db = flaskr.get_db()
            db.execute('DELETE FROM entries')
            db.commit()

        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_messages(self):
        # Test valid message submission
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

        # Test invalid message submission (e.g., empty fields)
        rv = self.app.post('/add', data=dict(
            title='',
            text='',
            category=''
        ), follow_redirects=True)
        assert b'Field must be filled out' in rv.data

    def test_delete_entry(self):
        # Test when entry to be deleted doesn't exist
        response = self.app.post('/delete', data={'id': 999})
        self.assertEqual(response.status_code, 404)

        # Test when deletion request is made with invalid parameters
        response = self.app.post('/delete', data={})
        self.assertEqual(response.status_code, 400)

    def test_edit_entry(self):
        # Test when entry to be edited doesn't exist
        response = self.app.post('/edit/999', data=dict(
            title='Updated Title',
            text='Updated Text',
            category='Updated Category'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 404)

        # Test when edit request is made with invalid parameters
        response = self.app.post('/edit/1', data={})
        self.assertEqual(response.status_code, 400)

        # Test editing only specific fields
        with flaskr.app.app_context():
            db = flaskr.get_db()
            db.execute('INSERT INTO entries (id, title, text, category) VALUES (?, ?, ?, ?)',
                       [1, 'Old Title', 'Old Text', 'Old Category'])
            db.commit()

        response = self.app.post('/edit/1', data=dict(
            title='Updated Title',
        ), follow_redirects=True)

        with flaskr.app.app_context():
            db = flaskr.get_db()
            entry = db.execute('SELECT * FROM entries WHERE id = ?', [1]).fetchone()
            self.assertIsNotNone(entry)
            self.assertEqual(entry['title'], 'Updated Title')
            self.assertEqual(entry['text'], 'Old Text')  # Text should remain unchanged
            self.assertEqual(entry['category'], 'Old Category')  # Category should remain unchanged

if __name__ == '__main__':
    unittest.main()
