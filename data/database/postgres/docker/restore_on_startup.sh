#!/bin/bash
set -e

echo "Running entrypoint.sh..."

echo ""

# Espera pasiva, ya que depends_on: service_healthy ya debería haber hecho el trabajo
# Sin embargo, un pg_isready final no hace daño.
echo "Verifying PostgreSQL connectivity..."
until pg_isready -q; do
  echo "PostgreSQL not yet responsive, waiting..."
  sleep 2
done
echo ""
echo "PostgreSQL is responsive. Proceeding with restoration."

echo ""

echo "Restoring database '${PGDATABASE}' from ${BAK_FILE} ..."
pg_restore -Fc -v -d "${PGDATABASE}" "${BAK_FILE}"
echo "Restoration completed."

echo ""

echo "Deleting 'public' schema if exists in '${PGDATABASE}' ..."
psql  -d "${PGDATABASE}" -c "DROP SCHEMA IF EXISTS public;"
echo "Deleation completed."

echo ""

