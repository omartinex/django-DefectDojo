"""
Wiring tests for the SSO module (`dojo/sso/`).

These assert the things `manage.py check` does not: that
`dojo.sso.settings.apply_sso_settings` actually landed its mutations on the final
settings, that the URLs are registered, and that the login templates render the provider
buttons. Several of these guard specific regressions that are silent at import time.
"""

from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from dojo.models import Dojo_User
from dojo.sso.views import get_sso_auto_redirect

from .dojo_test_case import DojoTestCase, versioned_fixtures

EXPECTED_BACKENDS = (
    "social_core.backends.open_id_connect.OpenIdConnectAuth",
    "social_core.backends.auth0.Auth0OAuth2",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.okta.OktaOAuth2",
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
    "social_core.backends.gitlab.GitLabOAuth2",
    "social_core.backends.keycloak.KeycloakOAuth2",
    "social_core.backends.github_enterprise.GithubEnterpriseOAuth2",
)

# Pipeline steps that write to the RBAC tables Pro owns since
# dojo.0268_release_authorization_to_pro. Deferred to the group-mapping deliverable;
# if one reappears here it will fail at runtime against a managed=False model.
DEFERRED_PIPELINE_STEPS = (
    "dojo.sso.pipeline.update_azure_groups",
    "dojo.sso.pipeline.update_product_access",
    "dojo.sso.pipeline.modify_permissions",
)


class TestSSOSettingsWiring(DojoTestCase):

    def test_all_eight_oauth_backends_are_installed(self):
        for backend in EXPECTED_BACKENDS:
            with self.subTest(backend=backend):
                self.assertIn(backend, settings.AUTHENTICATION_BACKENDS)

    def test_model_backend_stays_last(self):
        """Local username/password auth must remain the fallback, tried after the IdPs."""
        self.assertEqual(
            settings.AUTHENTICATION_BACKENDS[-1],
            "django.contrib.auth.backends.ModelBackend",
        )

    def test_social_django_app_installed(self):
        self.assertIn("social_django", settings.INSTALLED_APPS)

    def test_exception_middleware_survived_the_middleware_rebinding(self):
        """
        Regression guard for the port's main hazard.

        settings.dist.py rebinds MIDDLEWARE (MIDDLEWARE = [...]) several times after it is
        first defined, so apply_sso_settings has to run at the very end of that file.
        Called any earlier, this middleware is silently dropped and social-auth failures
        render a 500 instead of redirecting back to the login form.
        """
        self.assertIn(
            "dojo.sso.middleware.CustomSocialAuthExceptionMiddleware",
            settings.MIDDLEWARE,
        )

    def test_sso_context_processor_registered(self):
        self.assertIn(
            "dojo.sso.context_processors.sso_context",
            settings.TEMPLATES[0]["OPTIONS"]["context_processors"],
        )

    def test_sso_template_dir_registered(self):
        self.assertTrue(
            any(str(d).endswith("dojo/sso/templates") for d in settings.TEMPLATES[0]["DIRS"]),
            f"dojo/sso/templates missing from TEMPLATES[0]['DIRS']: {settings.TEMPLATES[0]['DIRS']}",
        )

    def test_social_urls_are_registered(self):
        self.assertEqual(reverse("social:begin", args=["oidc"]), "/login/oidc/")
        self.assertEqual(reverse("social:complete", args=["oidc"]), "/complete/oidc/")

    def test_pipeline_excludes_deferred_rbac_steps(self):
        for step in DEFERRED_PIPELINE_STEPS:
            with self.subTest(step=step):
                self.assertNotIn(step, settings.SOCIAL_AUTH_PIPELINE)

    def test_pipeline_creates_users_through_dojo_step(self):
        """The username-sanitising create_user must run, not social-core's stock one."""
        self.assertIn("dojo.sso.pipeline.create_user", settings.SOCIAL_AUTH_PIPELINE)
        self.assertNotIn("social_core.pipeline.user.create_user", settings.SOCIAL_AUTH_PIPELINE)

    def test_every_provider_is_disabled_by_default(self):
        """With no DD_SOCIAL_AUTH_* env vars set, behaviour must match a build without SSO."""
        for flag in (
            "OIDC_AUTH_ENABLED",
            "AZUREAD_TENANT_OAUTH2_ENABLED",
            "GOOGLE_OAUTH_ENABLED",
            "OKTA_OAUTH_ENABLED",
            "AUTH0_OAUTH2_ENABLED",
            "GITLAB_OAUTH2_ENABLED",
            "KEYCLOAK_OAUTH2_ENABLED",
            "GITHUB_ENTERPRISE_OAUTH2_ENABLED",
        ):
            with self.subTest(flag=flag):
                self.assertFalse(getattr(settings, flag))


