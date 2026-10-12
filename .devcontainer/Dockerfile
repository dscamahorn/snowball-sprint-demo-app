# The dev container image. VS Code builds it for "Reopen in Container", and
# the devcontainer command builds the same file on the Air.
#
# Starts from Microsoft's Python image (git, a proper shell, sudo, and the
# non-root "vscode" user). Node arrives later, from the node feature in
# devcontainer.json.
FROM mcr.microsoft.com/devcontainers/python:3.14

# uv, the house Python tool, plus the two security scanners the Security
# rules run before a milestone branch is pushed: Semgrep reads the code for
# known bad shapes, pip-audit checks Python packages against the database of
# known holes. (npm audit comes with npm.) They live in the image so every
# project has them on day one and the versions are the same everywhere. uv
# installs each scanner as an isolated tool under /opt/uv and links the
# commands into /usr/local/bin; the three variables on the RUN line tell it
# where, and are set for that one line only so the project's own `uv sync`
# is unaffected.
# The versions are pinned on purpose: bump them at a two-week review.
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/
RUN UV_TOOL_DIR=/opt/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    uv tool install semgrep==1.180.0 \
    && UV_TOOL_DIR=/opt/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    uv tool install pip-audit==2.10.1 \
    && chmod -R a+rX /opt/uv

# npm 12 is not set up here. This Python image has no Node yet at this point
# (it arrives later, from the node feature in devcontainer.json), so npm
# cannot run. The npm pin and the allow-scripts line run at the front of
# postCreateCommand instead; devcontainer.json explains them.

# System packages. ffmpeg is here for every project because the timelapse
# skill (installed into the container by postCreateCommand, see
# devcontainer.json) builds its video with it. Add the project's own system
# tools to the same line, one per row.
# --no-install-recommends keeps the image smaller by skipping optional
# extras; removing the apt lists afterward does the same.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Web projects only: the browser for the project's verification skill (the
# stack-verify skill explains the skill; Playwright is the library that drives
# the browser) and for the timelapse skill, which looks for it under this
# same path. Chromium is installed here, at build time, into a shared path
# every user can read, so no download happens inside a running session (the
# Bash sandbox allows only a short list of domains). This project does not
# use Playwright yet; when it does, pin the same Playwright version in the
# project and uncomment these lines. One catch for this Python image: npx
# needs Node, which only arrives from the node feature after the image is
# built, so these two lines will need adjusting before they work here (the
# template has not covered that case yet). Bump the version at a two-week
# review.
# ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
# RUN npx --yes playwright@1.64.0 install --with-deps chromium \
#     && chmod -R a+rX /opt/playwright

# Docker creates the folders a bind mount needs as root. Claude Code must be
# able to write in ~/.claude and in ~/.claude/projects (its session files;
# the project's own transcript folder is mounted inside projects/, and a
# session started in a subfolder of the repo writes a sibling folder there),
# so both are created here, owned by the normal user, before the mounts
# land inside them.
# The global rules and app preferences arrive as the shared/ folder mount
# (see devcontainer.json). Claude Code looks for them at ~/.claude/CLAUDE.md
# and ~/.claude/settings.json, so those two are a one-line import and a
# symlink pointing into shared/.
RUN mkdir -p /home/vscode/.claude/projects \
    && printf '@~/.claude/shared/CLAUDE.md\n' > /home/vscode/.claude/CLAUDE.md \
    && ln -s shared/settings.json /home/vscode/.claude/settings.json \
    && chown -R vscode:vscode /home/vscode/.claude
