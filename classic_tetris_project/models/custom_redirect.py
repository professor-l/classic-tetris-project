from django.http import HttpResponseRedirect
from django.contrib.redirects.middleware import RedirectFallbackMiddleware

class HttpResponseTemporaryRedirect(HttpResponseRedirect):
  status_code = 307

class CustomRedirect(RedirectFallbackMiddleware):
  response_redirect_class = HttpResponseTemporaryRedirect