class TestSSOLoginPageRendering(DojoTestCase):

    def test_login_page_has_no_sso_buttons_when_all_providers_disabled(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "/login/oidc/")

    @override_settings(OIDC_AUTH_ENABLED=True, SOCIAL_AUTH_OIDC_LOGIN_BUTTON_TEXT="Login with OIDC")
    def test_oidc_button_renders_on_login_page(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/login/oidc/")
        self.assertContains(response, "Login with OIDC")

    @override_settings(OIDC_AUTH_ENABLED=True)
    def test_local_login_form_still_renders_alongside_sso(self):
        """SSO must be additive: the username/password form stays unless explicitly hidden."""
        response = self.client.get("/login")
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    @override_settings(OIDC_AUTH_ENABLED=True, SHOW_LOGIN_FORM=False)
    def test_local_login_form_hidden_when_show_login_form_is_false(self):
        response = self.client.get("/login")
        self.assertNotContains(response, 'name="password"')

    @override_settings(OIDC_AUTH_ENABLED=True, SHOW_LOGIN_FORM=False)
    def test_force_login_form_brings_back_the_local_form(self):
        """The escape hatch: without it an IdP outage locks every user out."""
        response = self.client.get("/login?force_login_form")
        self.assertContains(response, 'name="password"')


class TestSSOAutoRedirect(DojoTestCase):

    def _get(self, path="/login"):
        return self.client.get(path).wsgi_request

    def test_no_redirect_while_the_login_form_is_shown(self):
        self.assertIsNone(get_sso_auto_redirect(self._get()))

    @override_settings(SHOW_LOGIN_FORM=False, SOCIAL_LOGIN_AUTO_REDIRECT=False, OIDC_AUTH_ENABLED=True)
    def test_no_redirect_when_auto_redirect_is_off(self):
        self.assertIsNone(get_sso_auto_redirect(self._get()))

    @override_settings(SHOW_LOGIN_FORM=False, SOCIAL_LOGIN_AUTO_REDIRECT=True)
    def test_no_redirect_when_no_provider_is_enabled(self):
        self.assertIsNone(get_sso_auto_redirect(self._get()))

    @override_settings(
        SHOW_LOGIN_FORM=False,
        SOCIAL_LOGIN_AUTO_REDIRECT=True,
        OIDC_AUTH_ENABLED=True,
        AZUREAD_TENANT_OAUTH2_ENABLED=True,
    )
    def test_no_redirect_when_two_providers_are_enabled(self):
        """With more than one provider there is no unambiguous target; show the buttons."""
        self.assertIsNone(get_sso_auto_redirect(self._get()))

    @override_settings(SHOW_LOGIN_FORM=False, SOCIAL_LOGIN_AUTO_REDIRECT=True, OIDC_AUTH_ENABLED=True)
    def test_redirects_to_the_single_enabled_provider(self):
        response = get_sso_auto_redirect(self._get())
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/oidc/?next=%2Fdashboard")

    @override_settings(SHOW_LOGIN_FORM=False, SOCIAL_LOGIN_AUTO_REDIRECT=True, OIDC_AUTH_ENABLED=True)
    def test_next_parameter_is_carried_through_the_redirect(self):
        response = get_sso_auto_redirect(self._get("/login?next=/product"))
        self.assertEqual(response.url, "/login/oidc/?next=%2Fproduct")

    @override_settings(SHOW_LOGIN_FORM=False, SOCIAL_LOGIN_AUTO_REDIRECT=True, OIDC_AUTH_ENABLED=True)
    def test_force_login_form_defeats_the_auto_redirect(self):
        self.assertIsNone(get_sso_auto_redirect(self._get("/login?force_login_form")))


@versioned_fixtures
class TestSSOLogoutBehaviour(DojoTestCase):

    """
    Logout needs an authenticated session: LoginRequiredMiddleware intercepts /logout for
    anonymous users and redirects to /login before logout_view is ever reached.
    """

    fixtures = ["dojo_testdata.json"]

    def setUp(self):
        super().setUp()
        self.client.force_login(Dojo_User.objects.get(username="admin"))

    @override_settings(SHOW_LOGIN_FORM=False, SOCIAL_LOGIN_AUTO_REDIRECT=True, OIDC_AUTH_ENABLED=True)
    def test_logout_bounces_back_to_the_idp(self):
        """
        Documents inherited 2.58.4 behaviour rather than endorsing it.

        With the form hidden AND auto-redirect on, logout_view() renders login_view(),
        which redirects straight back to the provider — so logging out of DefectDojo alone
        is not possible; the IdP session has to end too.
        """
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith("/login/oidc/"),
            f"expected a redirect to the IdP, got {response.url}",
        )

    @override_settings(SHOW_LOGIN_FORM=False, SOCIAL_LOGIN_AUTO_REDIRECT=True, OIDC_AUTH_ENABLED=True)
    def test_logout_with_force_login_form_stays_on_the_login_page(self):
        """The escape hatch from the behaviour above."""
        response = self.client.get("/logout?force_login_form")
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_to_login_normally(self):
        """Default config (form shown): unchanged from before the SSO port."""
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")
