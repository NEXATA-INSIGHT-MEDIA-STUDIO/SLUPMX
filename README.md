# SLUPMX — Tienda virtual

Primera versión estática para GitHub Pages, parte del ecosistema NUVARY.

## Publicar en GitHub Pages

1. Crea un repositorio llamado `SLUPMX`.
2. Sube todos los archivos y carpetas de este proyecto a la raíz del repositorio.
3. En GitHub abre **Settings → Pages**.
4. En **Build and deployment**, selecciona **Deploy from a branch**, rama `main` y carpeta `/ (root)`.
5. Guarda y espera a que GitHub publique el sitio.

La URL inicial será similar a `https://TU-USUARIO.github.io/SLUPMX/`.

## Configuración obligatoria antes de publicar

### WhatsApp
Edita `js/config.js`:
- `whatsappNumber`: código de país + número, solo dígitos. Para México suele comenzar por `52`.
- `whatsappMessage`: texto inicial.

El número de ejemplo está deliberadamente incompleto.

### Productos e imágenes Imgur
Edita `js/productos.js`. Cada producto admite:
- `name`, `category`, `description`
- `image`: enlace directo HTTPS de Imgur (por ejemplo `https://i.imgur.com/ID.webp`)
- `price`, `oldPrice`, `badge`, `recommended`
- `links.mercadoLibre`, `links.amazon`, `links.facebook`, `links.own`

Si un enlace está vacío, su botón no se muestra. Usa tus URL de afiliado reales donde corresponda. No uses enlaces de afiliado para simular una compra directa propia.

### Redes y proyectos
Edita `js/plataformas.js`. Agrega o cambia Wix, Blogger, Facebook, Instagram, YouTube y otras plataformas. Solo aparecen los enlaces con URL válida.

### Feed
Edita `js/publicaciones.js` para administrar las publicaciones.

## Suscripciones: falta conectar proveedor

El formulario de esta versión es una interfaz de demostración y **no guarda correos ni crea suscripciones**. Para activarlo, configura un proveedor externo de formularios/correo o membresías y coloca su URL pública en `subscriptionProviderUrl` dentro de `js/config.js`. Si el proveedor requiere API privada, usa una función serverless/backend; nunca expongas claves secretas en GitHub Pages.

Las membresías de pago requieren proveedor de pagos y backend para verificar transacciones, usuarios, renovaciones y cancelaciones. GitHub Pages no puede procesar pagos ni mantener cuentas seguras por sí solo.

## Caché
`service-worker.js` aplica caché básica a recursos propios. Cuando publiques una versión nueva:
1. Incrementa `CACHE_VERSION` en `service-worker.js`.
2. Cambia `?v=1.0.0` en las referencias CSS/JS de `index.html` si esos archivos cambiaron.

Imgur y otros recursos externos no son controlados por el service worker.

## Antes de abrir al público
- Sustituye todas las imágenes de demostración por imágenes reales de Imgur.
- Añade enlaces de compra reales y comprueba cada uno.
- Configura WhatsApp y redes.
- Conecta y prueba el proveedor de suscripciones.
- Completa aviso de privacidad y términos con información real y revisión adecuada.
- Añade información de contacto y políticas de compra/devolución de productos propios.
- Declara claramente los enlaces de afiliado.
- No recopiles información bancaria directamente en esta web.

## Dominio propio
Cuando compres el dominio:
1. En Settings → Pages → Custom domain, escribe el dominio exacto.
2. Configura los registros DNS indicados por GitHub para tu dominio y verifica HTTPS.
3. GitHub Pages puede crear/actualizar el archivo `CNAME` al guardar el dominio.
4. Comprueba la URL HTTPS y todos los enlaces después del cambio.
