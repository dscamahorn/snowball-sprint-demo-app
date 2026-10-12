#!/bin/sh
# Ships the current main branch to the droplet in one command:
#
#   ./deploy.sh
#
# Steps (PRD.md, Deployment section):
#   1. on the droplet: check out the exact commit being deployed
#   2. on the droplet: uv sync --frozen, the exact packages in uv.lock
#   3. restart the gunicorn service so it loads the new code
#   4. ask the live site's /health page whether the API keys are set
#
# Prompt and knowledge files are read from disk on every request, but Python
# code is loaded once at startup, so the service is always restarted.
#
# Runs only from a clean, pushed main, and ships that one commit: the
# droplet checks out the commit by hash rather than pulling a branch, so what
# is live is always a commit on GitHub.
# Stops at the first failing step and says which one. Safe to run twice.
# Needs deploy.env (see deploy.env.example) and the deploy key in 1Password. The .env file with the API keys stays on the
# droplet and is never copied.

set -e

if [ ! -f deploy.env ]; then
  echo "deploy.env is missing. Copy deploy.env.example to deploy.env and fill it in."
  exit 1
fi
. ./deploy.env

# Deploy only what is on main, committed, and pushed, so the live site always
# matches a commit on GitHub (the release record). Another session may have
# switched branches in this checkout, so check right now, not from memory.
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "On branch '$CURRENT_BRANCH'. Deploys run from main only."
  exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  echo "The working tree has uncommitted changes. Commit or stash them first."
  exit 1
fi
git fetch --quiet origin main
if [ -n "$(git log origin/main..main --oneline)" ]; then
  echo "main has commits that are not on GitHub yet. Push first, then deploy."
  exit 1
fi
DEPLOY_COMMIT=$(git rev-parse HEAD)
echo "Deploying commit $DEPLOY_COMMIT"

REMOTE="$DROPLET_USER@$DROPLET_HOST"
# The checkout lives in SITE_ROOT/repo, the droplet standard. (Inside it,
# "app" is this project's Flask package.)
REPO_DIR="$SITE_ROOT/repo"
SERVICE_NAME="snowball-sprint-demo-app-web"

# Reuse one SSH connection for every step. The droplet's firewall refuses
# an address that opens more than about six connections in half a minute.
# With a shared "control" connection the later steps ride along on the first.
SSH_OPTIONS="-o ControlMaster=auto -o ControlPath=/tmp/snowball-sprint-demo-app-web-deploy-ssh -o ControlPersist=120"

step() {
  echo ""
  echo "==> $1"
}

step "1/4 Checking out $DEPLOY_COMMIT on the droplet"
ssh $SSH_OPTIONS "$REMOTE" "cd '$REPO_DIR' && git fetch --quiet origin && git checkout --quiet --detach '$DEPLOY_COMMIT'"

step "2/4 Installing the exact packages in uv.lock"
# --frozen installs what the lock file says and refuses to change it, so the
# server runs the versions that were reviewed, not whatever uv resolves today.
# On the droplet uv is installed as a snap (/snap/bin). The official installer
# would put it in ~/.local/bin instead. Both are added to PATH so the command
# works either way over a non-interactive SSH connection.
# UV_PYTHON_INSTALL_DIR puts the interpreter in the shared folder the service
# (which runs as www-data) can read.
ssh $SSH_OPTIONS "$REMOTE" "cd '$REPO_DIR' && UV_PYTHON_INSTALL_DIR=/opt/uv/python PATH=\"\$PATH:/snap/bin:\$HOME/.local/bin\" uv sync --frozen"

step "3/4 Restarting the $SERVICE_NAME service"
# The droplet user is "deploy", which owns the site folder but is not root.
# A sudo rule on the droplet (/etc/sudoers.d/deploy) lets it run exactly
# these two systemctl commands for this service, without a password.
ssh $SSH_OPTIONS "$REMOTE" "sudo systemctl restart $SERVICE_NAME \
  && sudo systemctl is-active $SERVICE_NAME > /dev/null \
  && echo '$SERVICE_NAME: running'"

step "4/4 Checking the live site"
# /health answers with JSON that says whether each API key was found in .env.
# A few seconds' pause gives gunicorn time to finish starting.
sleep 3
curl --fail --silent --show-error "$SITE_URL/health"
echo ""
echo "Site:    $SITE_URL"
echo "Commit:  $DEPLOY_COMMIT"
