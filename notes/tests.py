import datetime
from django.utils import timezone
from django.test import TestCase
from notes.models import Note
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


def create_note(user, content=None, in_history=None, edit_date=None):
    user = user
    content = content if content else 'Nothing'
    in_history = in_history if in_history else False
    edit_date = edit_date if edit_date else timezone.now()

    return Note.objects.create(content=content,
                               in_history=in_history,
                               user=user,
                               edit_date=edit_date)


class NoteViewTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('temporary1',
                                              'temporary1@ntreal.com',
                                              'temporary1')
        self.user2 = User.objects.create_user('temporary2',
                                              'temporary2@ntreal.com',
                                              'temporary2')

    """
    Test index
    """

    def test_index_view_not_logged_in(self):
        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='temporary1', password='temporary1')
        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)

    def test_index_view_with_notes(self):
        self.client.login(username='temporary1', password='temporary1')
        create_note(self.user1, content='Test note')
        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

    def test_index_view_without_notes(self):
        self.client.login(username='temporary1', password='temporary1')
        response = self.client.get(reverse('notes:index'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])

    def test_index_view_foreign_notes(self):
        self.client.login(username='temporary1', password='temporary1')
        create_note(self.user1, content='Test note')
        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

        self.client.logout()
        self.client.login(username='temporary2', password='temporary2')
        response = self.client.get(reverse('notes:index'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])

    """
    Test history
    """

    def test_history_view_not_logged_in(self):
        response = self.client.get(reverse('notes:history'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='temporary1', password='temporary1')
        response = self.client.get(reverse('notes:history'))
        self.assertEqual(response.status_code, 200)

    def test_history_view_with_notes(self):
        self.client.login(username='temporary1', password='temporary1')
        create_note(self.user1, content='Test note', in_history=True)
        response = self.client.get(reverse('notes:history'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

    def test_history_view_without_notes(self):
        self.client.login(username='temporary1', password='temporary1')
        response = self.client.get(reverse('notes:history'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])

    def test_history_view_foreign_notes(self):
        self.client.login(username='temporary1', password='temporary1')
        create_note(self.user1, content='Test note', in_history=True)
        response = self.client.get(reverse('notes:history'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

        self.client.logout()
        self.client.login(username='temporary2', password='temporary2')
        response = self.client.get(reverse('notes:history'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])

    """
    Test move
    """

    def test_move_view_move_to_history(self):
        self.client.login(username='temporary1', password='temporary1')
        note = create_note(self.user1, content='Test note')
        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

        response = self.client.get(reverse('notes:history'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])
        response = self.client.post(reverse('notes:move', args=(note.id,)))

        response = self.client.get(reverse('notes:history'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

    def test_move_view_remove_from_history(self):
        self.client.login(username='temporary1', password='temporary1')
        note = create_note(self.user1, content='Test note', in_history=True)
        response = self.client.get(reverse('notes:history'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

        response = self.client.get(reverse('notes:index'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])
        response = self.client.post(reverse('notes:move', args=(note.id,)))

        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

    def test_move_view_not_logged_in(self):
        note_id = '0'
        response = self.client.post(reverse('notes:move', args=(note_id, )))
        self.assertEqual(response.status_code, 302)

    def test_move_view_wrong_note_id(self):
        self.client.login(username='temporary1', password='temporary1')
        note_id = '0'
        response = self.client.post(reverse('notes:move', args=(note_id, )))
        self.assertEqual(response.status_code, 404)

    def test_move_view_foreign_note(self):
        self.client.login(username='temporary1', password='temporary1')
        note = create_note(self.user1, content='Test note')
        self.client.logout()
        self.client.login(username='temporary2', password='temporary2')

        response = self.client.post(reverse('notes:move', args=(note.id, )))
        self.assertEqual(response.status_code, 404)

    """
    Test add
    """

    def test_add_view_add_note(self):
        self.client.login(username='temporary1', password='temporary1')
        response = self.client.get(reverse('notes:index'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])

        response = self.client.post(reverse('notes:add'),
                                    {'content': "Test note"})

        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

    def test_add_view_not_logged_in(self):
        response = self.client.post(reverse('notes:add'),
                                    {'content': "Test note"})
        self.assertEqual(response.status_code, 302)

    """
    Test delete
    """

    def test_delete_view_delete_note(self):
        self.client.login(username='temporary1', password='temporary1')
        note = create_note(self.user1, content='Test note')
        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

        response = self.client.post(reverse('notes:delete',
                                            args=(note.id, )))

        response = self.client.get(reverse('notes:index'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])

    def test_delete_view_not_logged_in(self):
        note_id = '0'
        response = self.client.post(reverse('notes:delete', args=(note_id, )))
        self.assertEqual(response.status_code, 302)

    def test_delete_view_wrong_note_id(self):
        self.client.login(username='temporary1', password='temporary1')
        note_id = '0'
        response = self.client.post(reverse('notes:delete', args=(note_id, )))
        self.assertEqual(response.status_code, 404)

    def test_delete_view_foreign_note(self):
        self.client.login(username='temporary1', password='temporary1')
        note = create_note(self.user1, content='Test note')
        self.client.logout()
        self.client.login(username='temporary2', password='temporary2')

        response = self.client.post(reverse('notes:delete', args=(note.id, )))
        self.assertEqual(response.status_code, 404)

    """
    Test clear_history
    """

    def test_clear_history_view_clear_history(self):
        self.client.login(username='temporary1', password='temporary1')
        create_note(self.user1, content='Test note', in_history=True)
        response = self.client.get(reverse('notes:history'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

        response = self.client.get(reverse('notes:clear_history'))

        response = self.client.get(reverse('notes:history'))
        self.assertContains(response, "No notes are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['own_note_list'], [])

    def test_clear_history_view_not_logged_in(self):
        response = self.client.get(reverse('notes:clear_history'))
        self.assertEqual(response.status_code, 302)

    """
    Test save
    """

    def test_save_view_save_note(self):
        self.client.login(username='temporary1', password='temporary1')
        note = create_note(self.user1, content='Test note')
        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Test note>']
        )

        response = self.client.post(reverse('notes:save', args=(note.id, )),
                                    {'content': "Edited note"})

        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['own_note_list'],
            ['<Note: Edited note>']
        )

    def test_save_view_not_logged_in(self):
        note_id = 0
        response = self.client.post(reverse('notes:save', args=(note_id, )),
                                    {'content': "Test note"})
        self.assertEqual(response.status_code, 302)

    def test_save_view_wrong_note_id(self):
        self.client.login(username='temporary1', password='temporary1')
        note_id = '0'
        response = self.client.post(reverse('notes:save', args=(note_id, )),
                                    {'content': "Test note"})
        self.assertEqual(response.status_code, 404)

    def test_save_view_foreign_note(self):
        self.client.login(username='temporary1', password='temporary1')
        note = create_note(self.user1, content='Test note')
        self.client.logout()
        self.client.login(username='temporary2', password='temporary2')

        response = self.client.post(reverse('notes:save', args=(note.id, )),
                                    {'content': "Test note"})
        self.assertEqual(response.status_code, 404)

    """
    Test edit
    """

    def test_edit_view_not_logged_in(self):
        note_id = '0'
        response = self.client.get(reverse('notes:edit', args=(note_id, )))
        self.assertEqual(response.status_code, 302)

    def test_edit_view_wrong_note_id(self):
        self.client.login(username='temporary1', password='temporary1')
        note_id = '0'
        response = self.client.get(reverse('notes:edit', args=(note_id, )))
        self.assertEqual(response.status_code, 302)

    def test_edit_view_foreign_note(self):
        self.client.login(username='temporary1', password='temporary1')
        note = create_note(self.user1, content='Test note')
        self.client.logout()
        self.client.login(username='temporary2', password='temporary2')

        response = self.client.get(reverse('notes:edit', args=(note.id, )))
        self.assertEqual(response.status_code, 302)
