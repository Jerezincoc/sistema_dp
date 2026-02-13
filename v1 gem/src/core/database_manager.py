import json
import os
import shutil
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import logging

# Configuração básica de logger para o Core
logger = logging.getLogger("v1_gem.database")

class JsonDatabaseManager:
    """
    Gerenciador de persistência definitivo para a Fase 1 (JSON).
    Implementa Singleton, Thread Safety e operações em lote (Batch).
    """
    _instance = None
    _lock = threading.Lock() # Trava global para o Singleton
    
    def __new__(cls, data_dir: str = "data"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JsonDatabaseManager, cls).__new__(cls)
                cls._instance._init_manager(data_dir)
            return cls._instance

    def _init_manager(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # Travas individuais por tabela (arquivo) para permitir leitura/escrita simultânea em tabelas diferentes
        self._table_locks: Dict[str, threading.Lock] = {}

    def _get_table_lock(self, table_name: str) -> threading.Lock:
        with self._lock:
            if table_name not in self._table_locks:
                self._table_locks[table_name] = threading.Lock()
            return self._table_locks[table_name]
        
    def _get_file_path(self, table_name: str) -> Path:
        return self.data_dir / f"{table_name}.json"

    def read_table(self, table_name: str) -> Dict[str, Any]:
        """Lê os dados com proteção de concorrência e fallback de corrupção."""
        file_path = self._get_file_path(table_name)
        
        with self._get_table_lock(table_name):
            if not file_path.exists():
                return {}
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                backup_path = file_path.with_suffix('.json.corrupted')
                shutil.copy2(file_path, backup_path)
                logger.error(f"Arquivo {table_name}.json corrompido. Backup gerado em {backup_path.name}")
                return {}

    def write_table(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Escrita atômica e thread-safe."""
        file_path = self._get_file_path(table_name)
        temp_path = file_path.with_suffix('.json.tmp')
        
        with self._get_table_lock(table_name):
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                temp_path.replace(file_path)
                return True
            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink()
                logger.error(f"Erro Crítico ao salvar {table_name}: {str(e)}")
                return False

    def get_record(self, table_name: str, record_id: str) -> Optional[Dict[str, Any]]:
        data = self.read_table(table_name)
        return data.get(str(record_id))

    def save_record(self, table_name: str, record_id: str, record_data: Dict[str, Any]) -> bool:
        data = self.read_table(table_name)
        data[str(record_id)] = record_data
        return self.write_table(table_name, data)

    def batch_save(self, table_name: str, records: Dict[str, Dict[str, Any]]) -> bool:
        """Salva múltiplos registros de uma vez (ex: processamento de folha)."""
        data = self.read_table(table_name)
        data.update(records) # Atualiza/Insere em massa
        return self.write_table(table_name, data)

    def find_records(self, table_name: str, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        """Busca avançada passando uma função lambda de filtro."""
        data = self.read_table(table_name)
        return [record for record in data.values() if predicate(record)]

    def delete_record(self, table_name: str, record_id: str) -> bool:
        data = self.read_table(table_name)
        if str(record_id) in data:
            del data[str(record_id)]
            return self.write_table(table_name, data)
        return False