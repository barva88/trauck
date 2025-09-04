Objetivo principal del proyecto

Trauck es un sistema tipo TMS (Transportation Management System) enfocado en carriers pequeños (menos de 5 camiones).

El producto central es un Dashboard en el dominio dashboard.trauck.com que permita a los carriers gestionar sus cargas, rutas y comunicación con clientes y despachadores. El enfoque principal de Trauck es optimizar rutas y automatizar el trabajo del dispatcher con IA, el usuario busca y gestiona  las cargas a traves de una comunicacion via WhatsApp, llamada o mensajeria con un agente AI de Retell AI. el dashboard es para que el usuario lleve todo el control de su gestion con esta herramienta. Ejemplo: El procesamiento de cobro a los shippers, la generacion de la documentacion, que el usuario tenga acceso a ver el uso del agente por ejemplo las comunaciones que ha tenido(el historial con fecha, resumen, y convesacion). Tambien el dasboard es para gestionar la autenticacion y registro de usuarios por lo que retell obtiene la infomacion de los usuarios, el usuario en la primera version del producto solo va a utilizar el modulo de education donde podra prepararse para elexamen de cdl

El dominio trauck.com solo tendrá una landing page (otro repo).

El objetivo clave del sistema: optimizar rutas y automatizar el trabajo del dispatcher con IA, cargas y comunicación.

Lineamientos de diseño

Tema base: Black Dashboard (Creative Tim).

Estilo visual: oscuro, minimalista, moderno y profesional.

Paleta de colores oficial de Trauck:

Primario: azul oscuro con acentos teal.

Secundario: gris oscuro/neutro.

Complemento: un toque de rosa/fucsia (detalles en botones/hover).

Tipografía: clara, legible y consistente en todas las vistas.

La UI debe ser responsive (desktop, tablet, móvil).

Sidebar fijo con secciones principales: Dashboard, Cargas, Conversaciones, Mi Perfil, Facturación y Pagos, Notificaciones, Soporte, Configuración.

Buenas prácticas y profesionalismo

Cada vez que generes/modifiques código:

Incluye pruebas unitarias y de integración básicas.

Asegúrate de que las migraciones de Django estén generadas y aplicables sin romper datos.

Documenta cambios en el README.md (siempre que afecten la configuración o el flujo del sistema).

Usa variables de entorno (.env) para todas las credenciales y secrets.

Aplica validaciones de seguridad (CSRF, HTTPS, cookies seguras, rate limiting en formularios críticos).

Mantén el código limpio y legible:

Sigue PEP8 y convenciones de Django/DRF.

Usa black o isort si está configurado.

Divide en apps dentro de apps/ para escalabilidad (auth, loads, payments, communications, etc.).

No dejes TODOs sin resolver en código que forme parte del MVP.

Todos los endpoints deben estar probados y documentados.

Requerimientos funcionales clave

Auth / Accounts: registro con email/teléfono + verificaciones (Twilio SendGrid + Twilio Verify).

Pagos: Stripe con planes Starter, Pro, Business (suscripciones).

Loads: modelo básico con estados (guardado, en progreso, completado) y filtros por destino/fecha/equipo.

Comunicación: registrar sesiones con IA (canal, tiempos, tokens, resumen, transcripción completa).

Perfil de Usuario: editable y seguro (reverificación si cambia email/teléfono).

Dashboard principal: KPIs de usuarios, cargas, sesiones de comunicación, pagos.

Admin: filtros avanzados en usuarios, cargas, suscripciones y comunicaciones.

Seguridad y cumplimiento

Nunca expongas claves en el repo.

Maneja todos los secrets vía .env.

Sanitiza logs (no guardar tokens o passwords en claro).

Usa HTTPS-only en despliegue (ejemplo Nginx config con SSL).

Entregables esperados

Código funcional y listo para producción.

Migraciones actualizadas.

Pruebas unitarias mínimas para: auth, pagos, loads, comunicación.

README.md completo:

Setup local.

Variables .env.example.

Cómo probar Twilio Verify/SendGrid.

Cómo probar Stripe (checkout + webhooks con Stripe CLI).

Un usuario demo y planes demo cargados en BD.

Mantener dos entornos de prueba: uno para desarrollo y otro para producción. en el de desarrollo se utilizarán datos ficticios y en el de producción datos reales. las url y base de datos deben ser diferentes en cada entorno. sql en desarrollo debe ser sqlite y en producción debe ser postgresql. las urls localhost en desarrollo y dashboard.trauck.com en producción.

👉 Instrucción final para Copilot:
Cada vez que trabajes en este proyecto, sigue estas reglas de forma estricta. No ignores los lineamientos de diseño, seguridad ni profesionalismo. Asegúrate de que cada módulo nuevo o modificado esté acompañado de pruebas unitarias y documentación actualizada.