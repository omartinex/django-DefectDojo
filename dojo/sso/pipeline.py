"""
social-auth pipeline steps.

Ported from DefectDojo 2.58.4 (`dojo/sso/pipeline.py`), trimmed to the login-only scope
of this port. The four functions that mapped IdP groups onto DefectDojo's RBAC models
(`update_azure_groups`, `assign_user_to_groups`, `cleanup_old_groups_for_user`) and the
GitLab project auto-import (`update_product_access`) were left out: they write to
``Dojo_Group``, ``Dojo_Group_Member``, ``Product_Member`` and ``Role``, which since
``dojo.0268_release_authorization_to_pro`` are ``managed=False`` shells whose tables
belong to the Pro edition. Group mapping is a separate deliverable.
"""

import re

import social_core.pipeline.user
from django.conf import settings
from social_core.backends.azuread_tenant import AzureADTenantOAuth2
from social_core.backends.google import GoogleOAuth2


def social_uid(backend, details, response, *args, **kwargs):
    if settings.AZUREAD_TENANT_OAUTH2_ENABLED and isinstance(backend, AzureADTenantOAuth2):
        """Return user details from Azure AD account"""
        fullname, first_name, last_name, upn = (
            response.get("name", ""),
            response.get("given_name", ""),
            response.get("family_name", ""),
            response.get("upn"),
        )
        uid = backend.get_user_id(details, response)
        return {"username": upn,
                "email": upn,
                "fullname": fullname,
                "first_name": first_name,
                "last_name": last_name,
                "uid": uid}
    if settings.GOOGLE_OAUTH_ENABLED and isinstance(backend, GoogleOAuth2):
        """Return user details from Google account"""
        if "sub" in response:
            google_uid = response["sub"]
        elif "email" in response:
            google_uid = response["email"]
        else:
            google_uid = response["id"]
        fullname, first_name, last_name, email = (
            response.get("fullname", ""),
            response.get("first_name", ""),
            response.get("last_name", ""),
            response.get("email"),
        )
        return {"username": email,
                "email": email,
                "fullname": fullname,
                "first_name": first_name,
                "last_name": last_name,
                "uid": google_uid}
    uid = backend.get_user_id(details, response)
    # Used for most backends
    if uid:
        return {"uid": uid}
    # Until OKTA PR in social-core is merged
    # This modified way needs to work
    return {"uid": response.get("preferred_username")}


def sanitize_username(username):
    allowed_chars_regex = re.compile(r"[\w@.+_-]")
    allowed_chars = filter(allowed_chars_regex.match, list(username))
    return "".join(allowed_chars)


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if not settings.SOCIAL_AUTH_CREATE_USER:
        return None
    username = details.get(settings.SOCIAL_AUTH_CREATE_USER_MAPPING)
    details["username"] = sanitize_username(username)
    return social_core.pipeline.user.create_user(strategy, details, backend, user, args, kwargs)
