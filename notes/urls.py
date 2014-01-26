from django.conf.urls import patterns, url
from notes import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^add/$', views.add, name='add'),
    url(r'^new/$', views.new, name='new'),
    url(r'^history/$', views.HistoryView.as_view(), name='history'),
    url(r'^(?P<note_id>\d+)/save/$', views.save, name='save'),
    url(r'^(?P<note_id>\d+)/move/$', views.move, name='move'),
    url(r'^(?P<note_id>\d+)/delete/$', views.delete, name='delete'),
    url(r'^(?P<note_id>\d+)/$', views.edit, name='edit'),
    url(r'^history/clear/$', views.clear_history, name='clear_history'),
)
