---
title: "Single Sign-On"
description: "DefectDojo Pro supports SAML and a range of OAuth providers for Single Sign-On"
summary: ""
date: 2023-09-07T16:06:50+02:00
lastmod: 2026-04-30T00:00:00+00:00
draft: false
weight: 8
collapsed: true
chapter: true
seo:
  title: ""
  description: ""
  canonical: ""
  robots: ""
exclude_search: true
pro-feature: true
aliases:
  - "/en/customize_dojo/user_management/configure_sso/"
  - /admin/user_management/configure_sso/
  - /admin/sso/os__saml/
  - /admin/sso/os__auth0/
  - /admin/sso/os__github_enterprise/
  - /admin/sso/os__gitlab/
  - /admin/sso/os__google/
  - /admin/sso/os__keycloak/
  - /admin/sso/os__okta/
  - /admin/sso/os__remote_user/
---

Upstream DefectDojo moved the whole SSO surface to DefectDojo Pro in 3.0. This build restores part of it: **OAuth2/OIDC login** works in the open-source edition, covering [OIDC](/admin/sso/os__oidc/) (the recommended route for Microsoft Entra ID) and [Azure Active Directory](/admin/sso/os__azure_ad/), plus the Google, Okta, Auth0, GitLab, Keycloak and GitHub Enterprise backends.

Two things from DefectDojo 2.x are **not** restored:

- **SAML and REMOTE_USER.** Neither is available; only the OAuth2/OIDC backends are.
- **Group mapping.** Identity-provider groups are not mapped onto DefectDojo User Groups, so the `..._GET_GROUPS`, `..._GROUPS_FILTER` and `..._CLEANUP_GROUPS` settings have no effect. Access control is via [Authorized Users](/admin/user_management/os__authorized_users/).

Users are matched by username, and by default a first successful login creates the local account (`DD_SOCIAL_AUTH_CREATE_USER`). New accounts start with no product access.

## Seeing what is configured

**[Authorization Connectors](/admin/sso/pro__authorization_connectors/)** lists every supported provider on one page — which are configured, which are enabled, and what protocol each speaks — and takes you straight to the settings form for any of them. Start there if you want to know the state of this instance rather than set up a specific provider.

## Supported SSO providers (DefectDojo Pro)

DefectDojo Pro supports SAML and the following OAuth providers. Each guide walks through the provider-side setup and the corresponding configuration in the Pro **Enterprise Settings** UI.

* **[Auth0](/admin/sso/pro__auth0/)**
* **[Azure Active Directory](/admin/sso/pro__azure_ad/)**
* **[GitHub Enterprise](/admin/sso/pro__github_enterprise/)**
* **[GitLab](/admin/sso/pro__gitlab/)**
* **[Google](/admin/sso/pro__google/)**
* **[KeyCloak](/admin/sso/pro__keycloak/)**
* **[Okta](/admin/sso/pro__okta/)**
* **[OIDC (OpenID Connect)](/admin/sso/pro__oidc/)**
* **[SAML](/admin/sso/pro__saml/)**
* **[LDAP](/admin/sso/pro__ldap/)**

## Provisioning users from your directory (DefectDojo Pro)

The providers above decide who may sign in. **[SCIM Provisioning](/admin/sso/pro__scim/)** keeps the account list itself in step with your directory, so users are created when they join, updated when their details change, and deactivated (along with their API tokens) when they leave.

SSO configuration in DefectDojo Pro can only be performed by a **Superuser**.

**DefectDojo Pro users:** Add the IP addresses of your SAML or SSO services to the Firewall whitelist before setting up SSO. See [Firewall Rules](/get_started/pro/cloud/using-cloud-manager/#changing-your-firewall-settings) for more information.

## Disabling Username / Password login

Once SSO is configured in DefectDojo Pro, you may want to disable the traditional username/password login form. Uncheck **Allow Login via Username and Password** under **Enterprise Settings > Login Settings**.

![image](images/pro_login_settings.png)

### Login fallback

If your SSO integration stops working, you can always return to the standard login form by appending the following to your DefectDojo URL:

`/login?force_login_form`

We recommend keeping at least one admin account with a username and password configured as a fallback.
