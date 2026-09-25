# Curio: incorporación diaria

El flujo está instalado en este repositorio. La importación necesita el secret de Supabase; sin él, se omite y el resumen de Actions indica qué falta.

## Activación única

1. En Supabase > Project Settings > API Keys, crear una clave secreta dedicada a esta automatización.
2. En este repositorio > Settings > Secrets and variables > Actions > New repository secret, guardarla como `SUPABASE_SECRET_KEY`. No pegarla en un chat, archivo o commit. Es una clave de servidor con privilegios amplios; nunca se incorpora al sitio web.
3. En Actions, abrir `Curio daily catalog` y seleccionar **Run workflow**. Los pushes solo validan código y catálogo; nunca insertan datos.
4. Revisar el paso **Add reviewed videos within limits** para ver cuántos videos se insertaron. Sin secret, el flujo puede terminar correctamente pero la importación queda omitida: revisar el resumen.

No requiere dependencias instaladas ni servicios de IA pagos. El repositorio contiene código y un catálogo de enlaces a fuentes públicas; las credenciales viven exclusivamente en GitHub Secrets.

## Comportamiento

- Hasta 3 videos diarios a partir de las 08:17 de Buenos Aires; GitHub puede retrasar la ejecución.
- Pausa a los 1.000 registros totales, sin borrar ninguno ni alterar favoritos.
- Solo publica la cola previamente revisada; no busca videos nuevos ni genera resúmenes con IA. La cola inicial contiene la segunda tanda de 20 videos. Si ya se cargaron mediante SQL, se omiten todos y será necesario ampliar la cola.
- Evita duplicados por URL. Una segunda ejecución el mismo día respeta el máximo contando los registros creados ese día, también los agregados manualmente.
- Mantiene aproximadamente 35% filosofía, 35% ciencia, 25% movilidad y 5% arte/música, según disponibilidad de la cola.
- Las inserciones nuevas quedan aprobadas porque la cola es curada. Revisar fuente, enlace y contenido antes de agregar entradas.
- Sin LLM, dependencias de Python, cachés ni archivos de video. Consume las cuotas gratuitas de GitHub Actions y Supabase, compartidas con otros proyectos del usuario; no garantiza capacidad ilimitada.
- El bloqueo de concurrencia cubre este workflow. No ejecutar otro importador en paralelo: las lecturas y las inserciones no forman una transacción global.
- Para pausar: Actions > workflow > Disable workflow. Para cambiar límites: editar DAILY_LIMIT (1–10) y CATALOG_CAP (1–1.000).

## Prueba local sin credenciales

`python3 -m unittest test_import_daily.py`

## Preferencias de la interfaz

Favoritos, me gusta y ver menos se guardan en el navegador actual. No se sincronizan con Supabase ni con otros dispositivos. Los favoritos conservan los metadatos para seguir disponibles aunque el video no esté en la primera tanda cargada. No se borran videos automáticamente. Para sincronizar preferencias se necesita autenticación y una tabla protegida por usuario.
