import subprocess
import sys
import time
import os

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
                break
            if frontend_process.poll() is not None:
                print("❌ ERRORE: Il Frontend si è fermato improvvisamente.")
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
