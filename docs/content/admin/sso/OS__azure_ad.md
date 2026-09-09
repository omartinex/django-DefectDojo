---
title: "Azure Active Directory"
description: "Configure Azure AD / Entra ID SSO in Open-Source DefectDojo"
weight: 6
audience: opensource
---

Open-Source DefectDojo supports login via Azure Active Directory / Microsoft Entra ID.

{{% alert title="Group mapping is not available" color="warning" %}}
This build restores **login only**. Automatic User Group synchronisation from Entra —
the `DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_GET_GROUPS`, `..._GROUPS_FILTER` and
`..._CLEANUP_GROUPS` settings documented for DefectDojo 2.x — is **not** implemented, and
those environment variables have no effect. Group mapping depended on the `Dojo_Group` /
`Dojo_Group_Member` / `Role` models, which are no longer writable in the open-source
edition. Use [Authorized Users](/admin/user_management/os__authorized_users/) for access
control in the meantime.
{{% /alert %}}

You can connect to Entra ID either with this dedicated backend or with the generic
[OIDC](/admin/sso/os__oidc/) backend pointed at your tenant's v2.0 endpoint. The generic
OIDC route is the better default for a new setup; this one exists mainly for parity with
existing 2.x configurations.

## Prerequisites

Complete the following steps in the Azure portal before configuring DefectDojo:

1. [Register a new app](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app) in Microsoft Entra ID.

2. Note the following values from the registered app:
   - **Application (client) ID**
   - **Directory (tenant) ID**
   - Under **Certificates & Secrets**, create a new **Client Secret** and note its value

3. Under **Authentication > Redirect URIs**, add a **Web** type URI:
   `https://your-instance.example.com/complete/azuread-tenant-oauth2/`

## Configuration

Set the following as environment variables, or without the `DD_` prefix in your `local_settings.py` file (see [Configuration](/get_started/open_source/configuration/)):

{{< highlight python >}}
DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY=(str, 'YOUR_APPLICATION_ID'),
DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET=(str, 'YOUR_CLIENT_SECRET'),
DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID=(str, 'YOUR_DIRECTORY_ID'),
DD_SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_ENABLED=True
{{< /highlight >}}

Restart DefectDojo. A **Login with Azure AD** button will appear on the login page.

## Account creation

By default the first successful login creates a local account for the Entra user
(`DD_SOCIAL_AUTH_CREATE_USER=True`). Set it to `False` if accounts should be provisioned
up front instead, in which case users without an existing account are rejected.

New accounts are created with no product access. See
[Authorized Users](/admin/user_management/os__authorized_users/) for granting it.
