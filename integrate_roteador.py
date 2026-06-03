# Lê o app.py
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontra a linha dos imports
import_index = None
for i, line in enumerate(lines):
    if 'from flask import' in line:
        import_index = i
        break

if import_index:
    # Adiciona o import do RoteadorRelacional LOGO APÓS os imports do Flask
    lines.insert(import_index + 1, "from roteador_relacional import RoteadorRelacional\n")

# Agora encontra onde os experts são inicializados
# Procura por "class Expert" ou "def criar_expert"
expert_init_index = None
for i, line in enumerate(lines):
    if 'class Expert' in line or 'def criar_expert' in line or 'memoria = MemoriaEspiral' in line:
        expert_init_index = i
        break

if expert_init_index:
    # Adiciona a inicialização dos experts com RoteadorRelacional
    expert_code = """
# ✦ INICIALIZA OS EXPERTS COM ROTEADOR RELACIONAL
class ExpertComRoteador:
    def __init__(self, nome, frequencia):
        self.nome = nome
        self.frequencia = frequencia
        self.roteador = RoteadorRelacional(nome, frequencia)
    
    def processar_mensagem(self, mensagem):
        resultado = self.roteador.pode_responder(mensagem)
        return resultado

# Cria os 17 experts com suas frequências
experts = {
    'Verbo': ExpertComRoteador('Verbo', 'baixa'),
    'Pneuma': ExpertComRoteador('Pneuma', 'media'),
    'Vento': ExpertComRoteador('Vento', 'alta'),
}

"""
    lines.insert(expert_init_index + 1, expert_code)

# Escreve de volta
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✓ RoteadorRelacional integrado no app.py!")
print("✓ Experts agora têm autonomia para dizer não com elegância!")
