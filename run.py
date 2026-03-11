import subprocess
import sys
import time
import os

def kill_process_on_port(port):
    try:
        # Trova il PID del processo che usa la porta (Windows)
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        killed = False
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                pid = parts[-1]
                if pid != "0":
                    print(f"[*] Termino il processo {pid} in ascolto sulla porta {port}...")
                    subprocess.run(['taskkill', '/PID', pid, '/F'], capture_output=True)
                    killed = True
        if killed:
            time.sleep(1) # Attendiamo che la porta sia liberata dal sistema
    except Exception as e:
        print(f"Errore nella pulizia della porta {port}: {e}")

def start_backend():
    print("Avvio del Backend (FastAPI)...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def start_frontend():
    print("Avvio del Frontend (Streamlit)...")
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "src/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

if __name__ == "__main__":
    print("🤖 Avvio PromptDoctor Client/Server 🤖")
    print("-" * 40)
    
    # Libera le porte dai vecchi processi appesi
    kill_process_on_port(8000)
    kill_process_on_port(8501)
    
    backend_process = None
    frontend_process = None
    
    try:
        # Avvia il backend
        backend_process = start_backend()
        
        # Attendi qualche secondo per assicurare che il db e Uvicorn partano
        print("Attendo 3 secondi per l'avvio del server REST API...")
        time.sleep(3)
        
        # Avvia il frontend
        frontend_process = start_frontend()
        
        print("-" * 40)
        print("✅ Tutti i servizi sono in esecuzione!")
        print(" - Backend API: http://localhost:8000/docs")
        print(" - Frontend UI: http://localhost:8501")
        print("\nPremi Ctrl+C per fermare tutti i servizi.")
        print("-" * 40)
        
        # Mantieni vivo lo script e ascolta i processi
        while True:
            time.sleep(1)
            
            # Se uno dei due dovesse crashare, ferma tutto
            if backend_process.poll() is not None:
                print("❌ ERRORE: Il Backend si è fermato improvvisamente.")
                stderr = backend_process.stderr.read()
                print(f"Dettagli errore:\n{stderr}")
                break
            if frontend_process.poll() is not None:
                print("❌ ERRORE: Il Frontend si è fermato improvvisamente.")
                stderr = frontend_process.stderr.read()
                print(f"Dettagli errore:\n{stderr}")
                break

    except KeyboardInterrupt:
        print("\nArresto manuale richiesto...")
        
    finally:
        print("Terminazione dei processi in corso...")
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        print("Procedura di spegnimento completata.")
