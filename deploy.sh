#!/bin/sh
# Ships the current main branch to the droplet in one command:
#
#   ./deploy.sh
#
# Steps (PRD.md, Deployment section):
#   1. on the droplet: git pull main
#   2. on the droplet: uv sync, so new Python dependencies get installed
#   3. restart the gunicorn service so it loads the new code
#   4. ask the live site's /health page whether the API keys are set
#
# Prompt and knowledge files are read from disk on every request, but Python
# code is loaded once at startup, so the service is always restarted.
#
# Stops at the first failing step and says which one. Safe to run twice.
# Needs deploy.env (see deploy.env.example) and SSH key access to the droplet.
# The SSH key lives in 1Password; see the README's Deploying section for how
# the container reaches it. The .env file with the API keys stays on the
# droplet and is never copied.

set -e

if [ ! -f deploy.env ]; then
  echo "deploy.env is missing. Copy deploy.env.example to deploy.env and fill it in."
  exit 1
fi
. ./deploy.env

REMOTE="$DROPLET_USER@$DROPLET_HOST"
APP_DIR="$SITE_ROOT/app"
SERVICE_NAME="circular-concept"

# Reuse one SSH connection for every step. The droplet's firewall refuses
# an address that opens more than about six connections in half a minute.
# With a shared "control" connection the later steps ride along on the first.
SSH_OPTIONS="-o ControlMaster=auto -o ControlPath=/tmp/circular-deploy-ssh -o ControlPersist=120"

step() {
  echo ""
  echo "==> $1"
}

step "1/4 Pulling main on the droplet"
ssh $SSH_OPTIONS "$REMOTE" "cd '$APP_DIR' && git pull --ff-only origin main"

step "2/4 Syncing Python dependencies"
# On the droplet uv is installed as a snap (/snap/bin). The official installer
# would put it in ~/.local/bin instead. Both are added to PATH so the command
# works either way over a non-interactive SSH connection.
ssh $SSH_OPTIONS "$REMOTE" "cd '$APP_DIR' && PATH=\"\$PATH:/snap/bin:\$HOME/.local/bin\" uv sync"

step "3/4 Restarting the $SERVICE_NAME service"
# The droplet user is root, so no sudo is needed in front of systemctl.
ssh $SSH_OPTIONS "$REMOTE" "systemctl restart $SERVICE_NAME \
  && systemctl is-active $SERVICE_NAME > /dev/null \
  && echo '$SERVICE_NAME: running'"

step "4/4 Checking the live site"
# /health answers with JSON that says whether each API key was found in .env.
# A few seconds' pause gives gunicorn time to finish starting.
sleep 3
curl --fail --silent --show-error "$SITE_URL/health"
echo ""
echo "Site:  $SITE_URL"
