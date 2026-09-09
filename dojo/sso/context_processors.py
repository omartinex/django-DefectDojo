from django.conf import settings


def sso_context(request):
    """
    Expose the per-provider enable flags to the login templates.

    ``SSO_AVAILABLE`` is what the login templates key off to decide whether to render the
    provider buttons at all; it is only True when this module is installed.
    """
    return {
        "SSO_AVAILABLE": True,
        # 2.58.4 exposed this from dojo/context_processors.py; it lives here instead so
        # the fork does not have to patch that upstream file.
        "SHOW_LOGIN_FORM": settings.SHOW_LOGIN_FORM,
        "OIDC_ENABLED": settings.OIDC_AUTH_ENABLED,
        "SOCIAL_AUTH_OIDC_LOGIN_BUTTON_TEXT": settings.SOCIAL_AUTH_OIDC_LOGIN_BUTTON_TEXT,
        "AUTH0_ENABLED": settings.AUTH0_OAUTH2_ENABLED,
        "GOOGLE_ENABLED": settings.GOOGLE_OAUTH_ENABLED,
        "OKTA_ENABLED": settings.OKTA_OAUTH_ENABLED,
        "GITLAB_ENABLED": settings.GITLAB_OAUTH2_ENABLED,
        "AZUREAD_TENANT_OAUTH2_ENABLED": settings.AZUREAD_TENANT_OAUTH2_ENABLED,
        "KEYCLOAK_ENABLED": settings.KEYCLOAK_OAUTH2_ENABLED,
        "SOCIAL_AUTH_KEYCLOAK_LOGIN_BUTTON_TEXT": settings.SOCIAL_AUTH_KEYCLOAK_LOGIN_BUTTON_TEXT,
        "GITHUB_ENTERPRISE_ENABLED": settings.GITHUB_ENTERPRISE_OAUTH2_ENABLED,
    }
