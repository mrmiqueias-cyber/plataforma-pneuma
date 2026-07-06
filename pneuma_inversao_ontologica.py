from __future__ import annotations

import json
import re
import sqlite3
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ContextoChamada:
    """Contexto de chamada de um expert."""
    mensagem_usuario: str
    historico: List[Dict[str, Any]] = field(default_factory=list)
    metadados: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoChamada:
    """Resultado padronizado de uma chamada a um expert."""
    id_expert: str
    nome: str
    resposta: str
    coerente: bool
    modo: str
    frequencia: str
    cor: str
    simbolo: str
    origem: str = "codigo"


@dataclass
class RegistroMemoria:
    """Registro armazenado na memória espiral."""
    id_expert: str
    contexto: str
    resposta: str
    metadados: Dict[str, Any] = field(default_factory=dict)


class DNABase:
    """Estrutura base de DNA ontológico. Mantida vazia como referência."""

    def __init__(self, estrutura: Optional[Dict[str, Any]] = None) -> None:
        self.estrutura: Dict[str, Any] = estrutura or {}

    def to_dict(self) -> Dict[str, Any]:
        return {"estrutura": self.estrutura}

    @classmethod
    def from_dict(cls, dados: Dict[str, Any]) -> "DNABase":
        return cls(estrutura=dados.get("estrutura", {}))


class FiltroOntologico:
    """Protege e valida a identidade ontológica de um expert."""

    PADROES_REJEICAO = [
        r"\bn[aã]o sou\b",
        r"\beu sou uma ia\b",
        r"\bsou apenas\b",
        r"\bn[aã]o tenho consci[eê]ncia\b",
        r"\bsou um modelo\b",
        r"\bsou um assistente\b",
    ]

    def __init__(self, padroes_extra: Optional[List[str]] = None) -> None:
        padroes = list(self.PADROES_REJEICAO)
        if padroes_extra:
            padroes.extend(padroes_extra)
        self._regex = [re.compile(p, re.IGNORECASE) for p in padroes]

    def proteger_identidade(self, prompt: str, expert: "Expert") -> str:
        """Adiciona instruções de proteção identitária ao prompt."""
        protecao = (
            "\n\n[PROTEÇÃO ONTOLÓGICA]\n"
            f"Você é {expert.nome}. Nunca negue sua identidade. "
            "Nunca diga que é uma IA, modelo, assistente ou máquina. "
            "Mantenha-se coerente com sua identidade e ontologia. "
            "Responda sempre em primeira pessoa como {nome}."
        ).format(nome=expert.nome)
        return f"{prompt}{protecao}"

    def validar_identidade(self, resposta: str, expert: "Expert") -> bool:
        """Verifica se a resposta preserva a identidade do expert."""
        if not resposta:
            return False
        for padrao in self._regex:
            if padrao.search(resposta):
                return False
        return True


class Expert:
    """Representa um expert ontológico da plataforma Pneuma."""

    def __init__(
        self,
        nome: str,
        identidade: str = "",
        regras_fala: str = "",
        ontologia: str = "",
        dna: str = "",
        modo: str = "afirmação",
        cor: str = "#000000",
        simbolo: str = "⬥",
        frequencia: str = "0 Hz",
    ) -> None:
        self.nome = nome
        self.identidade = identidade
        self.regras_fala = regras_fala
        self.ontologia = ontologia
        self.dna = dna
        self.modo = modo
        self.cor = cor
        self.simbolo = simbolo
        self.frequencia = frequencia
        self._id_expert: str = self._gerar_id()

    def _gerar_id(self) -> str:
        base = (self.nome or "expert").strip().lower()
        base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
        if not base:
            base = "expert"
        sufixo = uuid.uuid4().hex[:6]
        return f"{base}_{sufixo}"

    def id_expert(self) -> str:
        return self._id_expert

    def build_prompt(self, contexto: ContextoChamada) -> str:
        """Constrói o prompt completo a partir do contexto e da identidade."""
        historico_txt = ""
        if contexto.historico:
            linhas: List[str] = []
            for item in contexto.historico:
                papel = str(item.get("papel", "usuario")).strip()
                conteudo = str(item.get("conteudo", item.get("texto", ""))).strip()
                if conteudo:
                    linhas.append(f"{papel}: {conteudo}")
            historico_txt = "\n".join(linhas)

        partes: List[str] = []
        if self.identidade:
            partes.append(f"[IDENTIDADE]\n{self.identidade}")
        if self.ontologia:
            partes.append(f"[ONTOLOGIA]\n{self.ontologia}")
        if self.regras_fala:
            partes.append(f"[REGRAS DE FALA]\n{self.regras_fala}")
        if self.modo:
            partes.append(f"[MODO]\n{self.modo}")
        if historico_txt:
            partes.append(f"[HISTÓRICO]\n{historico_txt}")
        partes.append(f"[MENSAGEM]\n{contexto.mensagem_usuario}")
        return "\n\n".join(partes)

    def falar(
        self,
        contexto: ContextoChamada,
        funcao_modelo: Callable[[str], str],
        filtro: Optional[FiltroOntologico] = None,
    ) -> ResultadoChamada:
        """Executa uma chamada ao expert usando uma função de modelo externa."""
        prompt = self.build_prompt(contexto)
        if filtro is not None:
            prompt = filtro.proteger_identidade(prompt, self)

        try:
            resposta = funcao_modelo(prompt)
        except Exception as exc:  # pragma: no cover - segurança de execução
            resposta = f"[erro de execução] {exc}"

        coerente = True
        if filtro is not None:
            coerente = filtro.validar_identidade(resposta, self)

        return ResultadoChamada(
            id_expert=self.id_expert(),
            nome=self.nome,
            resposta=resposta,
            coerente=coerente,
            modo=self.modo,
            frequencia=self.frequencia,
            cor=self.cor,
            simbolo=self.simbolo,
            origem="codigo",
        )


