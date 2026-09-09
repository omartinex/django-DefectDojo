from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

# Provider enable-flag -> social-auth backend slug, in the order 2.58.4 checked them.
_PROVIDER_BACKENDS = (
    ("GOOGLE_OAUTH_ENABLED", "google-oauth2"),
    ("OKTA_OAUTH_ENABLED", "okta-oauth2"),
    ("AZUREAD_TENANT_OAUTH2_ENABLED", "azuread-tenant-oauth2"),
    ("GITLAB_OAUTH2_ENABLED", "gitlab"),
    ("KEYCLOAK_OAUTH2_ENABLED", "keycloak"),
    ("OIDC_AUTH_ENABLED", "oidc"),
    ("AUTH0_OAUTH2_ENABLED", "auth0"),
    ("GITHUB_ENTERPRISE_OAUTH2_ENABLED", "github-enterprise"),
)


def get_sso_auto_redirect(request):
    """
    Return an HttpResponseRedirect to the SSO provider, or None to render the login form.

    Only redirects when the local login form is hidden, auto-redirect is on, and exactly
    one provider is enabled — with two providers there is no unambiguous choice.
    ``?force_login_form`` always wins, so the local form stays reachable if the IdP is down.
    """
    if settings.SHOW_LOGIN_FORM or not settings.SOCIAL_LOGIN_AUTO_REDIRECT:
        return None
    if "force_login_form" in request.GET:
        return None

    enabled = [slug for flag, slug in _PROVIDER_BACKENDS if getattr(settings, flag, False)]
    if len(enabled) != 1:
        return None

    begin_url = reverse("social:begin", args=[enabled[0]])
    return HttpResponseRedirect(f"{begin_url}?{urlencode({'next': request.GET.get('next', '/dashboard')})}")
