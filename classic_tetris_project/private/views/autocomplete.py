from dal import autocomplete

from classic_tetris_project.models import TwitchChannel


class TwitchChannelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TwitchChannel.objects.all()
        if self.q:
            qs = qs.filter(twitch_user__username__istartswith=self.q)

        return qs
