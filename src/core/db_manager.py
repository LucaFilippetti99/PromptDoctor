import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

class PromptDBManager:
    """
    Data Access Object (DAO) per la gestione dello storico dei prompt generati.
    Utilizza SQLite3 per una persistenza leggera e nativa.
    """
    
    def __init__(self, db_name: str = "prompts_history.db"):
        # Se vogliamo salvare il db in una cartella specifica (es. data), possiamo strutturarlo qui
        # Per ora lo salviamo nella root o nella cartella specificata.
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.db_path = os.path.join(project_root, db_name)
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Crea e restituisce una connessione al database."""
        return sqlite3.connect(self.db_path)

    def _initialize_db(self) -> None:
        """Inizializza le tabelle del database se non esistono."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompts_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    original_input TEXT NOT NULL,
                    generated_prompt TEXT NOT NULL,
                    score INTEGER NOT NULL
                )
            ''')
            conn.commit()

    def save_prompt(self, original_input: str, generated_prompt: str, score: int) -> int:
        """
        Inserisce un nuovo record di prompt generato nel database.
        
        Args:
            original_input (str): L'input originale dell'utente.
            generated_prompt (str): Il prompt completo generato in formato CO-STAR.
            score (int): Il punteggio ottenuto dal prompt.
            
        Returns:
            int: L'ID del record appena inserito.
        """
        timestamp = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prompts_history (timestamp, original_input, generated_prompt, score)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, original_input, generated_prompt, score))
            conn.commit()
            return cursor.lastrowid

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """
        Recupera tutti i record dei prompt salvati, dal più recente al più vecchio.
        
        Returns:
            List[Dict[str, Any]]: Una lista di dizionari, ognuno rappresentante un record salvato.
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row  # Permette di accedere ai campi come in un dizionario
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, timestamp, original_input, generated_prompt, score
                FROM prompts_history
                ORDER BY timestamp DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
