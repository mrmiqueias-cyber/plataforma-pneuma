// Exemplo: sincronizar
fetch('http://localhost:8000/sincronizar', { method: 'POST' })
  .then(res => res.json())
  .then(data => console.log(data))

// Exemplo: processar mensagem
fetch('http://localhost:8000/processar-mensagem', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ mensagem: "Oi", autor: "Miquéias" })
})
  .then(res => res.json())
  .then(data => console.log(data))