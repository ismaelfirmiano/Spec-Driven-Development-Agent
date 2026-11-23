Regras técnicas (idênticas para todas as versões do experimento):
- Deve abrir com duplo clique em index.html (protocolo file://): nada de
  módulos ES, imports/exports, fetch de arquivos locais, build ou servidor.
  Scripts clássicos devem ser carregados na ordem de dependência.
- Use apenas HTML, CSS e JavaScript puro; bibliotecas externas só se o pedido
  exigir, e então via CDN.
- Confirme que cada caminho usado em `src` e `href` existe na lista de arquivos
  devolvida.
- Não use `innerHTML`, `outerHTML` ou `document.write`. Use `textContent` e
  APIs DOM seguras para qualquer conteúdo.
- Revise cada bloco JavaScript por erros de sintaxe antes de responder.
- Entregue todos os arquivos completos, sem "TODO" nem trechos omitidos.
  Use index.html, style.css e script.js quando o pedido não exigir outra estrutura.
- Não declare que executou ou testou o código.
