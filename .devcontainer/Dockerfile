# The dev container image. VS Code builds it for "Reopen in Container", and
# the devcontainer command builds the same file on the Air.
#
# Converted from an image-only devcontainer at the October 11, 2026 audit:
# every dev container builds from a Dockerfile, so the container's own setup
# lives in the image. Add the system tools the project needs below.
FROM mcr.microsoft.com/devcontainers/python:3.14

# Docker creates the folders a bind mount needs as root. Claude Code must be
# able to write in ~/.claude (its session files), so the folder is created
# here, owned by the normal user, before the mounts land inside it.
# The global rules and app preferences arrive as the shared/ folder mount
# (see devcontainer.json). Claude Code looks for them at ~/.claude/CLAUDE.md
# and ~/.claude/settings.json, so those two are a one-line import and a
# symlink pointing into shared/.
RUN mkdir -p /home/vscode/.claude \
    && printf '@~/.claude/shared/CLAUDE.md\n' > /home/vscode/.claude/CLAUDE.md \
    && ln -s shared/settings.json /home/vscode/.claude/settings.json \
    && chown -R vscode:vscode /home/vscode/.claude
