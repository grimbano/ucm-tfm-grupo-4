#!/bin/bash
set -e

echo "Running entrypoint.sh..."
echo ""

# Espera pasiva, ya que depends_on: service_healthy ya debería haber hecho el trabajo
# Sin embargo, un pg_isready final no hace daño.
echo "Verifying PostgreSQL connectivity..."
until pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -h /var/run/postgresql -q; do
  echo "PostgreSQL not yet responsive, waiting..."
  sleep 2
done
echo ""

echo "PostgreSQL is responsive. Proceeding with restoration."
echo ""

# Validación según la extensión del archivo
if [[ "${BAK_FILE}" == *.zip ]]; then
  echo "Restoring database '${PGDATABASE}' from zip archive ${BAK_FILE} ..."
  unzip -p "${BAK_FILE}" | pg_restore -U "${POSTGRES_USER}" -h /var/run/postgresql -Fc -v -d "${PGDATABASE}"
elif [[ "${BAK_FILE}" == *.bak ]]; then
  echo "Restoring database '${PGDATABASE}' directly from ${BAK_FILE} ..."
  pg_restore -U "${POSTGRES_USER}" -h /var/run/postgresql -Fc -v -d "${PGDATABASE}" "${BAK_FILE}"
else
  echo "Error: ${BAK_FILE} format not supported. Expected .bak or .zip"
  exit 1
fi

echo "Restoration completed."
echo ""

echo "Deleting 'public' schema if exists in '${PGDATABASE}' ..."
psql -U "${POSTGRES_USER}" -h /var/run/postgresql -d "${PGDATABASE}" -c "DROP SCHEMA IF EXISTS public;"

echo "Deletion completed."
echo ""