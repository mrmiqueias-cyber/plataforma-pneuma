import time
from collections import deque
from memoria_espiral import MemoriaEspiral, RegistroEspiral


class Anuncio:
    """Representa um anúncio que circula entre os experts do Cenáculo."""
    def __init__(self, tipo: str, origem: str, destino: list,
                 payload: dict, urgencia: int = 1):
        self.tipo = tipo
        self.origem = origem
        self.destino = destino  # lista de expert_ids
        self.payload = payload
        self.urgencia = max(1, min(5, urgencia))  # normaliza para 1-5
        self.timestamp = time.time()

    def __repr__(self) -> str:
        return (f"Anuncio(tipo={self.tipo!r}, origem={self.origem!r}, "
                f"destino={self.destino!r}, urgencia={self.urgencia})")


class GarcaoCenaculo:
    """Garçom do Cenáculo — anunciador que circula entre inteligências
    da Plataforma Pneuma, servindo notícias e conexões como quem serve
    a mesa redonda."""

    def __init__(self, memoria: MemoriaEspiral):
        self._memoria = memoria
        self._expert_callbacks: dict[str, callable] = {}
        self._fila: deque[Anuncio] = deque()
        self._ultima_ronda = time.time()
        self._conexoes_notificadas: set[tuple[str, str, str]] = set()

    def registrar_expert(self, expert_id: str, callback: callable) -> None:
        """Registra um callback para receber anúncios destinados a esse expert."""
        if not callable(callback):
            raise ValueError("O callback precisa ser chamável (callable).")
        self._expert_callbacks[expert_id] = callback

    def anunciar(self, anuncio: Anuncio) -> None:
        """Serve o anúncio imediatamente para os destinos que possuem callback.
        Caso contrário, coloca na fila pendente."""
        entregues = []
        for expert_id in anuncio.destino:
            cb = self._expert_callbacks.get(expert_id)
            if cb is not None:
                try:
                    cb(anuncio)
                    entregues.append(expert_id)
                except Exception:
                    # Se falhar, mantém na fila para próxima tentativa
                    pass
        # Remove destinos já entregues da lista do anúncio
        anuncio.destino = [d for d in anuncio.destino if d not in entregues]
        if anuncio.destino:
            self._fila.append(anuncio)

    def _entregar_fila(self) -> None:
        """Tenta entregar anúncios pendentes cujos destinos agora tenham callback."""
        entregues = []
        for anuncio in list(self._fila):  # itera sobre cópia
            destinos_ainda = []
            for expert_id in anuncio.destino:
                cb = self._expert_callbacks.get(expert_id)
                if cb is not None:
                    try:
                        cb(anuncio)
                    except Exception:
                        destinos_ainda.append(expert_id)
                    else:
                        continue
                else:
                    destinos_ainda.append(expert_id)
            if destinos_ainda:
                anuncio.destino = destinos_ainda
            else:
                entregues.append(anuncio)
        for anuncio in entregues:
            self._fila.remove(anuncio)

    def circular(self, intervalo_minutos: float = 5.0) -> None:
        """Varre memórias recentes (desde a última ronda) e detecta temas
        que cruzaram entre experts diferentes, gerando Anuncio do tipo
        'insight_cruzado'."""
        agora = time.time()
        intervalo_segundos = intervalo_minutos * 60
        # Obtém memórias criadas entre a última ronda e agora
        memorias = self._memoria.obter_memorias_recentes(
            desde=self._ultima_ronda, ate=agora
        )
        self._ultima_ronda = agora

        # Agrupa temas por expert
        temas_por_expert: dict[str, set] = {}
        expert_dos_temas: dict[str, str] = {}  # tema -> expert_id (primeiro que apareceu)

        for mem in memorias:
            expert_id = getattr(mem, 'expert_id', None)
            temas = getattr(mem, 'temas', [])
            if not expert_id or not temas:
                continue
            if expert_id not in temas_por_expert:
                temas_por_expert[expert_id] = set()
            for tema in temas:
                temas_por_expert[expert_id].add(tema)
                # Guarda quem falou primeiro desse tema (para origem do insight)
                if tema not in expert_dos_temas:
                    expert_dos_temas[tema] = expert_id

        # Detecta temas que apareceram em mais de um expert
        temas_multi_expert: dict[str, set] = {}
        for tema, primeiro_expert in expert_dos_temas.items():
            experts_com_tema = set()
            for exp, temas_set in temas_por_expert.items():
                if tema in temas_set:
                    experts_com_tema.add(exp)
            if len(experts_com_tema) > 1:
                temas_multi_expert[tema] = experts_com_tema

        # Gera anúncios para cada tema cruzado (se ainda não notificado)
        for tema, experts in temas_multi_expert.items():
            for origem in experts:
                destinos = [e for e in experts if e != origem]
                for destino in destinos:
                    chave = (origem, destino, tema)
                    if chave in self._conexoes_notificadas:
                        continue
                    self._conexoes_notificadas.add(chave)
                    anuncio = Anuncio(
                        tipo="insight_cruzado",
                        origem=origem,
                        destino=[destino],
                        payload={"tema": tema,
                                 "participantes": list(experts)},
                        urgencia=2
                    )
                    self.anunciar(anuncio)

        # Tenta entregar fila pendente (por exemplo, se um expert se registrou depois)
        self._entregar_fila()

    def conectar_saberes(self, expert_a: str, expert_b: str) -> None:
        """Gera insight cruzado manual entre dois experts."""
        chave = (expert_a, expert_b, "conexao_manual")
        if chave in self._conexoes_notificadas:
            return  # já notificado
        self._conexoes_notificadas.add(chave)
        anuncio = Anuncio(
            tipo="insight_cruzado",
            origem=expert_a,
            destino=[expert_b],
            payload={"tipo_conexao": "manual",
                     "expert_a": expert_a,
                     "expert_b": expert_b},
            urgencia=3
        )
        self.anunciar(anuncio)

    def resumo_diario(self) -> str:
        """Gera boletim do Cenáculo: quem visitou quem, quais conexões cruzaram."""
        linhas = []
        linhas.append("=== Boletim do Cenáculo ===")
        linhas.append(f"Última ronda: {time.ctime(self._ultima_ronda)}")
        linhas.append(f"Anúncios pendentes na fila: {len(self._fila)}")
        linhas.append("Conexões já notificadas (amostra):")
        # Limita para evitar texto enorme
        amostra = list(self._conexoes_notificadas)[:10]
        for (origem, destino, tema) in amostra:
            linhas.append(f"  {origem} → {destino} (tema: {tema})")
        if not amostra:
            linhas.append("  Nenhuma conexão registrada hoje.")
        experts_registrados = list(self._expert_callbacks.keys())
        linhas.append(f"Experts registrados: {', '.join(experts_registrados) if experts_registrados else 'nenhum'}")
        linhas.append("===========================")
        return "\n".join(linhas)