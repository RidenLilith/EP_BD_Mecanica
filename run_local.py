#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time
import socket
import webbrowser
import argparse
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "back-end"
FRONTEND_DIR = ROOT / "frontend"


def install_requirements():
    req = BACKEND_DIR / "requirements.txt"
    if not req.exists():
        print("[run_local] No requirements.txt found; skipping install.")
        return
    print("[run_local] Installing Python requirements (this may take a while)...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=True)


def run_seed():
    seed_script = BACKEND_DIR / "seed.py"
    if not seed_script.exists():
        print("[run_local] No seed.py found; skipping.")
        return True
    print("[run_local] Running seed script to populate the database...")
    res = subprocess.run([sys.executable, str(seed_script)])
    return res.returncode == 0


def run_frontend_http(port=8081):
    if not FRONTEND_DIR.exists():
        print(f"[run_local] ERROR: frontend directory not found: {FRONTEND_DIR}")
        return
    os.chdir(FRONTEND_DIR)
    print(f"[run_local] Front-end being served at http://localhost:{port}")
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def run_backend():
    app_script = BACKEND_DIR / "app.py"
    if not app_script.exists():
        print("[run_local] No backend app.py found; aborting.")
        return 1
    print("[run_local] Starting backend (Flask) ...")
    proc = subprocess.Popen([sys.executable, str(app_script)])
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
    return proc.returncode


def check_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Run project locally (seed + backend + static frontend).'
    )
    parser.add_argument('--no-open', action='store_true',
                        help='Do not open the browser automatically')
    parser.add_argument('--skip-seed', action='store_true',
                        help='Skip running seed.py')
    # >>> default AGORA É 8081 <<<
    parser.add_argument('--port', type=int, default=8081,
                        help='Frontend port (default 8081)')
    args = parser.parse_args()

    try:
        install_requirements()
    except subprocess.CalledProcessError:
        print("[run_local] WARNING: Failed to install requirements automatically. "
              "Please run pip install -r back-end/requirements.txt manually.")

    if not os.environ.get("DATABASE_URL") and not (ROOT / "local_config.json").exists():
        print("[run_local] No DATABASE_URL and no local_config.json found. "
              "Defaulting to sqlite://./app.db")

    if not args.skip_seed:
        ok = run_seed()
        if not ok:
            print("[run_local] Seed failed. Aborting.")
            sys.exit(2)

    frontend_port = args.port

    if not check_port_available(frontend_port):
        print(f"[run_local] ERROR: Port {frontend_port} is already in use.")
        print("Please close the application using this port or choose another with --port.")
        sys.exit(3)

    frontend_thread = threading.Thread(
        target=run_frontend_http,
        args=(frontend_port,),
        daemon=True
    )
    frontend_thread.start()

    if not args.no_open:
        try:
            time.sleep(0.5)
            webbrowser.open(f'http://localhost:{frontend_port}')
        except Exception:
            pass

    ret = run_backend()
    print(f"[run_local] Backend terminated with code {ret}")


if __name__ == '__main__':
    main()
