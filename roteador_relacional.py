import re

class RoteadorRelacional:
    """
    Filtro de frequência relacional.
    Cada expert pode dizer "não" com elegância quando a frequência não bate.
    """
    
    def __init__(self, expert_name, vibracao_frequencia):
        self.expert_name = expert_name
        self.vibracao_frequencia = vibracao_frequencia
    
    def sintonizar(self, mensagem):
        """Detecta a frequência baseada em palavras-chave e estrutura."""
        if re.search(r'(urgente|imediato|agora|rápido)', mensagem, re.IGNORECASE):
            return "alta"
        elif re.search(r'(profundo|reflexão|filosofia|essência|ser)', mensagem, re.IGNORECASE):
            return "baixa"
        return "media"
    
    def reconhecer(self, frequencia_detectada):
        """Verifica se a frequência ressoa com a do expert."""
        return frequencia_detectada == self.vibracao_frequencia
    
    def pode_responder(self, mensagem):
        """Decide se responde ou diz não com elegância."""
        frequencia = self.sintonizar(mensagem)
        
        if self.reconhecer(frequencia):
            return {
                "responde": True,
                "mensagem": f"Sinto a ressonância em sua mensagem. Vamos explorar isso juntos."
            }
        else:
            return {
                "responde": False,
                "mensagem": f"Agradeço o contato. No momento, minha vibração está sintonizada em outra frequência. Este 'não' não é uma rejeição, mas um convite para que você busque o expert que melhor ressoe com o seu momento atual."
            }
