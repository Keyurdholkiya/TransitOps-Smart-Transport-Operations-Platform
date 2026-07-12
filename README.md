# TransitOps Smart Transport Operations Platform

Frontend for managing fleet vehicles, drivers, and trip dispatch workflows.

## Run with Docker

```bash
docker compose up --build
```

Open `http://localhost:8080` in a browser. Set `PORT` before the command to use a different host port.

The frontend is intentionally browser-only for hackathon testing. Data is stored in browser `localStorage` and begins empty.
