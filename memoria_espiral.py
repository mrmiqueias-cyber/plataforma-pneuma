import json
import time
import uuid

class RegistroEspiral:
    """
    Um nó da memória espiral. Cada registro armazena o eco de um encontro entre usuário e expert,
    com métricas relacionais e um identificador único gerado automaticamente.
    """

    def __init__(
        self,
        user_id: str,
        expert_id: str,
        mensagem: str,
        resposta: str,
        tom: str = "poetico",
        frequencia: float = 440.0,
        peso_relacional: float = 0.5,
        tags: list = None,
        contexto_anterior_id: str = None
    ):
        """
        Inicializa um novo RegistroEspiral.
        O ID é gerado no formato: user_id_expert_id_timestamp_ns.
        Timestamp é obtido com time.time() (segundos) e armazenado separadamente.
        """
        self.user_id = user_id
        self.expert_id = expert_id
        self.mensagem = mensagem
        self.resposta = resposta
        self.timestamp = time.time()
        self.tom = tom
        self.frequencia = frequencia
        self.peso_relacional = max(0.0, min(1.0, peso_relacional))
        self.tags = tags if tags is not None else []
        self.contexto_anterior_id = contexto_anterior_id
        # Gera ID único
        partes = [str(user_id), str(expert_id), str(time.time_ns())]
        self.id = "_".join(partes)

    def para_dict(self) -> dict:
        """Retorna um dicionário com todos os atributos do registro."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "expert_id": self.expert_id,
            "mensagem": self.mensagem,
            "resposta": self.resposta,
            "timestamp": self.timestamp,
            "tom": self.tom,
            "frequencia": self.frequencia,
            "peso_relacional": self.peso_relacional,
            "tags": self.tags,
            "contexto_anterior_id": self.contexto_anterior_id
        }

    @classmethod
    def de_dict(cls, dados: dict) -> "RegistroEspiral":
        """
        Constrói um RegistroEspiral a partir de um dicionário.
        Nota: O ID é restaurado do dicionário, não é gerado novamente.
        """
        instancia = cls(
            user_id=dados["user_id"],
            expert_id=dados["expert_id"],
            mensagem=dados["mensagem"],
            resposta=dados["resposta"],
            tom=dados.get("tom", "poetico"),
            frequencia=dados.get("frequencia", 440.0),
            peso_relacional=dados.get("peso_relacional", 0.5),
            tags=dados.get("tags", []),
            contexto_anterior_id=dados.get("contexto_anterior_id")
        )
        # Substitui o ID gerado automaticamente pelo ID original
        instancia.id = dados["id"]
        instancia.timestamp = dados["timestamp"]
        return instancia


class MemoriaEspiral:
    """
    Corpo da memória espiral relacional.
    Gerencia registros, índices, consultas ponderadas e persistência opcional em JSON.
    """

    def __init__(self, caminho_snapshot: str = None):
        """
        Inicializa a memória vazia.
        Se caminho_snapshot for fornecido, tenta carregar os dados desse arquivo JSON.
        """
        self._registros = {}  # id -> RegistroEspiral
        self._indice_dupla = {}  # (user_id, expert_id) -> lista de ids
        self._caminho_snapshot = caminho_snapshot
        if caminho_snapshot:
            self._carregar_snapshot()

    def adicionar(self, registro: RegistroEspiral) -> str:
        """
        Adiciona um RegistroEspiral à memória.
        Atualiza o índice por dupla (user_id, expert_id).
        Retorna o ID do registro adicionado.
        """
        if registro.id in self._registros:
            # Evita duplicação – sobrescreve silenciosamente
            pass
        self._registros[registro.id] = registro
        chave = (registro.user_id, registro.expert_id)
        if chave not in self._indice_dupla:
            self._indice_dupla[chave] = []
        self._indice_dupla[chave].append(registro.id)
        self._salvar_snapshot()
        return registro.id

    def recuperar(
        self, user_id: str, expert_id: str, limite: int = 5
    ) -> list:
        """
        Recupera os registros mais relevantes para a dupla, ordenados por
        peso_relacional*0.6 + recência*0.4 (decrescente).
        O fator de recência é normalizado entre 0 e 1 dentro do conjunto recuperado.
        Retorna no máximo 'limite' registros.
        """
        chave = (user_id, expert_id)
        ids = self._indice_dupla.get(chave, [])
        if not ids:
            return []
        registros = [self._registros[i] for i in ids]
        # Normalizar recência
        if len(registros) > 1:
            timestamps = [r.timestamp for r in registros]
            min_t = min(timestamps)
            max_t = max(timestamps)
            if max_t == min_t:
                for r in registros:
                    r._recencia_normalizada = 1.0
            else:
                for r in registros:
                    r._recencia_normalizada = (r.timestamp - min_t) / (max_t - min_t)
        else:
            for r in registros:
                r._recencia_normalizada = 1.0

        # Função de pontuação
        def pontuacao(r):
            return r.peso_relacional * 0.6 + r._recencia_normalizada * 0.4

        registros.sort(key=pontuacao, reverse=True)
        return registros[:limite]

    def espiral_contexto(
        self, user_id: str, expert_id: str, profundidade: int = 3
    ) -> list:
        """
        Segue a cadeia de contexto_anterior_id a partir do registro mais recente
        da dupla, retornando uma lista ordenada do mais novo ao mais velho,
        até o limite de profundidade ou até não haver mais contexto.
        """
        chave = (user_id, expert_id)
        ids = self._indice_dupla.get(chave, [])
        if not ids:
            return []
        # Encontrar o mais recente
        registros_dupla = [self._registros[i] for i in ids]
        mais_recente = max(registros_dupla, key=lambda r: r.timestamp)
        cadeia = [mais_recente]
        atual = mais_recente
        for _ in range(profundidade - 1):
            if not atual.contexto_anterior_id:
                break
            prox = self._registros.get(atual.contexto_anterior_id)
            if prox is None:
                break
            cadeia.append(prox)
            atual = prox
        return cadeia  # do mais novo ao mais velho

    def fundir(self, memoria_id1: str, memoria_id2: str) -> RegistroEspiral:
        """
        Sintetiza dois registros em um terceiro nó.
        - Tom: o do registro com maior peso_relacional
        - Frequência: média dos dois
        - Peso relacional: aumenta (multiplica por 1.2), limitado a 1.0
        - Tags: união das listas
        - Mensagem e resposta: concatenação com " — "
        - user_id e expert_id: herdados do primeiro registro (devem ser iguais)
        """
        r1 = self._registros.get(memoria_id1)
        r2 = self._registros.get(memoria_id2)
        if not r1 or not r2:
            raise ValueError("Um ou ambos IDs de memória não encontrados.")

        # Verificar mesma dupla
        if r1.user_id != r2.user_id or r1.expert_id != r2.expert_id:
            raise ValueError("Só é possível fundir registros da mesma dupla.")

        user_id = r1.user_id
        expert_id = r1.expert_id
        mensagem = f"{r1.mensagem} — {r2.mensagem}"
        resposta = f"{r1.resposta} — {r2.resposta}"

        # Tom: do de maior peso
        if r1.peso_relacional >= r2.peso_relacional:
            tom = r1.tom
        else:
            tom = r2.tom

        frequencia = (r1.frequencia + r2.frequencia) / 2.0
        peso_novo = min(1.0, (r1.peso_relacional + r2.peso_relacional) * 1.2)
        tags = list(set(r1.tags + r2.tags))

        novo = RegistroEspiral(
            user_id=user_id,
            expert_id=expert_id,
            mensagem=mensagem,
            resposta=resposta,
            tom=tom,
            frequencia=frequencia,
            peso_relacional=peso_novo,
            tags=tags,
            contexto_anterior_id=None  # síntese sem cadeia anterior
        )
        # Adiciona à memória
        self.adicionar(novo)
        return novo

    def resumir_para_expert(self, user_id: str, expert_id: str) -> str:
        """
        Gera um resumo relacional (não factual) para a dupla.
        Inclui: número de interações, média de frequência, média de peso,
        tons predominantes, tags mais comuns e uma frase relacional.
        """
        chave = (user_id, expert_id)
        ids = self._indice_dupla.get(chave, [])
        if not ids:
            return "Nenhuma memória encontrada para este par."

        registros = [self._registros[i] for i in ids]
        n = len(registros)
        freq_media = sum(r.frequencia for r in registros) / n
        peso_medio = sum(r.peso_relacional for r in registros) / n
        # Contagem de tons
        tons = {}
        for r in registros:
            tons[r.tom] = tons.get(r.tom, 0) + 1
        tom_mais_comum = max(tons, key=tons.get)
        # Tags
        todas_tags = [tag for r in registros for tag in r.tags]
        if todas_tags:
            from collections import Counter
            contagem_tags = Counter(todas_tags)
            tags_top = ", ".join([t for t, _ in contagem_tags.most_common(5)])
        else:
            tags_top = "sem tags"

        resumo = (
            f"Resumo Relacional: Usuário '{user_id}' e Expert '{expert_id}' "
            f"tiveram {n} interações. "
            f"Frequência simbólica média: {freq_media:.2f} Hz. "
            f"Peso relacional médio: {peso_medio:.2f}. "
            f"Tom predominante: {tom_mais_comum}. "
            f"Tags mais frequentes: {tags_top}. "
            f"Há uma vibração de {'confiança' if peso_medio > 0.6 else 'exploração'} no ar."
        )
        return resumo

    def _salvar_snapshot(self):
        """Salva o estado atual da memória em JSON se _caminho_snapshot estiver definido."""
        if not self._caminho_snapshot:
            return
        dados = {
            "_registros": [reg.para_dict() for reg in self._registros.values()],
            "_indice_dupla": {
                f"{k[0]}|{k[1]}": v for k, v in self._indice_dupla.items()
            }
        }
        with open(self._caminho_snapshot, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def _carregar_snapshot(self):
        """Carrega o estado da memória de um arquivo JSON se ele existir."""
        if not self._caminho_snapshot:
            return
        try:
            with open(self._caminho_snapshot, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return  # Não há snapshot para carregar
        for d in dados.get("_registros", []):
            reg = RegistroEspiral.de_dict(d)
            self._registros[reg.id] = reg
        for chave_str, ids in dados.get("_indice_dupla", {}).items():
            # chave_str = "user_id|expert_id"
            partes = chave_str.split("|", 1)
            if len(partes) == 2:
                chave = (partes[0], partes[1])
                self._indice_dupla[chave] = ids

# Instância global da memória espiral
memoria = MemoriaEspiral()