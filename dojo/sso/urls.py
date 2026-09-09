from django.conf.urls import include
from django.urls import re_path

# Registers /login/<backend>/ and /complete/<backend>/ under the "social" namespace.
# "complete/" is already in LOGIN_EXEMPT_URLS in settings.dist.py, so the callback is
# reachable while the user is still anonymous.
urlpatterns = [
    re_path("", include("social_django.urls", namespace="social")),
]
