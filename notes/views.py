from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from notes.models import Note


class IndexView(generic.ListView):
    template_name = 'notes/index.html'
    context_object_name = 'own_note_list'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """Return own notes."""
        return Note.objects.filter(user=self.request.user, in_history=False)\
            .order_by('-edit_date')


class HistoryView(generic.ListView):
    template_name = 'notes/history.html'
    context_object_name = 'own_note_list'

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))
        return super(HistoryView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        context['title'] = _('History')
        return context

    def get_queryset(self):
        """Return own history."""
        if not self.request.user.is_authenticated():
            return []
        return Note.objects.filter(user=self.request.user, in_history=True)\
            .order_by('-edit_date')


@login_required(login_url='login')
def edit(request, note_id):
    try:
        note = Note.objects.get(pk=note_id, user=request.user)
    except:
        return HttpResponseRedirect(reverse('notes:index'))
    context = {'title': _('Edit note'), 'note': note}
    return render(request, 'notes/edit.html', context)


@login_required(login_url='login', redirect_field_name=None)
def save(request, note_id):
    note = get_object_or_404(Note, pk=note_id, user=request.user)
    try:
        content = request.POST['content']
    except (KeyError):
        return render(request, 'notes/edit.html', {
            'error_message': _("Can't save note."),
        })
    else:
        note.content = content if content else 'Nothing'
        note.edit_date = timezone.now()
        note.save()
        return HttpResponseRedirect(reverse('notes:index'))


@login_required(login_url='login')
def new(request):
    context = {'title': _('New note')}
    return render(request, 'notes/new.html', context)


@login_required(login_url='login', redirect_field_name=None)
def add(request):
    try:
        content = request.POST['content']
    except (KeyError):
        return render(request, 'notes/new.html', {
            'error_message': _("Can't add new note."),
        })
    else:
        content = content if content else _('Nothing')
        note = Note(content=content,
                    user=request.user,
                    edit_date=timezone.now())
        note.save()
        return HttpResponseRedirect(reverse('notes:index'))


@login_required(login_url='login', redirect_field_name=None)
def move(request, note_id):
    note = get_object_or_404(Note, pk=note_id, user=request.user)
    note.in_history = False if note.in_history else True
    note.save()
    return HttpResponseRedirect(reverse('notes:index'))


@login_required(login_url='login', redirect_field_name=None)
def delete(request, note_id):
    note = get_object_or_404(Note, pk=note_id, user=request.user)
    note.delete()
    return HttpResponseRedirect(reverse('notes:index'))


@login_required(login_url='login', redirect_field_name=None)
def clear_history(request):
    notes = Note.objects.filter(user=request.user, in_history=True)
    for note in notes:
        note.delete()
    return HttpResponseRedirect(reverse('notes:history'))

def main_index(request):
    return HttpResponseRedirect(reverse('notes:index'))
