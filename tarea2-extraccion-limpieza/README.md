Extracción y limpieza
## Proceso de extracción y limpieza - UNGRD

Se extrajeron los datos de la UNGRD desde el portal de Datos Abiertos,  filtrando solo los contratos de esta entidad (850 filas, 85 columnas), para no descargar el dataset completo de 6 millones de filas.

### Problema encontrado
Al subir el archivo a S3 y consultarlo desde Athena, los datos salían desordenados: algunas columnas de texto largo (como la descripción del proceso o la ubicación) tenían saltos de línea dentro del mismo campo, lo que hacía que Athena cortara mal las columnas.
### Intentos de solución
1. Se utilizo IA para identificar y organizar mejor los datos, ya que no lográbamos resolverlo por nuestra cuenta.
2. Primero se limpió el archivo quitando esos saltos de línea con Python, antes de subirlo a S3.
3. Aun así, al usar el crawler automático de Glue, columnas con comas dentro del texto seguían  quedando mal separadas, porque el crawler no reconocía bien las comillas.
4. Se intentó crear un "classifier" personalizado en Glue para indicarle cómo leer las comillas, pero tampoco funcionó del todo.
### Solución final
Se creó la tabla manualmente en Athena, escribiendo directamente el código SQL para indicarle cómo separar las columnas y reconocer las comillas. Este código se encuentra en el archivo `crear_tabla_ungrd.sql` en esta misma carpeta.
