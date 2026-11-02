#!/bin/bash
# Prepares SSH logins into this container, so the Claude desktop app can run
# a session in here (its "SSH" environment). Runs on every container start
# (postStartCommand in devcontainer.json), as the normal user.
#
# How the login works: the Mac's ~/.ssh/config has a Host entry whose
# ProxyCommand runs `docker exec -i <container> /usr/sbin/sshd -i`, so the
# SSH server starts inside this container only for the length of one
# connection, over docker exec. Nothing listens on a network port. The
# server's settings are in the Dockerfile.
set -e

SSH_FOLDER="$HOME/.ssh"
TRUSTED_KEYS_FILE="$HOME/.claude/shared/allowed_signers"
AUTHORIZED_KEYS_FILE="$SSH_FOLDER/authorized_keys"

mkdir -p "$SSH_FOLDER"
chmod 700 "$SSH_FOLDER"

# Who may log in: the same keys git already trusts as Doug for signed
# commits (allowed_signers, from the read-only shared mount). Each line
# there is "email key-type key comment"; dropping the email leaves a valid
# authorized_keys line. Lines starting with # are comments and are skipped.
# sshd refuses an authorized_keys file others can write, hence the chmod.
grep -v '^#' "$TRUSTED_KEYS_FILE" | cut -d ' ' -f 2- > "$AUTHORIZED_KEYS_FILE"
chmod 600 "$AUTHORIZED_KEYS_FILE"

# A safety net for the GitHub CLI. A session signs gh in for the push-time
# Dependabot check and out again at the end of it (the stack-security
# skill, step 5); if that session was interrupted, the sign-in would stay
# until a rebuild. Signing out here limits it to the next container start.
# "|| true" because gh says "not logged in" (an error) when there is
# nothing to sign out, and that must not stop the script.
if command -v gh > /dev/null; then
  gh auth logout --hostname github.com > /dev/null 2>&1 || true
fi
