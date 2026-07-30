# GastroFlow — Fase 1: Fundación

## Hoja de ruta oficial

| Fase | Nombre | Alcance |
| --- | --- | --- |
| 1 | Fundación | Arquitectura, base de datos, autenticación y panel de administración. |
| 2 | MVP | Menú digital, pedidos, reservas y códigos QR. |
| 3 | Comercialización | Multiempresa (SaaS), suscripciones, paneles por negocio y despliegue en la nube. |
| 4 | Escalabilidad | Analítica, fidelización, integraciones, IA y aplicación móvil. |

Las decisiones de cada fase deben habilitar las siguientes, sin adelantar funcionalidades que aún no correspondan.

## Alcance acordado

Esta fase construye el núcleo operativo sobre el que se montarán el menú, pedidos y cocina:

1. Estructura modular del proyecto Flask.
2. Base de datos y migraciones preparadas para evolucionar a SaaS.
3. Autenticación, sesiones seguras, JWT y roles.
4. Panel de administración inicial protegido por permisos.

No incluye todavía catálogo, mesas, pedidos, QR ni reservas. Tampoco implementa aún la operación multiempresa, suscripciones ni paneles por negocio: eso corresponde a la fase 3. La estructura de datos conservará una entidad de negocio para que esa evolución no exija rediseñar la base.

## Decisiones de base

- **Flask con application factory y Blueprints**: permite separar módulos sin acoplar el inicio de la aplicación.
- **SQLAlchemy + Flask-Migrate**: misma capa de datos para SQLite local y PostgreSQL en producción.
- **Preparación SaaS**: la entidad de negocio (`Tenant`) permite incorporar aislamiento por empresa en la fase 3 sin migraciones disruptivas.
- **Autenticación híbrida**: sesiones protegidas para el panel y JWT para las futuras APIs.
- **Roles iniciales**: administrador general, administrador del restaurante, gerente, mozo, cocinero y cajero.

## Entidades creadas en esta fase

```text
Tenant 1 ── * User * ── * Role
Tenant 1 ── * AuditLog
```

- `Tenant`: empresa gastronómica, identificada por un `slug` único.
- `User`: persona que opera la plataforma; tiene hash de contraseña y estado activo/inactivo.
- `Role`: conjunto de permisos de operación.
- `AuditLog`: registro de actividades sensibles por empresa.

## Resultado esperado

El administrador podrá iniciar sesión y ver un panel de administración base. Durante esta fase se trabajará con un negocio de referencia; el alta autoservicio de restaurantes, la administración de múltiples negocios y sus paneles aislados se incorporarán en la fase 3.

## Criterio de cierre

- La aplicación inicia con configuración por entorno.
- La primera migración crea las tablas base.
- Se puede crear un usuario administrador inicial con un comando.
- Login, logout y protección de rutas funcionan.
- El panel administra accesos según el rol.
