#!/usr/bin/env bash
set -e

mkdir -p "$MEDIA_ROOT"
if [ -d ./media ]; then
    cp -Rn ./media/. "$MEDIA_ROOT"/
fi

python manage.py migrate --noinput
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-10000}" \
    --workers 2 \
    --access-logfile - \
    --error-logfile -
