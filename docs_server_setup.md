# Direct Server Setup

This setup does not use Docker.

It uses:

- one Python virtual environment named `myenv`
- one editable config file named `.env.server`
- one command to start backend and Streamlit

## 1. Prepare the server

Clone the repo:

```bash
git clone <repo-url>
cd the-project-maverick
```

Make the config file:

```bash
cp server.env.example .env.server
```

Edit `.env.server`.

Main values to change:

- `POSTGRES_SERVER`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `BACKEND_PORT`
- `STREAMLIT_PORT`
- `FRONTEND_HOST`
- `BACKEND_CORS_ORIGINS`

If the database is on another machine, put its hostname or IP in `POSTGRES_SERVER`.

## 2. Create the Python environment

```bash
bash scripts/setup-myenv.sh
```

That creates:

```text
myenv/
```

## 3. Start both services

```bash
bash scripts/start-all.sh
```

This starts:

- backend on `BACKEND_PORT`
- Streamlit on `STREAMLIT_PORT`

Logs:

```text
run/backend.log
run/streamlit.log
```

## 4. Stop both services

```bash
bash scripts/stop-all.sh
```

## 5. Start one service only

Backend only:

```bash
bash scripts/start-backend.sh
```

Streamlit only:

```bash
bash scripts/start-streamlit.sh
```

## Notes

- Backend model artifacts are read from:

```text
model_artifacts/stock_prediction_xgb_global/
```

- Snapshot files are written to:

```text
datasets/
```

- If you want these services to survive logout and reboot cleanly, the next step would be adding `systemd` service files. The current scripts are meant to be the fastest manual setup path.
