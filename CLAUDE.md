# Project Memory — OpenPosture (fork de DefectDojo) [NOMBRE PROVISORIO]

> ⚠️ "OpenPosture" es un codename interno de trabajo, no un nombre final. No usar en dominios,
> redes sociales, ni nada público. Mantenerlo aislado en una única constante de configuración
> (`PROJECT_NAME`) — nunca hardcodeado en strings, nombres de tablas, ni en el schema de DB —
> para que renombrar más adelante sea trivial. Antes de cualquier lanzamiento público, hacer una
> búsqueda formal de marca registrada.

## Identidad del proyecto
- Fork de `DefectDojo/django-DefectDojo`, licencia BSD 3-Clause (heredada, se mantiene el aviso
  de copyright original en LICENSE.md).
- **Sin afiliación con OWASP ni con DefectDojo Inc.** No usar su logo, ni el término "Dojo" en el
  branding público, ni sugerir soporte oficial o partnership.
- Objetivo del fork: recuperar y extender funcionalidad open-source que fue movida a la edición
  Pro, más features propias (ver Roadmap).

## Stack (verificado contra el repo — 2026-09-06)
- Backend: Django + Django REST Framework (app única `dojo`, `app_label = "dojo"`)
- Async/tareas: Celery, broker **Valkey** (drop-in de Redis, protocolo `redis://valkey:6379`).
  No es Redis a secas: el servicio en `docker-compose.yml` se llama `valkey`.
- DB: PostgreSQL (servicio `postgres`)
- Búsqueda: **`django-watson` 1.6.3** (full-text sobre Postgres). **No hay Elasticsearch** —
  si alguna vez se agrega, es feature nueva del fork, no algo que ya exista.
- Contenedores: Docker Compose. Contenedor de Django = `uwsgi`. App expuesta en
  `http://localhost:8080` vía `nginx`.

### Comandos exactos
Todos verificados leyendo los archivos citados. Si algo de acá falla, **corregir esta sección**
antes que improvisar un comando alternativo.

**Entorno local**
```bash
docker/setEnv.sh dev          # modo dev con hot-reload (linkea docker-compose.override.dev.yml)
docker compose build
docker compose up             # → http://localhost:8080
docker compose logs initializer | grep "Admin password:"   # credenciales de admin
docker compose exec uwsgi bash                             # shell en el contenedor Django
```
Modos de `docker/setEnv.sh`: `dev | unit_tests | unit_tests_cicd | integration_tests | release`.
Fuente: `readme-docs/DOCKER.md:88-104,144`.

**Tests unitarios**
```bash
# suite completa (deja el uwsgi arriba al terminar)
docker/setEnv.sh unit_tests && docker compose up

# un test case, contra el stack dev ya levantado
./run-unittest.sh --test-case unittests.tools.test_stackhawk_parser.TestStackHawkParser
./run-unittest.sh --test-case unittests.<modulo> -f          # -f = --failfast

# dentro del contenedor
python manage.py test unittests --keepdb
python manage.py test unittests.<modulo>.<Clase>.<metodo> --keepdb
```
Fuente: `readme-docs/DOCKER.md:297-340`, `run-unittest.sh:69`.
En CI la suite se parte en 3 pasadas por tags (`--exclude-tag=non-parallel/transactional/performance`,
luego cada tag por separado) — `docker/entrypoint-unit-tests.sh:142-152`.

**Tests de integración (UI/Selenium) y API**
```bash
./run-integration-test-dev.sh <archivo_de_test>   # contra el stack dev levantado
./run-integration-tests.sh                        # suite completa, levanta su propio stack
```
Fuente: `run-integration-test-dev.sh:13-16`, `run-integration-tests.sh:51-58`.

**Lint / format**
```bash
pip install -r requirements-lint.txt   # ruff==0.16.0
ruff check .                           # en CI: ruff check --output-format=github .
```
**Ruff corre en el host, NO dentro del contenedor `uwsgi`** (no está instalado ahí).
Es gate bloqueante de `unit-tests.yml` — si ruff falla, no corre ningún test.
Fuente: `.github/workflows/ruff.yml:36,39`, `ruff.toml`, `requirements-lint.txt`.

