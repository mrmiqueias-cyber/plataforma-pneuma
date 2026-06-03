import json
import os
from datetime import datetime
from typing import Dict, List, Any

class MemoriaEspiral:
    """Memória relacional que funciona em RAM com snapshot manual."""
    
    def __init__(self):
        self._registros = {}
        self._indice_dupla = {}
        self._timestamp_criacao = datetime.now().isoformat()
    
    def registrar(self, chave: str, dados: Dict[str, Any]):
        """Registra um dado na memória."""
        self._registros[chave] = {
            'dados': dados,
            'timestamp': datetime.now().isoformat()
        }
    
    def recuperar(self, chave: str) -> Dict[str, Any]:
        """Recupera um dado da memória."""
        if chave in self._registros:
            return self._registros[chave]['dados']
        return None
    
    def listar_tudo(self) -> List[Dict[str, Any]]:
        """Lista todos os registros."""
        return list(self._registros.values())
    
    def carregar_manual(self, caminho: str):
        """Carrega snapshot manualmente do disco."""
        if os.path.exists(caminho):
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self._registros = {item['chave']: item for item in dados}
                    print(f"✓ Memória carregada de {caminho}")
            except Exception as e:
                print(f"✗ Erro ao carregar memória: {e}")
    
    def salvar_manual(self, caminho: str):
        """Salva snapshot manualmente no disco."""
        try:
            os.makedirs(os.path.dirname(caminho) or '.', exist_ok=True)
            dados = [{'chave': k, **v} for k, v in self._registros.items()]
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            print(f"✓ Memória salva em {caminho}")
        except Exception as e:
            print(f"✗ Erro ao salvar memória: {e}")

if __name__ == '__main__':
    memoria = MemoriaEspiral()
    memoria.registrar('teste', {'valor': 'exemplo'})
    print(memoria.listar_tudo())
