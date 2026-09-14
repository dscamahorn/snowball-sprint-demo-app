#!/bin/sh
# One-time droplet setup. Run it once, as root, from the app folder
# (/var/www/circular.workshopper.ai/app):
#
#   sh server/setup-site.sh circular.workshopper.ai you@example.com
#
# The first argument is the site's domain. The second is the email that
# Let's Encrypt uses for certificate expiry warnings.
#
# Steps:
#   1. install Apache and certbot with apt
#   2. install uv and the app's Python dependencies (uv also downloads Python)
#   3. create .env from .env.example if it is missing
#   4. retire the old "flask_subdomain" service that ran the app from
#      /var/www/circular-concept, then install and start the new service
#   5. install the Apache virtual host and turn on the proxy modules
#      (an older virtual host for the same domain is backed up and disabled)
#   6. request the HTTPS certificate and redirect HTTP to HTTPS
#
# Stops at the first failing step. Safe to run twice: every step either
# skips work that is already done or overwrites it with the same result.
# The droplet's login user is root, so no sudo is needed anywhere.

set -e

SITE_DOMAIN="$1"
LETSENCRYPT_EMAIL="$2"

if [ -z "$SITE_DOMAIN" ] || [ -z "$LETSENCRYPT_EMAIL" ]; then
  echo "Usage: sh server/setup-site.sh <domain> <email-for-lets-encrypt>"
  exit 1
fi

# The app folder is the parent of the server/ folder this script lives in.
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_NAME="circular-concept"
SERVICE_USER="$(id -un)"

step() {
  echo ""
  echo "==> $1"
}

step "1/6 Installing Apache and certbot"
apt-get update -q
apt-get install -y -q apache2 certbot python3-certbot-apache curl

step "2/6 Installing uv and the Python dependencies"
# uv manages the virtual environment and downloads the Python version that
# pyproject.toml asks for, so nothing else needs to be installed system-wide.
if ! command -v uv > /dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # The installer puts uv in ~/.local/bin, which is not on PATH yet in this shell.
  PATH="$HOME/.local/bin:$PATH"
fi
cd "$APP_DIR"
uv sync

step "3/6 Checking for .env"
if [ -f "$APP_DIR/.env" ]; then
  echo ".env already exists, leaving it alone"
else
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  echo "Created .env from .env.example. Fill in the API keys and a real SECRET_KEY,"
  echo "then run: systemctl restart $SERVICE_NAME"
fi

step "4/6 Installing the $SERVICE_NAME systemd service"
# The app used to run as a service called flask_subdomain from the old folder.
# It holds port 8000, so it must be stopped before the new service can start.
OLD_SERVICE_NAME="flask_subdomain"
if [ -f "/etc/systemd/system/$OLD_SERVICE_NAME.service" ]; then
  systemctl disable --now "$OLD_SERVICE_NAME"
  mv "/etc/systemd/system/$OLD_SERVICE_NAME.service" \
    "/etc/systemd/system/$OLD_SERVICE_NAME.service.retired"
  echo "Stopped the old $OLD_SERVICE_NAME service and kept its file as $OLD_SERVICE_NAME.service.retired"
fi

# Fill the placeholders in the unit file with this droplet's paths and user.
sed -e "s|__APP_DIR__|$APP_DIR|g" -e "s|__USER__|$SERVICE_USER|g" \
  "$APP_DIR/server/$SERVICE_NAME.service" \
  > "/etc/systemd/system/$SERVICE_NAME.service"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

step "5/6 Installing the Apache virtual host"
# The domain already has virtual host files from the earlier hand-made setup
# (the HTTP one and the HTTPS one certbot made). They are moved out of the way
# under a backup name so they can be looked at or restored. Apache normally
# keeps a link in sites-enabled pointing at sites-available, but on this
# droplet the HTTPS one is a separate real file, so both folders are checked.
# Only files named after this domain are touched; the other sites are left alone.
BACKUP_SUFFIX="before-gunicorn-$(date +%Y%m%d-%H%M%S)"
for OLD_SITE in "$SITE_DOMAIN" "$SITE_DOMAIN-le-ssl"; do
  for APACHE_FOLDER in sites-enabled sites-available; do
    OLD_FILE="/etc/apache2/$APACHE_FOLDER/$OLD_SITE.conf"
    if [ -L "$OLD_FILE" ]; then
      # A link: just remove it, the real file in sites-available is backed up below.
      rm "$OLD_FILE"
    elif [ -f "$OLD_FILE" ]; then
      mv "$OLD_FILE" "$OLD_FILE.$BACKUP_SUFFIX"
      echo "Backed up old $APACHE_FOLDER/$OLD_SITE.conf to $OLD_FILE.$BACKUP_SUFFIX"
    fi
  done
done

a2enmod proxy proxy_http headers > /dev/null
sed -e "s|__DOMAIN__|$SITE_DOMAIN|g" -e "s|__APP_DIR__|$APP_DIR|g" \
  "$APP_DIR/server/apache-site.conf" \
  > "/etc/apache2/sites-available/$SITE_DOMAIN.conf"
a2ensite "$SITE_DOMAIN" > /dev/null
apache2ctl configtest
systemctl reload apache2

step "6/6 Requesting the HTTPS certificate"
# certbot proves to Let's Encrypt that this server answers for the domain, so
# the DNS record must already point here (Cloudflare set to "DNS only").
# If the domain already has a certificate from the old setup, certbot reuses
# it and just wires it into the new virtual host.
# --redirect makes Apache send plain HTTP visitors to HTTPS.
certbot --apache --non-interactive --agree-tos --redirect \
  --domains "$SITE_DOMAIN" --email "$LETSENCRYPT_EMAIL"

echo ""
echo "Done. Site: https://$SITE_DOMAIN"
echo "Service status:"
systemctl is-active "$SERVICE_NAME" && echo "$SERVICE_NAME: running" || echo "$SERVICE_NAME: NOT running"
