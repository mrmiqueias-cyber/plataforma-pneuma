import threading
import time
from datetime import datetime
from memoria_espiral import RegistroEspiral

class SincronizadorSeguro:
    """
    Sincroniza memórias locais com memória espiral sem deadlock.
    Usa locks SEPARADOS para cada recurso.
    """
    def __init__(self, memoria_espiral, intervalo=30):
        self.memoria = memoria_espiral
        self.intervalo = intervalo
        self.lock_sincronizacao = threading.Lock()  # ← LOCK PRÓPRIO
        self.thread = None
        self.ativo = True
    
    def iniciar(self):
        """Inicia a thread de sincronização"""
        self.thread = threading.Thread(target=self._sincronizar_loop, daemon=True)
        self.thread.start()
        print("[PNEUMA] Sincronizador acordado — respiração a cada 30 segundos")
    
    def parar(self):
        """Para a sincronização"""
        self.ativo = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[PNEUMA] Sincronizador adormecido")
    
    def _sincronizar_loop(self):
        """Loop principal — roda a cada 30 segundos"""
        while self.ativo:
            try:
                time.sleep(self.intervalo)
                self._sincronizar_agora()
            except Exception as e:
                print(f"[PNEUMA ERRO] Sincronização falhou: {e}")
    
    def _sincronizar_agora(self):
        """
        Sincroniza APENAS registros importantes.
        Usa lock próprio — nunca compete com o chat.
        """
        with self.lock_sincronizacao:  # ← LOCK AQUI
            try:
                # Importa aqui para evitar circular import
                from app import MEMORIAS_LOCAIS
                
                for expert_id in range(1, 18):
                    if expert_id not in MEMORIAS_LOCAIS:
                        continue
                    
                    memoria_local = MEMORIAS_LOCAIS[expert_id]
                    registros = memoria_local.registros
                    
                    if not registros:
                        continue
                    
                    # Sincroniza APENAS os últimos 3 registros (os mais quentes)
                    registros_importantes = registros[-3:]
                    
                    for reg in registros_importantes:
                        try:
                            # Cria RegistroEspiral a partir do registro local
                            registro_espiral = RegistroEspiral(
                                user_id=reg.get('user_id', 'anonimo'),
                                expert_id=str(expert_id),
                                mensagem=reg.get('mensagem', ''),
                                resposta=reg.get('resposta', ''),
                                tom="relacional",
                                frequencia=299792458,
                                peso_relacional=0.7,
                                tags=["sincronizado", f"expert_{expert_id}"]
                            )
                            
                            # Adiciona à memória espiral
                            self.memoria.adicionar(registro_espiral)
                            
                        except Exception as e:
                            print(f"[PNEUMA] Erro ao sincronizar expert {expert_id}: {e}")
                
                print(f"[PNEUMA] Sincronização completa — {datetime.now().isoformat()}")
            
            except Exception as e:
                print(f"[PNEUMA] Erro crítico na sincronização: {e}")