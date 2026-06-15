#!/usr/bin/env bash
#
# Deploy the latest `main` to the EC2 server.
#
# Usage: ./deploy.bash
#
# Requires the EC2 SSH key. Defaults to ~/Desktop/kindergarten-ssh.pem,
# override with DEPLOY_SSH_KEY=/path/to/key.pem ./deploy.bash

set -euo pipefail

SSH_KEY="${DEPLOY_SSH_KEY:-$HOME/Desktop/kindergarten-ssh.pem}"
SSH_HOST="ubuntu@16.171.16.72"
REMOTE_APP_DIR="/home/ubuntu/kindergarten-app-BE"
SERVICE_NAME="kindergarten-backend"

ssh_run() {
  ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new "$SSH_HOST" "$@"
}

echo "==> Pulling latest main"
ssh_run "cd '$REMOTE_APP_DIR' && git pull origin main"

echo "==> Installing dependencies"
ssh_run "cd '$REMOTE_APP_DIR/core' && venv/bin/pip install -r requirements.txt"

echo "==> Running migrations"
ssh_run "cd '$REMOTE_APP_DIR/core' && venv/bin/python manage.py migrate --noinput"

echo "==> Collecting static files"
ssh_run "cd '$REMOTE_APP_DIR/core' && venv/bin/python manage.py collectstatic --noinput"

echo "==> Restarting $SERVICE_NAME"
ssh_run "sudo systemctl restart $SERVICE_NAME"

sleep 2
echo "==> Service status"
ssh_run "sudo systemctl is-active $SERVICE_NAME"

echo "==> Verifying"
curl -s -o /dev/null -w "HTTP %{http_code} from /swagger/\n" "http://16.171.16.72:8000/swagger/"

echo "==> Deploy complete"
