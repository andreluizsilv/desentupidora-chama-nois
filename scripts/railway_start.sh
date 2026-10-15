#!/usr/bin/env bash
set -e

if [ -z "${MEDIA_ROOT:-}" ] && [ -n "${RAILWAY_VOLUME_MOUNT_PATH:-}" ]; then
    export MEDIA_ROOT="${RAILWAY_VOLUME_MOUNT_PATH}/media"
fi
MEDIA_ROOT="${MEDIA_ROOT:-./media}"
export MEDIA_ROOT

mkdir -p "$MEDIA_ROOT"
if [ -d ./media ]; then
    cp -Rn ./media/. "$MEDIA_ROOT"/
fi

python manage.py migrate --noinput
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --access-logfile - \
    --error-logfile -