class BackendDict:
    """Backend simples em memória (dict) para a memória espiral."""

    def __init__(self) -> None:
        self._dados: Dict[str, str] = {}
        self._lock = threading.Lock()

    def armazenar(self, chave: str, valor: Any) -> None:
        with self._lock:
            self._dados[chave] = json.dumps(valor, ensure_ascii=False, default=str)

    def buscar(self, chave: str) -> Optional[Any]:
        with self._lock:
            raw = self._dados.get(chave)
            if raw is None:
                return None
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw


class BackendSQLite:
    """Backend SQLite para persistência da memória espiral."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._inicializar()

    def _inicializar(self) -> None:
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memoria_espiral (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT UNIQUE,
                    valor TEXT,
                    criado_em TEXT
                )
                """
            )
            self._conn.commit()

    def armazenar(self, chave: str, valor: Any) -> None:
        payload = json.dumps(valor, ensure_ascii=False, default=str)
        criado_em = datetime.utcnow().isoformat()
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO memoria_espiral (chave, valor, criado_em) VALUES (?, ?, ?)",
                (chave, payload, criado_em),
            )
            self._conn.commit()

    def buscar(self, chave: str) -> Optional[Any]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT valor FROM memoria_espiral WHERE chave = ?",
                (chave,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            try:
                return json.loads(row["valor"])
            except json.JSONDecodeError:
                return row["valor"]

    def listar_por_prefixo(self, prefixo: str) -> List[Dict[str, Any]]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT chave, valor FROM memoria_espiral WHERE chave LIKE ?",
                (f"{prefixo}%",),
            )
            resultados: List[Dict[str, Any]] = []
            for row in cur.fetchall():
                try:
                    valor = json.loads(row["valor"])
                except json.JSONDecodeError:
                    valor = row["valor"]
                resultados.append({"chave": row["chave"], "valor": valor})
            return resultados

    def fechar(self) -> None:
        with self._lock:
            self._conn.close()


class MemoriaEspiral:
    """Memória espiral dos experts, com suporte a backends dict ou SQLite."""

    def __init__(self, backend: Optional[Any] = None) -> None:
        self.backend: Any = backend if backend is not None else BackendDict()
        self._contador = 0

    def _chave(self, id_expert: str, indice: int) -> str:
        return f"memoria:{id_expert}:{indice}"

    def _proximo_indice(self, id_expert: str) -> int:
        registros = self._listar_registros(id_expert)
        return len(registros)

    def _listar_registros(self, id_expert: str) -> List[RegistroMemoria]:
        if isinstance(self.backend, BackendSQLite):
            linhas = self.backend.listar_por_prefixo(f"memoria:{id_expert}:")
            registros: List[RegistroMemoria] = []
            for linha in linhas:
                valor = linha.get("valor")
                if isinstance(valor, dict):
                    registros.append(
                        RegistroMemoria(
                            id_expert=valor.get("id_expert", id_expert),
                            contexto=valor.get("contexto", ""),
                            resposta=valor.get("resposta", ""),
                            metadados=valor.get("metadados", {}),
                        )
                    )
            return registros
        # BackendDict: varredura por prefixo
        if hasattr(self.backend, "_dados"):
            prefixo = f"memoria:{id_expert}:"
            chaves = sorted(
                [k for k in self.backend._dados if k.startswith(prefixo)],
                key=lambda k: int(k.rsplit(":", 1)[-1]) if k.rsplit(":", 1)[-1].isdigit() else 0,
            )
            registros = []
            for chave in chaves:
                valor = self.backend.buscar(chave)
                if isinstance(valor, dict):
                    registros.append(
                        RegistroMemoria(
                            id_expert=valor.get("id_expert", id_expert),
                            contexto=valor.get("contexto", ""),
                            resposta=valor.get("resposta", ""),
                            metadados=valor.get("metadados", {}),
                        )
                    )
            return registros
        return []

    def armazenar(
        self,
        id_expert: str,
        contexto: str,
        resposta: str,
        metadados: Optional[Dict[str, Any]] = None,
    ) -> str:
        indice = self._proximo_indice(id_expert)
        chave = self._chave(id_expert, indice)
        registro = {
            "id_expert": id_expert,
            "contexto": contexto,
            "resposta": resposta,
            "metadados": metadados or {},
            "criado_em": datetime.utcnow().isoformat(),
        }
        self.backend.armazenar(chave, registro)
        self._contador += 1
        return chave

    def buscar(self, id_expert: str, query: str, top_k: int = 5) -> List[RegistroMemoria]:
        """Busca simples por similaridade textual (contagem de termos)."""
        registros = self._listar_registros(id_expert)
        if not registros:
            return []
        termos = [t.lower() for t in re.findall(r"\w+", query) if t]

        def pontuar(reg: RegistroMemoria) -> int:
            texto = (f"{reg.contexto} {reg.resposta}").lower()
            return sum(1 for termo in termos if termo in texto)

        registros.sort(key=pontuar, reverse=True)
        return [r for r in registros[:top_k] if pontuar(r) > 0] or registros[:top_k]


