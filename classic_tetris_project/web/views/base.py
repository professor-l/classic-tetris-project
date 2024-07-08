from django.views import View

from classic_tetris_project.util.memo import lazy

class BaseView(View):
    @lazy
    def current_user(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, "website_user"):
            return self.request.user.website_user.user
        else:
            return None
