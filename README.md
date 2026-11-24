# Fábrica de APK

Site que transforma ZIP, pasta ou HTML em APK Android. O site roda no GitHub Pages e a compilação roda no GitHub Actions, de graça.

## Instalação (uma vez)

1. Crie um repositório **público** no GitHub (Pages grátis exige repositório público).
2. Envie todo o conteúdo desta pasta para a raiz do repositório: `index.html`, `tools/` e `.github/`. No PC, arraste os arquivos e as pastas. No celular, crie cada arquivo em **Add file → Create new file**, digitando o caminho completo (por exemplo `tools/make_project.py`) e colando o conteúdo.
3. Em **Settings → Pages**, escolha **Deploy from a branch**, branch `main`, pasta `/ (root)`. Em alguns minutos o site fica em `https://SEU-USUARIO.github.io/NOME-DO-REPO/`.
4. Crie um token em https://github.com/settings/personal-access-tokens/new, só para este repositório, com **Contents** e **Actions** em Read and write.

## Como usar

1. Abra o site, cole o token (fica só no seu navegador) e confirme o repositório.
2. Escolha o ZIP, a pasta ou os HTMLs do seu app ou jogo, ajuste nome, pacote, orientação e ícone.
3. Toque em **Gerar APK**. Em uns 5 minutos o link de download aparece na página e na aba **Releases** do repositório.

## Observações

- Em repositório público, o código do seu jogo fica visível para todos.
- Se o Actions falhar, abra **Settings → Actions → General → Workflow permissions** e marque **Read and write permissions**.
- O pacote enviado pelo navegador pode ter até 50 MB.
- O app abre os arquivos de dentro do APK. Bibliotecas carregadas de CDN (como o Phaser) precisam de internet; para jogar offline, coloque os arquivos delas dentro do ZIP.
