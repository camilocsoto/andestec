#!/bin/bash
set -e
# Realiza la restauración del backup.
# Usamos las variables de entorno que docker-compose ya le pasa al contenedor de postgres.
pg_restore --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -v "/docker-entrypoint-initdb.d/initdb.dump"

echo ">>>>>>>>> BACKUP RESTAURADO CORRECTAMENTE <<<<<<<<<"