#!/bin/bash
set -euo pipefail

# 1) Import GPG private key from secret
mkdir -p ~/.gnupg
chmod 700 ~/.gnupg

if [ -n "${AURORA_GPG_PRIVATE:-}" ]; then
  printf "%s\n" "$AURORA_GPG_PRIVATE" | gpg --batch --yes --import
  # Trust the key ultimately (non-interactive)
  KEYID="$(gpg --list-secret-keys --with-colons | awk -F: '/^fpr:/ {print $10; exit}')"
  printf 'trust\n5\ny\nsave\n' | gpg --batch --yes --command-fd 0 --edit-key "$KEYID" >/dev/null 2>&1 || true
  # If key has passphrase, configure GPG agent to allow loopback
  if [ -n "${AURORA_GPG_PASSPHRASE:-}" ]; then
    echo "allow-loopback-pinentry" >> ~/.gnupg/gpg-agent.conf || true
    gpgconf --kill gpg-agent || true
  fi
fi

# 2) Git identity + signing
git config --global user.name  "${AURORA_GIT_NAME:-aurora}"
git config --global user.email "${AURORA_GIT_EMAIL:-aurora@example.com}"
git config --global gpg.program gpg
git config --global commit.gpgsign true
# Pick the first secret key as signer if none set explicitly
if [ -z "$(git config --global user.signingkey)" ]; then
  SIGKEY="$(gpg --list-secret-keys --with-colons | awk -F: '/^sec:/ {print $5; exit}')"
  [ -n "$SIGKEY" ] && git config --global user.signingkey "$SIGKEY"
fi

# 3) Make sure the remote is present
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git remote remove origin >/dev/null 2>&1 || true
  if [ -n "${AURORA_GIT_URL:-}" ]; then
    git remote add origin "$AURORA_GIT_URL"
    git fetch origin || true
  fi
fi

echo "[aurora_boot] GPG + git signing ready."