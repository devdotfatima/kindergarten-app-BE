# Deployment

The backend runs on an EC2 instance (`16.171.16.72`) as a systemd-managed
Gunicorn service (`kindergarten-backend`), serving on port 8000.

## One-time server setup

```bash
ssh -i kindergarten-ssh.pem ubuntu@16.171.16.72

cd kindergarten-app-BE
sudo cp deploy/kindergarten-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kindergarten-backend

# stop the old dev server if it's still running
pkill -f "manage.py runserver" || true

sudo systemctl start kindergarten-backend
```

## Deploying updates

From your machine:

```bash
./deploy.bash
```

This pulls `main`, installs dependencies, runs migrations, collects static
files, and restarts the service.

The SSH key defaults to `~/Desktop/kindergarten-ssh.pem`. Override with
`DEPLOY_SSH_KEY=/path/to/key.pem ./deploy.bash`.

## Logs & status

```bash
sudo systemctl status kindergarten-backend
journalctl -u kindergarten-backend -f
```
