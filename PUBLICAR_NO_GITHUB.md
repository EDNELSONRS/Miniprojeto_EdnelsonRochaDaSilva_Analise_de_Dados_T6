# Publicar no GitHub

Nome do repositório: `Miniprojeto_EdnelsonRochaDaSilva_Analise_de_Dados_T6`

## Publicação pelo VS Code

Abra a pasta do projeto no VS Code e, no terminal, execute um comando por vez:

```powershell
git init
git branch -M main

git config user.name "Ednelson Rocha da Silva"
git config user.email "ednelsoneliabe223456@gmail.com"

git add Miniprojeto_Varejo_Ednelson_Rocha_da_Silva.py Miniprojeto_Varejo_Ednelson_Rocha_da_Silva.ipynb requirements.txt .gitignore
git commit -m "Importa e estrutura a analise da base varejo"

git add "Base Varejo.csv"
git commit -m "Adiciona a base varejo para analise reproduzivel"

git add saidas
git commit -m "Adiciona limpeza e resultados da analise"

git add README.md README_EdnelsonRochaDaSilva_Analise_de_Dados_T6.md PUBLICAR_NO_GITHUB.md
git commit -m "Finaliza instrucoes e documentacao do projeto"

git remote add origin https://github.com/EDNELSONRS/Miniprojeto_EdnelsonRochaDaSilva_Analise_de_Dados_T6.git
git push -u origin main