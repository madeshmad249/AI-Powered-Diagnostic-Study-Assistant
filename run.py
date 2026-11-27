import os
import sys
import socket
import subprocess

def find_free_port(start_port=8000):
    for port in range(start_port, start_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start_port

def main():
    port = find_free_port(8000)

    print("=" * 70)
    print("🚀 Starting GapFinder AI - AI-Powered Diagnostic Study Assistant")
    print("=" * 70)
    print("👤 Demo User: student@demo.com")
    print("🔑 Password:  demo123")
    print(f"🌐 Full-stack Web App: http://127.0.0.1:{port}")
    print(f"📚 API Docs:            http://127.0.0.1:{port}/docs")
    print("=" * 70)

    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    
    # Auto-seed if not seeded
    print("Verifying database & vector store status...")
    subprocess.run([sys.executable, "seed_demo.py"], cwd=backend_dir)

    print(f"\nStarting Uvicorn server on http://127.0.0.1:{port} ...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "127.0.0.1", 
        "--port", str(port),
        "--reload"
    ], cwd=backend_dir)

if __name__ == "__main__":
    main()
