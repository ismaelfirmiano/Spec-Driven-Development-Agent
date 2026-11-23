# Especificação: Conduit — Plataforma de Artigos (RealWorld)

**Versão:** 1.0.0
**Tipo:** Aplicação web de página única (SPA)
**Idioma da interface:** Inglês (textos padrão do Conduit)
**Tecnologias:** HTML5, CSS3 e JavaScript puro, sem frameworks e sem bibliotecas externas
**Persistência:** `localStorage` (simula o servidor)
**Execução:** abrir `index.html` direto no navegador (`file://`), sem servidor e sem build

> **Origem e licença.** Adaptada da especificação do projeto RealWorld
> (repositório `realworld-apps/realworld`, licença MIT,
> https://github.com/realworld-apps/realworld), que define o "Conduit", um clone
> do Medium usado para comparar implementações de front-end. Foram usados os
> documentos de funcionalidades, rotas, modelos de página e endpoints. Como esta
> versão não tem servidor, a API foi substituída por uma camada de dados local
> que segue as mesmas regras dos endpoints oficiais, e as rotas usam `#/` no
> lugar de caminhos, para funcionar via `file://`.

---

## 1. Visão geral

O Conduit é uma plataforma de publicação de artigos. Usuários se cadastram,
publicam artigos escritos em Markdown, marcam artigos como favoritos, seguem
outros autores, comentam e navegam por listas de artigos filtradas por feed,
tag, autor ou favoritos.

### 1.1 Objetivos

- **OBJ-01** Permitir cadastro, login, logout e edição do perfil.
- **OBJ-02** Permitir criar, ler, editar e excluir artigos.
- **OBJ-03** Permitir comentar artigos e excluir os próprios comentários.
- **OBJ-04** Permitir favoritar artigos e seguir autores.
- **OBJ-05** Exibir listas paginadas de artigos: feed global, feed pessoal, por
  tag, por autor e favoritos de um usuário.

### 1.2 Fora do escopo

- Servidor, banco de dados remoto, envio de e-mail, recuperação de senha.
- Edição de comentários (só criar, listar e excluir).
- Exclusão de conta de usuário.
- Upload de imagens (a imagem de perfil é uma URL).
- Notificações, mensagens privadas, busca textual.

### 1.3 Aviso sobre segurança

A autenticação é apenas demonstrativa: senhas e sessão ficam no navegador e
**não** oferecem segurança real. A interface não deve sugerir o contrário.

---

## 2. Modelo de dados

Todos os dados ficam em `localStorage`, sob chaves com o prefixo `conduit.`.

### 2.1 User

| Campo | Tipo | Regras |
|---|---|---|
| `id` | string | único, gerado na criação |
| `username` | string | obrigatório, único (sem diferenciar maiúsculas), 1 a 30 caracteres, sem espaços |
| `email` | string | obrigatório, único (sem diferenciar maiúsculas), formato de e-mail válido |
| `password` | string | obrigatório, mínimo 8 caracteres |
| `bio` | string | opcional, pode ser vazio |
| `image` | string | opcional; URL de imagem; se vazio, usar imagem padrão |

### 2.2 Article

| Campo | Tipo | Regras |
|---|---|---|
| `slug` | string | único, derivado do título em kebab-case; títulos iguais geram slugs diferentes (ex.: sufixo `-2`) |
| `title` | string | obrigatório |
| `description` | string | obrigatório (resumo do artigo) |
| `body` | string | obrigatório, texto em Markdown |
| `tagList` | string[] | opcional; sem tags repetidas; sem espaços nas pontas; tags vazias descartadas |
| `createdAt` | data ISO 8601 | definido na criação |
| `updatedAt` | data ISO 8601 | atualizado a cada edição |
| `authorId` | string | usuário que criou |
| `favoritedBy` | string[] | ids dos usuários que favoritaram |

Campos derivados para exibição: `favorited` (o usuário atual favoritou?),
`favoritesCount` (tamanho de `favoritedBy`), `author` (perfil do autor).

### 2.3 Comment

| Campo | Tipo | Regras |
|---|---|---|
| `id` | string | único |
| `body` | string | obrigatório, não vazio após `trim()` |
| `createdAt` | data ISO 8601 | definido na criação |
| `articleSlug` | string | artigo comentado |
| `authorId` | string | usuário que comentou |

### 2.4 Follow

Relação "usuário A segue usuário B". Um usuário não pode seguir a si mesmo.

### 2.5 Sessão

O id do usuário logado fica em `localStorage` (equivalente ao token JWT do
original). Ao recarregar a página, a sessão continua ativa até o logout.

---

## 3. Rotas

| Rota | Página | Acesso |
|---|---|---|
| `#/` | Home | todos |
| `#/login` | Sign in | apenas deslogados |
| `#/register` | Sign up | apenas deslogados |
| `#/settings` | Settings | apenas logados |
| `#/editor` | Novo artigo | apenas logados |
| `#/editor/:slug` | Editar artigo | apenas o autor |
| `#/article/:slug` | Artigo | todos |
| `#/profile/:username` | Perfil (artigos do usuário) | todos |
| `#/profile/:username/favorites` | Perfil (favoritos do usuário) | todos |

- **ROT-01** A navegação entre rotas não recarrega a página (evento `hashchange`).
- **ROT-02** Acessar uma rota "apenas logados" sem sessão redireciona para `#/login`.
- **ROT-03** Acessar `#/login` ou `#/register` com sessão ativa redireciona para `#/`.
- **ROT-04** Acessar `#/editor/:slug` de um artigo de outro autor redireciona para
  a página do artigo.
- **ROT-05** Slug ou usuário inexistente mostra uma mensagem de "não encontrado",
  sem erro no console.
- **ROT-06** Recarregar a página mantém a rota atual.

---

## 4. Requisitos funcionais

### 4.1 Cabeçalho e rodapé

- **RF-01** O cabeçalho mostra a marca "conduit" (link para `#/`).
- **RF-02** Deslogado, o cabeçalho mostra os links "Home", "Sign in" e "Sign up".
- **RF-03** Logado, o cabeçalho mostra "Home", "New Article", "Settings" e o nome
  do usuário com sua imagem (link para o próprio perfil).
- **RF-04** O link da página atual fica destacado (classe `active`).
- **RF-05** O rodapé mostra a marca "conduit" e um texto curto de créditos.

### 4.2 Cadastro e login

- **RF-06** A página Sign up tem os campos Username, Email e Password e o botão
  "Sign up", além de um link "Have an account?" para `#/login`.
- **RF-07** O cadastro valida as regras do modelo `User`. Se houver erros, eles
  aparecem em uma lista acima do formulário (ex.: "email has already been taken",
  "username can't be blank") e nada é salvo.
- **RF-08** Cadastro válido cria o usuário, inicia a sessão e leva para `#/`.
- **RF-09** A página Sign in tem os campos Email e Password e o botão "Sign in",
  além de um link "Need an account?" para `#/register`.
- **RF-10** E-mail ou senha incorretos mostram a mensagem "email or password is
  invalid", sem indicar qual dos dois está errado.
- **RF-11** Login válido inicia a sessão e leva para `#/`.
- **RF-12** O botão de envio fica desabilitado enquanto a operação está em
  andamento, para evitar envio duplicado.

### 4.3 Settings

- **RF-13** A página Settings tem os campos: URL da imagem de perfil, Username,
  Bio (área de texto), Email e New Password, com os valores atuais preenchidos
  (exceto a senha), e o botão "Update Settings".
- **RF-14** Campos válidos atualizam o usuário; a nova senha só muda se o campo
  for preenchido. Username e e-mail continuam únicos.
- **RF-15** Após salvar, o usuário é levado ao próprio perfil e o cabeçalho
  mostra os dados novos.
- **RF-16** Erros de validação aparecem em lista, como no cadastro.
- **RF-17** O botão "Or click here to logout." encerra a sessão e leva para `#/`.

### 4.4 Home

- **RF-18** Deslogado, a Home mostra um banner com "conduit" e o texto "A place
  to share your knowledge."; logado, o banner não aparece.
- **RF-19** A Home tem abas: "Your Feed" (só para logados), "Global Feed" e, quando
  uma tag está selecionada, uma aba "# nome-da-tag".
- **RF-20** Logado, a aba inicial é "Your Feed"; deslogado, é "Global Feed".
- **RF-21** "Global Feed" lista todos os artigos, do mais recente para o mais antigo.
- **RF-22** "Your Feed" lista apenas artigos de autores que o usuário segue, do
  mais recente para o mais antigo.
- **RF-23** A barra lateral "Popular Tags" mostra as tags existentes, ordenadas
  pela quantidade de artigos que as usam (empate em ordem alfabética).
- **RF-24** Clicar em uma tag abre a aba "# tag" com os artigos que têm essa tag.
- **RF-25** Lista vazia mostra "No articles are here... yet.".

### 4.5 Lista de artigos (componente usado na Home e no Perfil)

- **RF-26** Cada item mostra: imagem e nome do autor (link para o perfil), data de
  criação (formato "January 20, 2026"), botão de favorito com a contagem,
  título, descrição, "Read more..." e as tags do artigo.
- **RF-27** Clicar no título, na descrição ou em "Read more..." abre o artigo.
- **RF-28** A lista é paginada com **10 artigos por página**. Os links de página
  aparecem abaixo da lista quando houver mais de uma página; a página atual fica
  destacada.
- **RF-29** Trocar de aba ou de tag volta para a página 1.

### 4.6 Favoritos

- **RF-30** Clicar no botão de favorito alterna o estado: favorita (contagem +1,
  botão preenchido) ou desfavorita (contagem −1, botão vazado).
- **RF-31** Deslogado, clicar em favorito leva para `#/login` e nada muda.
- **RF-32** Um usuário favorita um artigo no máximo uma vez.
- **RF-33** A contagem e o estado aparecem iguais em todas as telas que mostram o
  artigo.

### 4.7 Página do artigo

- **RF-34** Mostra o título em destaque, os dados do autor e a data.
- **RF-35** O corpo é exibido convertendo Markdown em HTML (ver seção 5).
- **RF-36** As tags aparecem abaixo do corpo.
- **RF-37** Para quem não é o autor, aparecem os botões "Follow <username>" (ou
  "Unfollow <username>") e "Favorite Article (N)" (ou "Unfavorite Article (N)").
- **RF-38** Para o autor, aparecem "Edit Article" (leva a `#/editor/:slug`) e
  "Delete Article".
- **RF-39** "Delete Article" pede confirmação; confirmado, exclui o artigo, seus
  comentários e favoritos, e leva para `#/`.

### 4.8 Comentários

- **RF-40** Abaixo do artigo fica a seção de comentários, do mais recente para o
  mais antigo. Cada comentário mostra texto, imagem e nome do autor e data.
- **RF-41** Logado, aparece um formulário com área de texto "Write a comment..." e
  o botão "Post Comment"; o comentário novo aparece na lista sem recarregar a
  página e o campo é limpo.
- **RF-42** Comentário vazio (ou só com espaços) não é publicado.
- **RF-43** Deslogado, aparece o texto "Sign in or sign up to add comments on this
  article." com links para `#/login` e `#/register`.
- **RF-44** O autor do comentário vê um ícone de lixeira que exclui o comentário;
  outros usuários não veem esse ícone.

### 4.9 Editor

- **RF-45** O editor tem os campos: Article Title, "What's this article about?"
  (descrição), "Write your article (in markdown)" (corpo) e "Enter tags", e o botão
  "Publish Article".
- **RF-46** No campo de tags, pressionar Enter adiciona a tag digitada à lista
  exibida abaixo do campo; cada tag tem um "×" para removê-la. Enter nesse campo
  não envia o formulário.
- **RF-47** Título, descrição e corpo são obrigatórios; erros aparecem em lista.
- **RF-48** Publicar um artigo novo gera o slug, salva e leva para a página do artigo.
- **RF-49** Em `#/editor/:slug`, os campos vêm preenchidos; salvar atualiza o
  artigo (e o slug, se o título mudar) e leva para a página do artigo.
- **RF-50** Ao mudar o slug, comentários e favoritos continuam ligados ao artigo.

### 4.10 Perfil

- **RF-51** Mostra imagem, username e bio do usuário.
- **RF-52** Para outros usuários (logado), aparece "Follow <username>" ou
  "Unfollow <username>"; para o próprio usuário, aparece "Edit Profile Settings"
  (leva a `#/settings`).
- **RF-53** Deslogado, clicar em Follow leva para `#/login`.
- **RF-54** Abas "My Articles" (artigos escritos pelo usuário) e "Favorited
  Articles" (artigos que ele favoritou), cada uma com a lista paginada da seção 4.5.
- **RF-55** Seguir ou deixar de seguir atualiza o botão na hora e passa a afetar o
  "Your Feed".

---

## 5. Renderização de Markdown

Sem bibliotecas externas, o corpo do artigo deve suportar este subconjunto:

- **MD-01** Parágrafos separados por linha em branco.
- **MD-02** Títulos `#`, `##` e `###`.
- **MD-03** **Negrito** (`**texto**`) e *itálico* (`*texto*`).
- **MD-04** Código em linha (`` `código` ``) e bloco de código (três crases).
- **MD-05** Listas com `-` ou `*` e listas numeradas `1.`.
- **MD-06** Links `[texto](url)`, aceitando apenas `http:`, `https:` e `mailto:`.
- **MD-07** Citações com `>`.
- **MD-08** Qualquer HTML escrito pelo usuário aparece como texto literal, nunca é
  interpretado (ex.: `<script>` ou `<img onerror=...>` não executam).

---

## 6. Regras de negócio

- **RN-01** Só o autor pode editar ou excluir um artigo.
- **RN-02** Só o autor pode excluir um comentário.
- **RN-03** Username e e-mail são únicos, sem diferenciar maiúsculas de minúsculas.
- **RN-04** Ninguém pode seguir a si mesmo; o botão Follow não aparece no próprio perfil.
- **RN-05** Um usuário favorita cada artigo no máximo uma vez.
- **RN-06** Slugs são únicos; dois artigos com o mesmo título têm slugs diferentes.
- **RN-07** Excluir um artigo exclui seus comentários e remove seus favoritos.
- **RN-08** Todas as listas de artigos e comentários são ordenadas do mais recente
  para o mais antigo.
- **RN-09** As regras de permissão valem na camada de dados, não só na interface
  (ex.: chamar a função de exclusão com outro usuário logado é recusado).

---

## 7. Dados iniciais

- **DI-01** Na primeira execução (sem dados salvos), a aplicação cria 2 usuários
  de demonstração e 3 artigos com tags e comentários, para a Home não começar
  vazia. Os dados de demonstração não são recriados depois que o usuário os
  apagar.
- **DI-02** O README ou a tela de login informa o e-mail e a senha dos usuários
  de demonstração.

---

## 8. Requisitos não funcionais

- **RNF-01** Abre com duplo clique em `index.html`, sem servidor, módulos ES ou build.
- **RNF-02** Separação entre camada de dados (regras e `localStorage`), roteamento
  e interface, em arquivos ou módulos distintos.
- **RNF-03** Conteúdo do usuário é inserido no DOM como texto (`textContent`); o
  único HTML gerado a partir de dados é o do Markdown, já escapado.
- **RNF-04** Dados corrompidos em `localStorage` não impedem a aplicação de abrir.
- **RNF-05** Layout responsivo: em telas estreitas, a barra de tags vai para baixo
  da lista e o menu do cabeçalho continua utilizável.
- **RNF-06** Formulários com rótulos acessíveis e operação completa por teclado.
- **RNF-07** Nenhum erro de JavaScript no console durante o uso normal.

---

## 9. Critérios de aceitação

1. **Dado** um visitante, **quando** ele se cadastra com dados válidos, **então**
   fica logado e vê "Your Feed" vazio e "Global Feed" com os artigos existentes.
2. **Dado** um cadastro com e-mail já usado, **então** aparece "email has already
   been taken" e nenhum usuário novo é criado.
3. **Dado** um usuário logado, **quando** publica um artigo com as tags "js" e
   "web", **então** é levado à página do artigo, e as tags aparecem em "Popular Tags".
4. **Dado** dois artigos com o título "Hello", **então** eles têm slugs diferentes
   e cada um abre a sua página.
5. **Dado** 25 artigos, **então** o Global Feed tem 3 páginas (10, 10 e 5 artigos).
6. **Dado** que A segue B, **quando** B publica um artigo, **então** ele aparece no
   "Your Feed" de A; **quando** A deixa de seguir B, o artigo sai do feed.
7. **Dado** um artigo com 0 favoritos, **quando** um usuário favorita, **então** a
   contagem vai a 1 na lista e na página do artigo; clicar de novo volta a 0.
8. **Dado** um visitante, **quando** clica em favoritar, **então** vai para
   `#/login` e a contagem não muda.
9. **Dado** um artigo cujo corpo contém `<img src=x onerror=alert(1)>`, **então** o
   texto aparece literalmente e nenhum script é executado.
10. **Dado** um comentário de outro usuário, **então** o ícone de lixeira não aparece.
11. **Dado** o autor editando o título de um artigo comentado, **então** o slug muda
    e os comentários continuam aparecendo.
12. **Dado** um usuário logado, **quando** recarrega a página, **então** continua
    logado e na mesma rota.
13. **Dado** um visitante acessando `#/settings`, **então** é redirecionado para `#/login`.
14. **Dado** que o autor exclui um artigo, **então** ele some de todas as listas, das
    tags populares (se a tag não for usada por outro artigo) e dos favoritos.
