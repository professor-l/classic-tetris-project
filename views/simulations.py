from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.static import serve

from classic_tetris_project.util.fieldgen.hz_simulation import HzSimulation
from classic_tetris_project.util.memo import lazy
from .base import BaseView


class HzView(BaseView):
    def get(self, request):
        try:
            self.simulation.cache_image()
        except (KeyError, ValueError):
            return HttpResponseBadRequest("Invalid params")

        if settings.DEBUG:
            return serve(request, self.simulation.filename, HzSimulation.IMAGE_CACHE.root)
        else:
            # Serve up the cached file much more efficiently using nginx:
            # https://www.nginx.com/resources/wiki/start/topics/examples/x-accel/
            response = HttpResponse(content_type="image/gif")
            response["X-Accel-Redirect"] = HzSimulation.IMAGE_CACHE.cache_path(self.simulation.filename)
            return response

    @lazy
    def simulation(self):
        level = int(self.request.GET["level"])
        height = int(self.request.GET["height"])
        taps = int(self.request.GET["taps"])
        return HzSimulation(level, height, taps)
