# The dev container image. VS Code builds it for "Reopen in Container", and
# the devcontainer command builds the same file on the Air.
#
# Starts from Microsoft's Python image (git, a proper shell, sudo, and the
# non-root "vscode" user). Node is copied in below, from the official
# Node image.
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
    && UV_PYTHON_INSTALL_DIR=/opt/uv/python uv python install 3.14 \
    && chmod -R a+rX /opt/uv
# The "uv python install" line makes sure /opt/uv/python holds a Python on
# every image. The timelapse install in postCreateCommand looks there. uv
# only downloads a Python for the scanners when the image's own is too old,
# so on an image whose system Python is new enough (Node 22-bookworm) the
# folder was never made and the timelapse install failed (found October 12,
# 2026).

# Node, copied from the official Node image, because this Python image
# has none. Node goes in here, at build time, so the npm 12 lines below
# can run and nothing npm-related is left for postCreateCommand. (The node
# feature was tried first, on October 12, 2026: it brings Node only after
# this file is built, so npm 12 had to wait for postCreateCommand, where it
# raced VS Code's own shells re-making nvm's "current" link and failed now
# and then.) The two COPY lines bring the node program and its global
# packages, npm among them; the RUN line makes the npm and npx commands,
# which in the Node image are links to npm's own scripts.
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:22-bookworm-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# npm 12, pinned. The Node copied in above ships npm 10. From npm 12, a
# package's install scripts do not run unless the project lists the
# package in an "allowScripts" allowlist in package.json (built with "npm
# approve-scripts"), git and remote-URL dependencies are off, and the
# "min-release-age" cooldown in the project's .npmrc is honored. Those
# three closed the install-time path every 2026 npm supply-chain wave
# used. Bump the version at a two-week review.
RUN npm install -g npm@12.2.0

# The one exception to "scripts off". The Claude Code devcontainer feature
# installs @anthropic-ai/claude-code with "npm install -g" after this image
# is built, and that package's install script is what fetches the native
# binary; without the allowance, claude fails with "exec format error"
# (found by the read-only-mounts test on October 12, 2026). The setting is
# a global-install allowlist by package name, so no other package's script
# runs. It is a separate RUN line on purpose: in the same shell as the
# install above, "npm" still meant the image's npm 10, which does not know
# the option.
RUN npm config set --location=global allow-scripts=@anthropic-ai/claude-code

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
# project and uncomment these lines. They work in this Python image as
# they are, because the Node block above puts npx in place first. Bump
# the version at a two-week review.
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
