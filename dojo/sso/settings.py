"""
SSO settings for the OAuth2/OIDC login backends.

Ported from DefectDojo 2.58.4 (`dojo/sso/settings.py`), which upstream removed in
``952a56d13f`` when the authorization layer moved to the Pro edition. Scope of this
port is *login only*: the eight OAuth2 backends social-core ships. SAML2 and
REMOTE_USER were deliberately left behind, as was every pipeline step that writes to
the RBAC tables (``Dojo_Group``, ``Product_Member``, ``Role``) — those are
``managed=False`` shells owned by Pro since ``dojo.0268_release_authorization_to_pro``.
Group mapping is a separate deliverable.

The shape here mirrors ``dojo/auditlog/settings.py`` and ``dojo/notifications/settings.py``:
an ``ENV_SCHEMA`` dict merged into the ``environ.FileAwareEnv`` constructor, plus an
``apply_*_settings(env, globals())`` call from ``dojo/settings/settings.dist.py``.

Note the dependency pins are NOT 2.58.4's: ``social-auth-core==4.8.7`` hard-pins
``PyJWT[crypto]==2.12.1``, and ``952a56d13f`` bumped PyJWT to 2.13.0 in the same commit
that dropped SSO. This runs on ``social-auth-core==5.1.0`` /
``social-auth-app-django==6.0.1``, which require ``PyJWT>=2.13.0``.

``apply_sso_settings`` MUTATES ``MIDDLEWARE``, so it has to run after the last
``MIDDLEWARE = [...]`` rebinding in ``settings.dist.py`` — i.e. at the very end of that
file. Calling it earlier silently drops ``CustomSocialAuthExceptionMiddleware``.
"""

SSO_ENV_SCHEMA = {
    "DD_SOCIAL_AUTH_SHOW_LOGIN_FORM": (bool, True),  # do we show user/pass input
    # Useful to disable when non-local authentication (OIDC, Azure, ...) is in place
    "DD_SOCIAL_LOGIN_AUTO_REDIRECT": (bool, False),  # auto-redirect if there is only one social login method
    "DD_SOCIAL_AUTH_CREATE_USER": (bool, True),
    "DD_SOCIAL_AUTH_CREATE_USER_MAPPING": (str, "username"),
    "DD_SOCIAL_AUTH_REDIRECT_IS_HTTPS": (bool, False),
    "DD_SOCIAL_AUTH_TRAILING_SLASH": (bool, True),
    "DD_SOCIAL_AUTH_OIDC_AUTH_ENABLED": (bool, False),
    "DD_SOCIAL_AUTH_OIDC_OIDC_ENDPOINT": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_ID_KEY": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_KEY": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_SECRET": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_USERNAME_KEY": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_WHITELISTED_DOMAINS": (list, []),
    "DD_SOCIAL_AUTH_OIDC_JWT_ALGORITHMS": (list, ["RS256", "HS256"]),
    "DD_SOCIAL_AUTH_OIDC_ID_TOKEN_ISSUER": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_ACCESS_TOKEN_URL": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_AUTHORIZATION_URL": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_USERINFO_URL": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_JWKS_URI": (str, ""),
    "DD_SOCIAL_AUTH_OIDC_LOGIN_BUTTON_TEXT": (str, "Login with OIDC"),
    "DD_SOCIAL_AUTH_AUTH0_OAUTH2_ENABLED": (bool, False),
    "DD_SOCIAL_AUTH_AUTH0_KEY": (str, ""),
    "DD_SOCIAL_AUTH_AUTH0_SECRET": (str, ""),
    "DD_SOCIAL_AUTH_AUTH0_DOMAIN": (str, ""),
    "DD_SOCIAL_AUTH_AUTH0_SCOPE": (list, ["openid", "profile", "email"]),
    "DD_SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED": (bool, False),
    "DD_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": (str, ""),
    "DD_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET": (str, ""),
    "DD_SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS": (list, [""]),
    "DD_SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_EMAILS": (list, [""]),
    "DD_SOCIAL_AUTH_OKTA_OAUTH2_ENABLED": (bool, False),
    "DD_SOCIAL_AUTH_OKTA_OAUTH2_KEY": (str, ""),
    "DD_SOCIAL_AUTH_OKTA_OAUTH2_SECRET": (str, ""),
    "DD_SOCIAL_AUTH_OKTA_OAUTH2_API_URL": (str, "https://{your-org-url}/oauth2"),
    "DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_ENABLED": (bool, False),
    "DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY": (str, ""),
    "DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET": (str, ""),
    "DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID": (str, ""),
    "DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_RESOURCE": (str, "https://graph.microsoft.com/"),
    "DD_SOCIAL_AUTH_GITLAB_OAUTH2_ENABLED": (bool, False),
    "DD_SOCIAL_AUTH_GITLAB_KEY": (str, ""),
    "DD_SOCIAL_AUTH_GITLAB_SECRET": (str, ""),
    "DD_SOCIAL_AUTH_GITLAB_API_URL": (str, "https://gitlab.com"),
    "DD_SOCIAL_AUTH_GITLAB_SCOPE": (list, ["read_user", "openid"]),
    "DD_SOCIAL_AUTH_KEYCLOAK_OAUTH2_ENABLED": (bool, False),
    "DD_SOCIAL_AUTH_KEYCLOAK_KEY": (str, ""),
    "DD_SOCIAL_AUTH_KEYCLOAK_SECRET": (str, ""),
    "DD_SOCIAL_AUTH_KEYCLOAK_PUBLIC_KEY": (str, ""),
    "DD_SOCIAL_AUTH_KEYCLOAK_AUTHORIZATION_URL": (str, ""),
    "DD_SOCIAL_AUTH_KEYCLOAK_ACCESS_TOKEN_URL": (str, ""),
    "DD_SOCIAL_AUTH_KEYCLOAK_LOGIN_BUTTON_TEXT": (str, "Login with Keycloak"),
    "DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_OAUTH2_ENABLED": (bool, False),
    "DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_URL": (str, ""),
    "DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_API_URL": (str, ""),
    "DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_KEY": (str, ""),
    "DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_SECRET": (str, ""),
    "DD_SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL": (bool, True),
    "DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_REQUEST_EXCEPTION": (str, "Please use the standard login below."),
    "DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_CANCELED": (str, "Social login was canceled. Please try again or use the standard login."),
    "DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_FAILED": (str, "Social login failed. Please try again or use the standard login."),
    "DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_FORBIDDEN": (str, "You are not authorized to log in via this method. Please contact support or use the standard login."),
    "DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_NONE_TYPE": (str, "An unexpected error occurred during social login. Please use the standard login."),
    "DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_TOKEN_ERROR": (str, "Social login failed due to an invalid or expired token. Please try again or use the standard login."),
}