**Migraciones**
```bash
docker compose exec uwsgi python manage.py migrate
docker compose exec uwsgi python manage.py makemigrations --no-input --check --dry-run --verbosity 3
docker compose exec uwsgi python manage.py check
python3 scripts/check_migration_leaves.py    # el grafo debe tener una sola hoja
```
`makemigrations --check` debe decir "No changes detected" antes de cualquier commit que toque
modelos. Fuente: `docker/entrypoint-unit-tests.sh:87,118`, `.github/workflows/migration-graph.yml:51`.

### `AGENTS.md` (de upstream) — qué aplica y qué no
La raíz trae un `AGENTS.md` de upstream (~465 líneas). **Sí aplica** lo técnico: playbook de
reorganización modular (`dojo/{module}/{models,services,ui/,api/}`), convenciones de re-exports
backward-compat, reglas de ruff, y los gates de verificación.
**NO aplica al fork**: las reglas de PR/milestone contra `DefectDojo/django-DefectDojo`, y el
esquema de ramas `dev`/`bugfix`/`master` (ver abajo).

## Remotes de git
- `origin` → `https://github.com/omartinex/django-DefectDojo` (tu fork)
- `upstream` → `https://github.com/DefectDojo/django-DefectDojo` (para sync periódico)
- **Rama principal: `master`** (no `main` — heredado del repo original de DefectDojo). Cualquier
  agente que abra este repo debe asumir `master` como base para ramas nuevas y para el sync con
  upstream.
- **Este fork solo tiene `origin/master`.** `dev` y `bugfix` existen únicamente en `upstream`.
  Por eso el `SessionStart` hook avisa "contiene ni origin/bugfix ni origin/dev" en toda rama
  nueva: es un falso positivo heredado del flujo de release de upstream, no una rama mal cortada.
  Lo mismo con `.claude/hooks/branch-guard.sh`, que bloquea escrituras estando en `master` —
  eso sí aplica, trabajar siempre en una rama de feature.

