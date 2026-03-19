# Deploy to fido.nickmitn.ru

Deployment is automated via GitHub Actions on push to `main`.

## Prerequisites

### Server setup
1. Create directory on server: `~/fido.nickmitn.ru/`
2. Ensure Docker and Docker Compose are installed
3. Create SSH user (typically same as domain: `fido.nickmitn.ru`) with access to Docker

### GitHub secrets
Configure in repository: **Settings → Secrets and variables → Actions**

| Secret | Description |
|--------|-------------|
| `DEPLOY_KEY` | SSH private key for server access |
| `DOCKER_REGISTRY_HOST` | Registry host (e.g. `ghcr.io` or your registry) |
| `DOCKER_REGISTRY_USERNAME` | Registry username |
| `DOCKER_REGISTRY_PASSWORD` | Registry password or token |
| `FIDO_ENV_FILE` | Contents of `.env` (all sensitive config) |

### Docker registry
You need a registry to push the telegram-bot image. Options:
- **GitHub Container Registry**: `ghcr.io` — use a PAT with `write:packages` as password
- **Docker Hub**: `docker.io` — use your Docker Hub credentials
- **Private registry**: your own registry host

If using GHCR, image will be `ghcr.io/YOUR_ORG/fido-setup-telegram-bot:main`.

### First-time server setup
On the server, log in and run:
```bash
mkdir -p ~/fido.nickmitn.ru
# Ensure Docker can access your registry (docker login)
```
