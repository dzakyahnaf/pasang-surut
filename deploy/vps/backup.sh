#!/bin/sh
set -eu
umask 077
base=/opt/pasang-surut
container=pasang-surut-db-1
project=$(docker inspect "$container" --format '{{index .Config.Labels "com.docker.compose.project"}}')
test "$project" = pasang-surut
available=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
if [ "$available" -lt 450000 ]; then
    echo 'Backup ditunda: RAM tersedia kurang dari 450000 KiB.' >&2
    exit 1
fi
out="$base/backups/pasang-surut-$(date -u +%Y%m%dT%H%M%SZ).dump"
docker exec "$container" sh -c 'exec nice -n 10 pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$out.tmp"
docker exec -i "$container" pg_restore --list < "$out.tmp" > /dev/null
mv "$out.tmp" "$out"
printf '%s %s bytes\n' "$out" "$(wc -c < "$out")"
