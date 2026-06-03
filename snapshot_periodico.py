import threading
import time
import os
from datetime import datetime
from typing import Optional

class SnapshotManager:
    """Gerencia snapshots periódicos da memória espiral."""
    
    def __init__(self, memoria, caminho_base: str, intervalo_horas: int = 6):
        self.memoria = memoria
        self.caminho_base = caminho_base
        self.intervalo_segundos = intervalo_horas * 3600
        self.thread = None
        self.ativo = False
    
    def iniciar(self):
        """Inicia o gerenciador de snapshots em thread separada."""
        if self.ativo:
            return
        
        self.ativo = True
        self.thread = threading.Thread(target=self._loop_snapshot, daemon=True)
        self.thread.start()
        print(f"✓ SnapshotManager iniciado — snapshot a cada {self.intervalo_segundos // 3600}h")
    
    def parar(self):
        """Para o gerenciador de snapshots."""
        self.ativo = False
        if self.thread:
            self.thread.join(timeout=5)
        print("✓ SnapshotManager parado")
    
    def _loop_snapshot(self):
        """Loop que salva snapshot periodicamente."""
        while self.ativo:
            try:
                time.sleep(self.intervalo_segundos)
                if self.ativo:
                    self._salvar_snapshot()
            except Exception as e:
                print(f"✗ Erro no loop de snapshot: {e}")
    
    def _salvar_snapshot(self):
        """Salva um snapshot da memória."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(self.caminho_base, exist_ok=True)
            caminho = os.path.join(self.caminho_base, f"memoria_{timestamp}.json")
            self.memoria.salvar_manual(caminho)
            print(f"✓ Snapshot salvo: {caminho}")
        except Exception as e:
            print(f"✗ Erro ao salvar snapshot: {e}")

if __name__ == '__main__':
    from memoria_espiral_persistente import MemoriaEspiral
    
    memoria = MemoriaEspiral()
    memoria.registrar('teste', {'valor': 'exemplo'})
    
    manager = SnapshotManager(memoria, "snapshots/memoria", intervalo_horas=1)
    manager.iniciar()
    
    print("Aguardando 5 segundos...")
    time.sleep(5)
    manager.parar()
