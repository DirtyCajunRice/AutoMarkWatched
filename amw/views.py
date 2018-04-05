from django.views import View
from django.contrib import messages
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.http import HttpResponseRedirect, HttpResponse

from .utilities import plex, thetvdb
from .models import TVShow, ServerInfo
from .forms import ServerForm

class HomeView(ListView):
    template_name = "home.html"
    context_object_name = "tv_shows"

    def get_queryset(self):
        context = TVShow.objects.order_by('title')
        return context

    def post(self, request, *args, **kwargs):
        bulkeditinfo = [ (show, request.POST[show]) for show in request.POST if 'csrfmiddlewaretoken' not in show ]
        valid = {
            'True': True,
            'False': False
        }
        for pkid, choice in bulkeditinfo:
            show = TVShow.objects.filter(id=pkid)[0]
            if show.silenced != valid[choice]:
                show.silenced = valid[choice]
                show.save()
                if valid[choice]:
                    print('Silenced {}'.format(show.title))
                else:
                    print('Unsilenced {}'.format(show.title))
        return HttpResponseRedirect('/')


class SettingsView(TemplateView):
    form_class = ServerForm
    initial = {'key': 'value'}
    template_name = "settings.html"

    def get(self, request, *args, **kwargs):
        serverinfo = ''
        if ServerInfo.objects.count() > 0:
            serverinfo = ServerInfo.objects.all()[0]
            self.initial = {'url': serverinfo.url, 'token': serverinfo.token}
        form = self.form_class(initial=self.initial)
        context = {
            'form': form,
            'tvshows': TVShow.objects.all(),
            'serverinfo': serverinfo
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ServerForm(request.POST)
        if form.is_valid():
            if ServerInfo.objects.count() > 0:
                for server in ServerInfo.objects.all():
                    server.delete()
            server = ServerInfo(url=form.cleaned_data['url'], token=form.cleaned_data['token'])
            server.save()
        else:
            print('shit')
        return HttpResponseRedirect('/settings')

class ShowDetailView(TemplateView):
    template_name = "showdetail.html"

    def get(self, request, show_pk, *args, **kwargs):
        context = { 'show': TVShow.objects.get(pk=show_pk) }
        return render(request, self.template_name, context)

    def post(self, request, show_pk, *args, **kwargs):
        show = TVShow.objects.get(pk=show_pk)

        if show.silenced:
            show.silenced = False
            print('Unsilenced {}'.format(show.title))
        else:
            show.silenced = True
            print('Silenced {}'.format(show.title))

        show.save()

        return HttpResponseRedirect('/{}'.format(show_pk))


def filltable(request):

    if request.method == "POST":
        server = plex.Plex()
        server.rectify_show_list()
        messages.success(request, 'Success! TV Show table populated!')

        return HttpResponseRedirect('/')

def syncTVDB(request):

    if request.method == "POST":
        server = thetvdb.TheTVDB()
        server.syncShows()
        messages.success(request, 'Success! TV show continuing status synced with TheTVDB')

        return HttpResponseRedirect('/')

def markWatched(request):

    if request.method == "POST":
        server = plex.Plex()
        server.mark_watched()
        messages.success(request, 'Success! TV shows have been marked watched')

        return HttpResponseRedirect('/settings')

