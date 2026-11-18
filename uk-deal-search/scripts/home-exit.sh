#!/usr/bin/env bash
# Route dealsearch through your HOME connection using a Tailscale exit node.
# Works inside an unprivileged container (userspace networking, no /dev/net/tun).
#
# One-time, on a computer at home (Mac/Windows/Linux/Raspberry Pi):
#   1. Install Tailscale, sign in, and enable "Run as exit node".
#   2. Approve it as an exit node in the Tailscale admin console (Machines -> ... -> Edit route settings).
#   3. Create an auth key (Settings -> Keys; reusable + ephemeral is ideal).
# Here: export TS_AUTHKEY=tskey-...  and  TS_EXIT_NODE=<home machine name or 100.x IP>
# Then:  source scripts/home-exit.sh   (sets DEALSEARCH_PROXY for this shell)
set -euo pipefail
: "${TS_AUTHKEY:?set TS_AUTHKEY}"; : "${TS_EXIT_NODE:?set TS_EXIT_NODE}"
TS_DIR="${TS_DIR:-$HOME/.cache/dealsearch-tailscale}"; mkdir -p "$TS_DIR"
if ! command -v tailscaled >/dev/null && [ ! -x "$TS_DIR/tailscaled" ]; then
  ver=$(curl -fsSL "https://pkgs.tailscale.com/stable/?mode=json" | python3 -c 'import sys,json;print(json.load(sys.stdin)["TarballsVersion"])')
  curl -fsSL "https://pkgs.tailscale.com/stable/tailscale_${ver}_amd64.tgz" | tar -xz -C "$TS_DIR" --strip-components=1
fi
PATH="$TS_DIR:$PATH"
tailscaled --tun=userspace-networking --socks5-server=127.0.0.1:1055 \
  --state="$TS_DIR/state" --socket="$TS_DIR/sock" >"$TS_DIR/log" 2>&1 &
sleep 3
tailscale --socket="$TS_DIR/sock" up --authkey="$TS_AUTHKEY" --hostname=dealsearch-cloud \
  --exit-node="$TS_EXIT_NODE" --accept-routes
export DEALSEARCH_PROXY=socks5h://127.0.0.1:1055
echo "Exit IP: $(curl -s --socks5-hostname 127.0.0.1:1055 https://ifconfig.co/country) $(curl -s --socks5-hostname 127.0.0.1:1055 https://ifconfig.co)"
