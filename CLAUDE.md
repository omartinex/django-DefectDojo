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

## Stack (a confirmar/completar por el agente en la primera exploración)
- Backend: Django + Django REST Framework
- Async/tareas: Celery + Redis
- DB: PostgreSQL
- Búsqueda: Elasticsearch
- Contenedores: Docker / docker-compose
- [ ] TODO: el primer agente que trabaje en este repo debe correr una exploración completa y
      completar aquí: comandos exactos para tests, lint, migraciones, y levantar el entorno local.

## Remotes de git
- `origin` → `https://github.com/omartinex/django-DefectDojo` (tu fork)
- `upstream` → `https://github.com/DefectDojo/django-DefectDojo` (para sync periódico)
- **Rama principal: `master`** (no `main` — heredado del repo original de DefectDojo). Cualquier
  agente que abra este repo debe asumir `master` como base para ramas nuevas y para el sync con
  upstream.

## Roadmap / Tracks activos
1. **[ACTIVO] SSO revival** — Recuperar soporte de SAML/OIDC (específicamente login vía Azure
   Entra ID) que existía en DefectDojo 2.x y fue removido/movido a Pro en 3.0.
   - Branch: `feature/sso-revival`
   - Criterio de aceptación: un usuario de Entra ID puede loguearse por OIDC, el mapeo de grupos
     funciona, y la suite de tests completa sigue en verde.
   - Restricción: NO tocar archivos de `/infra` o `/terraform` en este track (evitar conflictos
     con el track de infraestructura que corre en paralelo).
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
- El área de autenticación (`dojo/settings.py` secciones SAML/OIDC, `dojo/user_auth/` o
  equivalente) es zona de conflicto recurrente esperada — upstream tiende a remover/mover esto
  a Pro en cada major release. Documentar cada resolución de conflicto en
  `docs/upstream-sync-log.md` (crear si no existe).
