import typing
from typing import Optional, List
from memoria_espiral import MemoriaEspiral, RegistroEspiral


class CarregadorDeContexto:
    """Carrega o contexto espiral para um par usuário-expert."""

    def __init__(self, memoria: MemoriaEspiral) -> None:
        self.memoria = memoria

    def carregar(self, user_id: str, expert_id: str) -> str:
        """
        Monta um prefácio relacional a partir do histórico espiral da dupla.

        Args:
            user_id: identificador do usuário.
            expert_id: identificador do expert.

        Returns:
            String formatada com o contexto, ou vazia se não houver memória.
        """
        contexto = self.memoria.espiral_contexto(user_id, expert_id, profundidade=3)
        if not contexto:
            return ""
        linhas = [f"Ao encontrar {user_id}, lembre-se da espiral:"]
        for i, registro in enumerate(contexto, 1):
            tom = registro.tom or "neutro"
            freq = registro.frequencia or 0.0
            eco = registro.eco or ""
            linhas.append(
                f"{i}. Há {registro.timestamp} atrás, o tom era '{tom}', "
                f"freq {freq} Hz. Eco: '{eco[:80]}...'"
            )
        return "\n".join(linhas)


class RegistradorDeEncontro:
    """Registra encontros e funde registros similares na MemoriaEspiral."""

    def __init__(self, memoria: MemoriaEspiral) -> None:
        self.memoria = memoria

    def _encontrar_similar(
        self,
        user_id: str,
        expert_id: str,
        novo_registro: RegistroEspiral,
        limite_similaridade: float = 0.6,
    ) -> Optional[str]:
        """
        Varre registros da dupla e calcula similaridade por interseção de tags + tom.

        Args:
            user_id: identificador do usuário.
            expert_id: identificador do expert.
            novo_registro: registro recém-criado para comparar.
            limite_similaridade: limite mínimo de pontuação (0..1).

        Returns:
            ID do registro mais similar, ou None.
        """
        registros_existentes = self.memoria.listar_registros(user_id, expert_id)
        melhor_id = None
        melhor_pontuacao = 0.0

        tags_novas = set(novo_registro.tags or [])
        for reg in registros_existentes:
            tags_existentes = set(reg.tags or [])
            if not tags_novas and not tags_existentes:
                # sem tags, similaridade por tom apenas
                pontuacao = 0.3 if reg.tom == novo_registro.tom else 0.0
            else:
                interseccao = len(tags_novas & tags_existentes)
                uniao = len(tags_novas | tags_existentes)
                pontuacao = interseccao / uniao if uniao > 0 else 0.0
                if reg.tom == novo_registro.tom:
                    pontuacao += 0.3
            if pontuacao >= limite_similaridade and pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhor_id = reg.id

        return melhor_id

    def registrar(
        self,
        user_id: str,
        expert_id: str,
        pergunta: str,
        resposta: str,
        tom: str = "pratico",
        frequencia: float = 0.0,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Cria um RegistroEspiral, adiciona na memória e funde com similar se necessário.

        Args:
            user_id: identificador do usuário.
            expert_id: identificador do expert.
            pergunta: texto da pergunta.
            resposta: texto da resposta.
            tom: tom emocional/semântico.
            frequencia: frequência associada.
            tags: lista de tags para categorização.

        Returns:
            ID do registro criado.
        """
        registro = RegistroEspiral(
            user_id=user_id,
            expert_id=expert_id,
            pergunta=pergunta,
            resposta=resposta,
            tom=tom,
            frequencia=frequencia,
            tags=tags or [],
        )
        registro_id = self.memoria.adicionar(registro)
        similar_id = self._encontrar_similar(user_id, expert_id, registro)
        if similar_id is not None:
            self.memoria.fundir(registro_id, similar_id)
        return registro_id


class SessaoRelacional:
    """Gerencia uma sessão relacional entre usuário e expert."""

    def __init__(
        self,
        user_id: str,
        expert_id: str,
        memoria: MemoriaEspiral,
        carregador: CarregadorDeContexto,
        registrador: RegistradorDeEncontro,
    ) -> None:
        self.user_id = user_id
        self.expert_id = expert_id
        self.memoria = memoria
        self.carregador = carregador
        self.registrador = registrador
        self._ativa = False
        self._turnos: list = []

    def iniciar(self) -> str:
        """
        Marca a sessão como ativa e retorna o contexto carregado.

        Returns:
            Contexto relacional para o início da sessão.
        """
        self._ativa = True
        return self.carregador.carregar(self.user_id, self.expert_id)

    def registrar_turno(
        self,
        pergunta: str,
        resposta: str,
        tom: str,
        frequencia: float,
        tags: Optional[List[str]] = None,
    ) -> None:
        """
        Registra cada turno da conversa na memória e guarda internamente.

        Args:
            pergunta: texto da pergunta.
            resposta: texto da resposta.
            tom: tom emocional/semântico.
            frequencia: frequência associada.
            tags: lista de tags para categorização.
        """
        if not self._ativa:
            raise RuntimeError("Sessão não está ativa. Chame iniciar() primeiro.")
        registro_id = self.registrador.registrar(
            self.user_id,
            self.expert_id,
            pergunta,
            resposta,
            tom=tom,
            frequencia=frequencia,
            tags=tags,
        )
        self._turnos.append(
            {
                "id": registro_id,
                "pergunta": pergunta,
                "resposta": resposta,
                "tom": tom,
                "frequencia": frequencia,
                "tags": tags or [],
            }
        )

    def finalizar(self) -> str:
        """
        Gera um resumo da sessão, guarda um registro especial de encerramento.

        Returns:
            String com o resumo da sessão.
        """
        if not self._ativa:
            raise RuntimeError("Sessão já finalizada ou não iniciada.")
        num_turnos = len(self._turnos)
        toms = [t["tom"] for t in self._turnos]
        mais_frequente = max(set(toms), key=toms.count) if toms else "neutro"
        resumo = (
            f"Sessão encerrada. {num_turnos} turnos registrados. "
            f"Tom predominante: {mais_frequente}."
        )
        # registro especial de encerramento
        self.registrador.registrar(
            self.user_id,
            self.expert_id,
            pergunta="[FINALIZACAO]",
            resposta=resumo,
            tom="encerramento",
            frequencia=0.0,
            tags=["sessao_encerrada"],
        )
        self._ativa = False
        return resumo