#!/bin/bash
# Daily backup of every site on this server, copied OFF the server.
#
# What it does:
#   1. backs up each site (database + public files + private files + site config)
#   2. copies today's backup files to a remote storage with rclone
#   3. deletes local backups older than 7 days (the remote keeps its own history)
#
# Install (see docs/DEPLOY.md, step 9):
#   cp ~/frappe-bench/apps/dz_cod/scripts/backup_offsite.sh ~/backup_offsite.sh
#   chmod +x ~/backup_offsite.sh
#   crontab -e   ->   30 2 * * * /home/frappe/backup_offsite.sh >> /home/frappe/backup_offsite.log 2>&1
#
# Needs: rclone configured with a remote called "offsite" (rclone config).

set -euo pipefail   # stop at the first error, and treat unset variables as errors

BENCH_DIR="/home/frappe/frappe-bench"
REMOTE="offsite:erp-backups/$(hostname)"   # remote name and folder in rclone
KEEP_LOCAL_DAYS=7

cd "$BENCH_DIR"
echo "=== Backup started $(date) ==="

for site_dir in sites/*/; do
	site=$(basename "$site_dir")
	# A real site has a site_config.json; skip "assets" and other folders
	[ -f "sites/$site/site_config.json" ] || continue

	echo "--- $site"
	bench --site "$site" backup --with-files --compress

	# Copy only the files of the last 24 hours to the remote folder of this site
	rclone copy "sites/$site/private/backups" "$REMOTE/$site" --max-age 24h

	# Free disk space: local backups older than KEEP_LOCAL_DAYS days
	find "sites/$site/private/backups" -type f -mtime +"$KEEP_LOCAL_DAYS" -delete
done

echo "=== Backup finished $(date) ==="