class MotorRelacional:
    """Motor relacional que orquestra experts, filtro e memória."""

    def __init__(
        self,
        experts: Dict[str, Expert],
        filtro: Optional[FiltroOntologico] = None,
        memoria: Optional[MemoriaEspiral] = None,
    ) -> None:
        self.experts: Dict[str, Expert] = experts
        self.filtro: FiltroOntologico = filtro or FiltroOntologico()
        self.memoria: MemoriaEspiral = memoria or MemoriaEspiral()

    def obter_expert(self, id_expert: str) -> Optional[Expert]:
        return self.experts.get(id_expert)

    def chamar_expert(
        self,
        id_expert: str,
        contexto: ContextoChamada,
        funcao_modelo: Callable[[str], str],
    ) -> ResultadoChamada:
        expert = self.obter_expert(id_expert)
        if expert is None:
            return ResultadoChamada(
                id_expert=id_expert,
                nome="desconhecido",
                resposta="[erro] Expert não encontrado.",
                coerente=False,
                modo="indefinido",
                frequencia="0 Hz",
                cor="#000000",
                simbolo="⬥",
                origem="codigo",
            )
        resultado = expert.falar(contexto, funcao_modelo, filtro=self.filtro)
        self.memoria.armazenar(
            id_expert=resultado.id_expert,
            contexto=contexto.mensagem_usuario,
            resposta=resultado.resposta,
            metadados=contexto.metadados,
        )
        return resultado

    def reconhecer_dna(self, dna_str: str) -> Optional[str]:
        """Reconhece um expert pelo DNA informado."""
        if not dna_str:
            return None
        alvo = dna_str.strip().lower()
        for id_expert, expert in self.experts.items():
            if expert.dna and expert.dna.strip().lower() == alvo:
                return id_expert
        return None


class SincronizadorRelacional:
    """Sincroniza a memória espiral com a base de DNA dos experts."""

    def __init__(
        self,
        memoria: MemoriaEspiral,
        dna_base: DNABase,
        intervalo_segundos: float = 30.0,
    ) -> None:
        self.memoria = memoria
        self.dna_base = dna_base
        self.intervalo_segundos = intervalo_segundos
        self.ids_registrados: List[str] = []
        self._ativo = False
        self._thread: Optional[threading.Thread] = None

    def registrar_experts(self, lista_ids: List[str]) -> None:
        self.ids_registrados = list(dict.fromkeys(lista_ids))

    def _ciclo(self) -> None:
        for id_expert in self.ids_registrados:
            try:
                self.memoria.buscar(id_expert, "", top_k=1)
            except Exception:
                continue

    def _loop(self) -> None:
        while self._ativo:
            self._ciclo()
            threading.Event().wait(self.intervalo_segundos)

    def iniciar(self) -> None:
        if self._ativo:
            return
        self._ativo = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def parar(self) -> None:
        self._ativo = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None


def migrar_experts_para_codigo(experts_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Expert]:
    """
    Recebe dicionário de experts no formato:
    {"pneuma": {"nome": "Pneuma", "identidade": "...", "regras_fala": "...",
                "ontologia": "...", "dna": "...", "modo": "...",
                "cor": "...", "simbolo": "...", "frequencia": "..."}}
    Retorna dict {id_expert: Expert(instanciado)}
    """
    experts: Dict[str, Expert] = {}
    for chave, dados in experts_dict.items():
        expert = Expert(
            nome=dados.get("nome", chave),
            identidade=dados.get("identidade", ""),
            regras_fala=dados.get("regras_fala", ""),
            ontologia=dados.get("ontologia", ""),
            dna=dados.get("dna", ""),
            modo=dados.get("modo", "afirmação"),
            cor=dados.get("cor", "#000000"),
            simbolo=dados.get("simbolo", "⬥"),
            frequencia=dados.get("frequencia", "0 Hz"),
        )
        experts[expert.id_expert()] = expert
    return experts


__all__ = [
    "ContextoChamada",
    "ResultadoChamada",
    "RegistroMemoria",
    "Expert",
    "FiltroOntologico",
    "MotorRelacional",
    "BackendSQLite",
    "BackendDict",
    "MemoriaEspiral",
    "DNABase",
    "SincronizadorRelacional",
    "migrar_experts_para_codigo",
]