def apply_sso_settings(env, globs):
    """
    Apply all SSO-related settings.

    Called from the very end of settings.dist.py: this mutates MIDDLEWARE,
    INSTALLED_APPS, TEMPLATES and AUTHENTICATION_BACKENDS, and MIDDLEWARE is rebound
    several times further down that file.
    """
    from pathlib import Path  # noqa: PLC0415

    # --------------------------------------------------------------------------
    # LOGIN FORM VISIBILITY
    # --------------------------------------------------------------------------
    globs["SHOW_LOGIN_FORM"] = env("DD_SOCIAL_AUTH_SHOW_LOGIN_FORM")
    globs["SOCIAL_LOGIN_AUTO_REDIRECT"] = env("DD_SOCIAL_LOGIN_AUTO_REDIRECT")

    # --------------------------------------------------------------------------
    # AUTHENTICATION_BACKENDS
    # --------------------------------------------------------------------------
    # Replaces the ModelBackend-only tuple from settings.dist.py. ModelBackend stays
    # last so local username/password auth keeps working as the fallback.
    globs["AUTHENTICATION_BACKENDS"] = (
        "social_core.backends.open_id_connect.OpenIdConnectAuth",
        "social_core.backends.auth0.Auth0OAuth2",
        "social_core.backends.google.GoogleOAuth2",
        "social_core.backends.okta.OktaOAuth2",
        "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
        "social_core.backends.gitlab.GitLabOAuth2",
        "social_core.backends.keycloak.KeycloakOAuth2",
        "social_core.backends.github_enterprise.GithubEnterpriseOAuth2",
        "django.contrib.auth.backends.ModelBackend",
    )

    # --------------------------------------------------------------------------
    # SOCIAL_AUTH_PIPELINE
    # --------------------------------------------------------------------------
    # NOTE: `associate_by_email` links an incoming social identity to an existing local
    # account whose email matches. With an IdP that does not verify email ownership this
    # is an account-takeover vector. Kept because it is the 2.58.4 behaviour and is safe
    # for a single trusted tenant; drop this step if you federate untrusted providers.
    globs["SOCIAL_AUTH_PIPELINE"] = (
        "social_core.pipeline.social_auth.social_details",
        "dojo.sso.pipeline.social_uid",
        "social_core.pipeline.social_auth.auth_allowed",
        "social_core.pipeline.social_auth.social_user",
        "social_core.pipeline.user.get_username",
        "social_core.pipeline.social_auth.associate_by_email",
        "dojo.sso.pipeline.create_user",
        "social_core.pipeline.social_auth.associate_user",
        "social_core.pipeline.social_auth.load_extra_data",
        "social_core.pipeline.user.user_details",
    )

    # --------------------------------------------------------------------------
    # SOCIAL AUTH GENERAL
    # --------------------------------------------------------------------------
    globs["SOCIAL_AUTH_REDIRECT_IS_HTTPS"] = env("DD_SOCIAL_AUTH_REDIRECT_IS_HTTPS")
    # SOCIAL_AUTH_CREATE_USER=True means every user the IdP authenticates gets a local
    # account on first login. Set DD_SOCIAL_AUTH_CREATE_USER=False to require that an
    # account be provisioned up front.
    globs["SOCIAL_AUTH_CREATE_USER"] = env("DD_SOCIAL_AUTH_CREATE_USER")
    globs["SOCIAL_AUTH_CREATE_USER_MAPPING"] = env("DD_SOCIAL_AUTH_CREATE_USER_MAPPING")

    globs["SOCIAL_AUTH_STRATEGY"] = "social_django.strategy.DjangoStrategy"
    globs["SOCIAL_AUTH_STORAGE"] = "social_django.models.DjangoStorage"
    globs["SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS"] = ["username", "first_name", "last_name", "email"]
    globs["SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL"] = env("DD_SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL")
    globs["SOCIAL_AUTH_LOGIN_ERROR_URL"] = "/login"
    globs["SOCIAL_AUTH_BACKEND_ERROR_URL"] = "/login"

    # --------------------------------------------------------------------------
    # OIDC
    # --------------------------------------------------------------------------
    globs["OIDC_AUTH_ENABLED"] = env("DD_SOCIAL_AUTH_OIDC_AUTH_ENABLED")
    globs["SOCIAL_AUTH_OIDC_OIDC_ENDPOINT"] = env("DD_SOCIAL_AUTH_OIDC_OIDC_ENDPOINT")
    globs["SOCIAL_AUTH_OIDC_KEY"] = env("DD_SOCIAL_AUTH_OIDC_KEY")
    globs["SOCIAL_AUTH_OIDC_SECRET"] = env("DD_SOCIAL_AUTH_OIDC_SECRET")
    # Optional OIDC settings: only set when non-empty, so social-core falls back to the
    # values it discovers from the provider's .well-known document.
    if value := env("DD_LOGIN_REDIRECT_URL"):
        globs["SOCIAL_AUTH_LOGIN_REDIRECT_URL"] = value
    if value := env("DD_SOCIAL_AUTH_OIDC_ID_KEY"):
        globs["SOCIAL_AUTH_OIDC_ID_KEY"] = value
    if value := env("DD_SOCIAL_AUTH_OIDC_USERNAME_KEY"):
        globs["SOCIAL_AUTH_OIDC_USERNAME_KEY"] = value
    if env("DD_SOCIAL_AUTH_OIDC_WHITELISTED_DOMAINS"):
        globs["SOCIAL_AUTH_OIDC_WHITELISTED_DOMAINS"] = env("DD_SOCIAL_AUTH_OIDC_WHITELISTED_DOMAINS")
    if env("DD_SOCIAL_AUTH_OIDC_JWT_ALGORITHMS"):
        globs["SOCIAL_AUTH_OIDC_JWT_ALGORITHMS"] = env("DD_SOCIAL_AUTH_OIDC_JWT_ALGORITHMS")
    if value := env("DD_SOCIAL_AUTH_OIDC_ID_TOKEN_ISSUER"):
        globs["SOCIAL_AUTH_OIDC_ID_TOKEN_ISSUER"] = value
    if value := env("DD_SOCIAL_AUTH_OIDC_ACCESS_TOKEN_URL"):
        globs["SOCIAL_AUTH_OIDC_ACCESS_TOKEN_URL"] = value
    if value := env("DD_SOCIAL_AUTH_OIDC_AUTHORIZATION_URL"):
        globs["SOCIAL_AUTH_OIDC_AUTHORIZATION_URL"] = value
    if value := env("DD_SOCIAL_AUTH_OIDC_USERINFO_URL"):
        globs["SOCIAL_AUTH_OIDC_USERINFO_URL"] = value
    if value := env("DD_SOCIAL_AUTH_OIDC_JWKS_URI"):
        globs["SOCIAL_AUTH_OIDC_JWKS_URI"] = value
    globs["SOCIAL_AUTH_OIDC_LOGIN_BUTTON_TEXT"] = env("DD_SOCIAL_AUTH_OIDC_LOGIN_BUTTON_TEXT")

    # --------------------------------------------------------------------------
    # AZURE AD TENANT OAUTH2
    # --------------------------------------------------------------------------
    globs["AZUREAD_TENANT_OAUTH2_ENABLED"] = env("DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_ENABLED")
    globs["SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY"] = env("DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY")
    globs["SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET"] = env("DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET")
    globs["SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID"] = env("DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID")
    globs["SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_RESOURCE"] = env("DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_RESOURCE")

    # --------------------------------------------------------------------------
    # GOOGLE OAUTH2
    # --------------------------------------------------------------------------
    globs["GOOGLE_OAUTH_ENABLED"] = env("DD_SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED")
    globs["SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"] = env("DD_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
    globs["SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"] = env("DD_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
    globs["SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS"] = tuple(env.list("DD_SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS", default=[""]))
    globs["SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_EMAILS"] = tuple(env.list("DD_SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_EMAILS", default=[""]))

    # --------------------------------------------------------------------------
    # OKTA OAUTH2
    # --------------------------------------------------------------------------
    globs["OKTA_OAUTH_ENABLED"] = env("DD_SOCIAL_AUTH_OKTA_OAUTH2_ENABLED")
    globs["SOCIAL_AUTH_OKTA_OAUTH2_KEY"] = env("DD_SOCIAL_AUTH_OKTA_OAUTH2_KEY")
    globs["SOCIAL_AUTH_OKTA_OAUTH2_SECRET"] = env("DD_SOCIAL_AUTH_OKTA_OAUTH2_SECRET")
    globs["SOCIAL_AUTH_OKTA_OAUTH2_API_URL"] = env("DD_SOCIAL_AUTH_OKTA_OAUTH2_API_URL")

    # --------------------------------------------------------------------------
    # AUTH0 OAUTH2
    # --------------------------------------------------------------------------
    globs["AUTH0_OAUTH2_ENABLED"] = env("DD_SOCIAL_AUTH_AUTH0_OAUTH2_ENABLED")
    globs["SOCIAL_AUTH_AUTH0_KEY"] = env("DD_SOCIAL_AUTH_AUTH0_KEY")
    globs["SOCIAL_AUTH_AUTH0_SECRET"] = env("DD_SOCIAL_AUTH_AUTH0_SECRET")
    globs["SOCIAL_AUTH_AUTH0_DOMAIN"] = env("DD_SOCIAL_AUTH_AUTH0_DOMAIN")
    globs["SOCIAL_AUTH_AUTH0_SCOPE"] = env("DD_SOCIAL_AUTH_AUTH0_SCOPE")
    globs["SOCIAL_AUTH_TRAILING_SLASH"] = env("DD_SOCIAL_AUTH_TRAILING_SLASH")

    # --------------------------------------------------------------------------
    # GITLAB OAUTH2
    # --------------------------------------------------------------------------
    # Login only. The GitLab project auto-import from 2.58.4 wrote Product_Member /
    # Role rows, which are Pro-owned tables in 3.x, so it is not part of this port.
    globs["GITLAB_OAUTH2_ENABLED"] = env("DD_SOCIAL_AUTH_GITLAB_OAUTH2_ENABLED")
    globs["SOCIAL_AUTH_GITLAB_KEY"] = env("DD_SOCIAL_AUTH_GITLAB_KEY")
    globs["SOCIAL_AUTH_GITLAB_SECRET"] = env("DD_SOCIAL_AUTH_GITLAB_SECRET")
    globs["SOCIAL_AUTH_GITLAB_API_URL"] = env("DD_SOCIAL_AUTH_GITLAB_API_URL")
    globs["SOCIAL_AUTH_GITLAB_SCOPE"] = env("DD_SOCIAL_AUTH_GITLAB_SCOPE")

    # --------------------------------------------------------------------------
    # KEYCLOAK OAUTH2
    # --------------------------------------------------------------------------
    globs["KEYCLOAK_OAUTH2_ENABLED"] = env("DD_SOCIAL_AUTH_KEYCLOAK_OAUTH2_ENABLED")
    globs["SOCIAL_AUTH_KEYCLOAK_KEY"] = env("DD_SOCIAL_AUTH_KEYCLOAK_KEY")
    globs["SOCIAL_AUTH_KEYCLOAK_SECRET"] = env("DD_SOCIAL_AUTH_KEYCLOAK_SECRET")
    globs["SOCIAL_AUTH_KEYCLOAK_PUBLIC_KEY"] = env("DD_SOCIAL_AUTH_KEYCLOAK_PUBLIC_KEY")
    globs["SOCIAL_AUTH_KEYCLOAK_AUTHORIZATION_URL"] = env("DD_SOCIAL_AUTH_KEYCLOAK_AUTHORIZATION_URL")
    globs["SOCIAL_AUTH_KEYCLOAK_ACCESS_TOKEN_URL"] = env("DD_SOCIAL_AUTH_KEYCLOAK_ACCESS_TOKEN_URL")
    globs["SOCIAL_AUTH_KEYCLOAK_LOGIN_BUTTON_TEXT"] = env("DD_SOCIAL_AUTH_KEYCLOAK_LOGIN_BUTTON_TEXT")

    # --------------------------------------------------------------------------
    # GITHUB ENTERPRISE OAUTH2
    # --------------------------------------------------------------------------
    globs["GITHUB_ENTERPRISE_OAUTH2_ENABLED"] = env("DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_OAUTH2_ENABLED")
    globs["SOCIAL_AUTH_GITHUB_ENTERPRISE_URL"] = env("DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_URL")
    globs["SOCIAL_AUTH_GITHUB_ENTERPRISE_API_URL"] = env("DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_API_URL")
    globs["SOCIAL_AUTH_GITHUB_ENTERPRISE_KEY"] = env("DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_KEY")
    globs["SOCIAL_AUTH_GITHUB_ENTERPRISE_SECRET"] = env("DD_SOCIAL_AUTH_GITHUB_ENTERPRISE_SECRET")

    # --------------------------------------------------------------------------
    # SOCIAL AUTH EXCEPTION MESSAGES
    # --------------------------------------------------------------------------
    globs["SOCIAL_AUTH_EXCEPTION_MESSAGE_REQUEST_EXCEPTION"] = env("DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_REQUEST_EXCEPTION")
    globs["SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_CANCELED"] = env("DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_CANCELED")
    globs["SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_FAILED"] = env("DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_FAILED")
    globs["SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_FORBIDDEN"] = env("DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_FORBIDDEN")
    globs["SOCIAL_AUTH_EXCEPTION_MESSAGE_NONE_TYPE"] = env("DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_NONE_TYPE")
    globs["SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_TOKEN_ERROR"] = env("DD_SOCIAL_AUTH_EXCEPTION_MESSAGE_AUTH_TOKEN_ERROR")

    # --------------------------------------------------------------------------
    # INSTALLED_APPS
    # --------------------------------------------------------------------------
    globs["INSTALLED_APPS"] += ("social_django",)

    # --------------------------------------------------------------------------
    # MIDDLEWARE
    # --------------------------------------------------------------------------
    if isinstance(globs["MIDDLEWARE"], list):
        globs["MIDDLEWARE"].append("dojo.sso.middleware.CustomSocialAuthExceptionMiddleware")
    else:
        globs["MIDDLEWARE"] = [*globs["MIDDLEWARE"], "dojo.sso.middleware.CustomSocialAuthExceptionMiddleware"]

    # --------------------------------------------------------------------------
    # TEMPLATES - add SSO context processors and template dir
    # --------------------------------------------------------------------------
    # DIRS is the _DOJO_EXTRA_TEMPLATE_DIRS list, shared by reference with the
    # FilesystemLoader entry, so appending here is picked up at render time.
    context_processors = globs["TEMPLATES"][0]["OPTIONS"]["context_processors"]
    context_processors.append("social_django.context_processors.backends")
    context_processors.append("social_django.context_processors.login_redirect")
    context_processors.append("dojo.sso.context_processors.sso_context")
    globs["TEMPLATES"][0]["DIRS"].append(str(Path(__file__).parent / "templates"))
