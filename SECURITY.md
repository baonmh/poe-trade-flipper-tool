# Security

## Threat model

This application is a **local web UI** that fetches **public** market data (primarily [poe.ninja](https://poe.ninja)) and optional public GGG league metadata. It is **not** a Path of Exile or trade-site login client.

## Reporting issues

If you find a security problem in this repository (e.g. unsafe dependency, accidental secret), please open a **private** security advisory on GitHub (**Security → Report a vulnerability**) or contact the maintainer via GitHub. Do not post exploit details in public issues.

## Good practices for users

- Run from source or trusted release binaries only.
- The bundled Flask server listens on **127.0.0.1** (loopback) only — it is not meant to be reachable from other machines on your network.
- Do not paste `settings.json` or screenshots containing personal data in public bug reports if they matter to you.
- Keep Python and dependencies updated (`pip install -r requirements.txt`).

## Out of scope

- **In-game account safety** (malware on your PC, stolen OS session) is outside what this app can enforce.
- **Third-party sites** (poe.ninja, GGG) have their own terms and availability; the tool does not control their uptime or rate limits.