## Roadmap / Tracks activos
1. **[ACTIVO] SSO revival** — Recuperar soporte de SAML/OIDC (específicamente login vía Azure
   Entra ID) que existía en DefectDojo 2.x y fue removido/movido a Pro en 3.0.
   - Branch: `feature/sso-revival`
   - Criterio de aceptación: un usuario de Entra ID puede loguearse por OIDC, el mapeo de grupos
     funciona, y la suite de tests completa sigue en verde.
   - Restricción: NO tocar archivos de `/infra` o `/terraform` en este track (evitar conflictos
     con el track de infraestructura que corre en paralelo).

   #### Inventario de remoción (arqueología hecha 2026-09-06 — no repetirla)
   - **Tag base para el port: `2.58.4`** (último de la serie 2.x; el siguiente es `3.0.0`).
   - **Commit de remoción: `952a56d13f`** — *"Tailwind UI rebuild, legacy authorization, OS
     surface removals (#14865)"*, Greg Anderson, 2026-05-14. Padre `db1932c9ec`; primer tag que
     lo contiene: `3.0.0`. Es un commit gigante (689 archivos, +48989/−18293) que mezcla el
     rebuild de Tailwind con el traspaso de autorización a Pro; **el subconjunto SSO son 40
     archivos, ~2281 borrados**. No hubo remoción parcial previa ni cleanup posterior: todo lo
     que toca rutas `sso` después es `docs/` (traducciones y docs de Pro).
     Ver el diff acotado con:
     `git show 952a56d13f -- dojo/sso dojo/settings/settings.dist.py dojo/urls.py requirements.txt`

   - **Paquete `dojo/sso/` borrado entero (1182 líneas):** `settings.py` (455, `SSO_ENV_SCHEMA` +
     `apply_sso_settings()`), `attribute_maps/saml_uri.py` (243), `pipeline.py` (188, incluye
     `assign_user_to_groups` y el sync de grupos AzureAD), `remote_user.py` (110),
     `templates/dojo/sso_login_buttons.html` (56), `views.py` (43), `middleware.py` (35),
     `context_processors.py` (23), `urls.py` (10), `attribute_maps/django_saml_uri.py` (19).

   - **Puntos de enganche — lo más importante:** en 2.58.4 `dojo/sso/` ya era un **módulo
     opcional enchufable**, cargado con `try/except ImportError` en solo 3 lugares:
     `settings.dist.py:39-43` (merge de `SSO_ENV_SCHEMA` en el `environ.FileAwareEnv`),
     `settings.dist.py:814-818` (`apply_sso_settings(env, globals())`), y `dojo/urls.py`
     (`from dojo.sso.urls import urlpatterns as sso_urlpatterns`). Más `SHOW_LOGIN_FORM` /
     `SOCIAL_LOGIN_AUTO_REDIRECT`, el logger `saml2`, y `dojo/templates/dojo/login.html`
     (reescrito a Tailwind en el mismo commit → no se puede copiar tal cual).
     **Consecuencia: el port es restaurar un paquete autocontenido + 3 hooks + 3 deps, no
     cirugía dispersa.** Es la mejor forma posible de minimizar conflictos de sync.

   - **Deps eliminadas de `requirements.txt`:** `social-auth-app-django==5.8.0`,
     `social-auth-core==4.8.7`, `djangosaml2==1.12.0`.
   - **Test borrado:** `unittests/test_social_auth_failure_handling.py` (153 líneas).
   - **Docs OS borradas:** `docs/content/admin/sso/OS__*.md` (saml, oidc, azure_ad, google, okta,
     keycloak, gitlab, auth0, github_enterprise, remote_user). Solo quedan los `PRO__*.md`.
   - **Colateral del mismo commit:** `dojo/group/` completo, 8 viewsets de la API desregistrados
     en `dojo/urls.py` (`dojo_groups`, `dojo_group_members`, `global_roles`, `product_members`,
     `product_groups`, `roles`, …), y recortes en `dojo/user/{queries,views,urls}.py`.

   #### Entrega 1 — login OIDC (opción A) — HECHA
   Decisiones tomadas con el dueño del repo, **no relitigar**:
   - **Opción A**: login primero, mapeo de grupos en una segunda entrega.
   - **Los 8 backends OAuth** de 2.58.4 (OIDC, AzureAD tenant, Google, Okta, Auth0, GitLab,
     Keycloak, GitHub Enterprise). **Sin SAML, sin REMOTE_USER** (`djangosaml2` no se
     reintrodujo; `xmlsec1` igual sigue en los Dockerfiles si algún día hace falta).
   - **Verificación**: unit tests + validación manual contra un tenant real de Entra.
     Sin IdP local en docker-compose.

   Lo que se restauró: paquete `dojo/sso/` (settings, pipeline, middleware,
   context_processors, urls, views, 2 templates de botones), las 2 deps de social-auth,
   `unittests/test_social_auth_failure_handling.py` + `unittests/test_sso_settings.py`,
   y `docs/content/admin/sso/OS__{oidc,azure_ad}.md`.

   **⚠️ NO se pueden usar los pines de 2.58.4.** `social-auth-core==4.8.7` declara
   `Requires-Dist: PyJWT[crypto]==2.12.1` — un pin **exacto**, y HEAD tiene `PyJWT==2.13.0`.
   El build muere con `ResolutionImpossible`. No es casualidad: el mismo commit `952a56d13f`
   que borró SSO subió PyJWT de 2.12.1 a 2.13.0 — el bump lo **habilitó** sacar social-auth.
   El fork usa **`social-auth-core==5.1.0` + `social-auth-app-django==6.0.1`**, que piden
   `PyJWT>=2.13.0` y por lo tanto están alineados con HEAD (también `cryptography>=46.0.7`
   y `requests>=2.34.0`, ambos satisfechos). Verificado que los 8 backends, las 6 funciones
   del pipeline, las 4 excepciones y toda la superficie de `social_django` que usamos siguen
   existiendo en 5.x/6.x con firmas compatibles.

   **Dos trampas del port que NO están en 2.58.4** (si se ignoran, compila y falla en runtime):
   1. `MIDDLEWARE` se **re-liga** (`MIDDLEWARE = [...]`, no `.append`) cuatro veces después de
      definirse en `settings.dist.py` — la última en el bloque de `DJANGO_DEBUG_TOOLBAR_ENABLED`.
      Por eso `_apply_sso_settings(env, globals())` va **al final del archivo**. En la posición
      de 2.58.4 (línea 814) el `CustomSocialAuthExceptionMiddleware` se perdía en silencio.
      El test `test_exception_middleware_survived_the_middleware_rebinding` cubre esto.
   2. Hay **dos árboles de templates** (`dojo/templates/` y `dojo/templates_classic/`,
      resueltos por `UIPreferenceLoader` en `dojo/template_loaders.py`). Los botones tienen dos
      variantes, ambas dentro de `dojo/sso/templates/dojo/`, y cada `login.html` incluye la suya.
   Además: `SHOW_LOGIN_FORM` se expone desde `dojo/sso/context_processors.py` y no desde
   `dojo/context_processors.py` como en 2.58.4, para no tocar otro archivo de upstream.

   #### 🚧 Entrega 2 — DECISIÓN PENDIENTE: el mapeo de grupos
   El pipeline de 2.58.4 mapea grupos de Entra vía `Dojo_Group` / `Dojo_Group_Member` / `Role`
   (`sso/pipeline.py:104-125`). En 3.x esos ocho modelos RBAC viven en
   `dojo/authorization/models.py` como **shells `managed=False`** cuyas tablas son propiedad de
   Pro (migración `dojo/db_migrations/0268_release_authorization_to_pro.py`).
   A favor: 0268 hace el flip con `SeparateDatabaseAndState` y **solo `state_operations`**, así
   que **las tablas físicas siguen existiendo** (creadas por 0102/0109/0112) — no se dropearon.
   En contra: OS volvió al modelo legacy (`Product.authorized_users` / `Product_Type.authorized_users`
   + `is_superuser`/`is_staff`) y 0268 removió `System_Settings.default_group`,
   `default_group_role` y `default_group_email_pattern`, que el pipeline usaba.

   Las funciones que quedaron **fuera** de la entrega 1 por esto (están en
   `git show 2.58.4:dojo/sso/pipeline.py` si hay que recuperarlas): `update_azure_groups`,
   `assign_user_to_groups`, `cleanup_old_groups_for_user`, y `update_product_access`
   (el auto-import de proyectos de GitLab, que es el mismo problema con otro nombre: escribe
   `Product_Member` + `Role`). El test `test_pipeline_excludes_deferred_rbac_steps` falla si
   alguna vuelve al pipeline sin resolver esto.

   Opciones sobre la mesa (**sin decidir — no elegir una sin confirmar con el dueño del repo**):
   - **(B)** Revivir `Dojo_Group` + `Dojo_Group_Member` como `managed=True` en el fork.
     Divergencia fuerte con upstream → conflicto garantizado en cada sync.
   - **(C)** Mapear grupos de Entra al modelo legacy que OS sí conserva (`authorized_users` +
     `is_staff`/`is_superuser`), sin resucitar RBAC.
2. **[PENDIENTE] Infraestructura Terraform** — Módulo para desplegar en ECS Fargate + RDS
   (Postgres) + ElastiCache (Redis) + Elasticsearch/OpenSearch.
   - Branch: `feature/terraform-ecs`
   - Vive en `/infra`, no debe tocar código Python de la aplicación.
3. **[PENDIENTE] Triage asistido (estilo Sensei)** — Enriquecimiento de hallazgos vía LLM
   (dedupe, contexto CVE/EPSS, sugerencias de remediación). Arranca después de validar el loop
   en los tracks 1 y 2.

## Convenciones de trabajo (loop agéntico)
Para cada tarea, seguir siempre: **plan → implementar → verificar (tests + lint) → reflexionar
si falla → commit solo en verde.** No hacer commit sin que la suite de tests релевante pase.

## Sync con upstream
- Cadencia: revisar releases de upstream DefectDojo en cada versión nueva.
- Zona de conflicto recurrente esperada — **son exactamente los 6 archivos de upstream que el
  fork toca para el SSO**; el resto vive en `dojo/sso/`, que upstream no tiene:
  `dojo/settings/settings.dist.py` (no `dojo/settings.py`), `dojo/urls.py`,
  `dojo/user/ui/views.py`, `dojo/templates/dojo/login.html`,
  `dojo/templates_classic/dojo/login.html` y `requirements.txt`.
  (No existe `dojo/user_auth/`.)
  Upstream tiende a remover/mover esto a Pro en cada major release. Documentar cada resolución de
  conflicto en `docs/upstream-sync-log.md` (crear si no existe).
