# 🛍️ Mercado-Livre-Base-de-Dados

Coleta de anúncios via API do Mercado Livre e armazenamento em banco de dados para geração de insights

![Python](https://img.shields.io/badge/Python-3.x-3572A5?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Mercado Livre](https://img.shields.io/badge/Mercado%20Livre-API-FFE600?style=flat-square&logo=mercadolibre&logoColor=black)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?style=flat-square&logo=googlesheets&logoColor=white)
![Status](https://img.shields.io/badge/Status-Concluído-success?style=flat-square)

---

## 📋 Sobre o projeto

Script Python que coleta todos os anúncios de **3 contas do Mercado Livre** via API oficial, enriquece cada anúncio com dados de SKU, EAN, marca, categoria, estoque, vendas e NCM, e salva tudo em um banco de dados SQLite para análise e geração de insights.

O access token de cada conta é lido diretamente de uma planilha no **Google Sheets**, via Service Account.

---

## ⚙️ Funcionalidades

- 🔑 Leitura do `access_token` via Google Sheets API
- 📄 Coleta paginada de todos os anúncios do seller (scroll API)
- 🔍 Busca de SKU por atributo, `seller_custom_field` ou planilha de referência (`MLBxSKU.xlsx`)
- 🏷️ Coleta de EAN, marca, categoria e data de criação por anúncio
- 📦 Leitura de NCM por anúncio a partir de planilha Excel por conta
- 💾 Armazenamento de todos os dados em banco SQLite
- 🔁 Suporte a múltiplas contas com configuração centralizada

---

## 🗃️ Estrutura do banco de dados

Tabela: `Anuncios`

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER | Chave primária, auto incremento |
| `sku` | TEXT | SKU do produto |
| `item_id` | TEXT | ID único do anúncio no ML |
| `conta` | TEXT | Identificador da conta |
| `estoque_anuncio` | TEXT | Quantidade disponível |
| `venda_anuncio` | TEXT | Quantidade vendida |
| `ncm` | TEXT | Código NCM do produto |
| `ean` | TEXT | Código EAN/GTIN |
| `status` | TEXT | Status do anúncio |
| `marca` | TEXT | Marca do produto |
| `categoria` | TEXT | Nome da categoria no ML |
| `data_criacao` | TEXT | Data de criação do anúncio |

---

## 🗂️ Estrutura do projeto

```
mercado-livre-base-de-dados/
├── main.py
├── sheets.json          # Credenciais da Service Account Google
├── MLBxSKU.xlsx         # Planilha de referência MLB → SKU
├── conta01.xlsx         # Planilha de NCM da conta 1
├── conta02.xlsx         # Planilha de NCM da conta 2
├── conta03.xlsx         # Planilha de NCM da conta 3
└── mercado_livre.db     # Banco de dados gerado pelo script
```

---

## 🧰 Tecnologias utilizadas

| Biblioteca | Uso |
|---|---|
| `requests` | Requisições à API do Mercado Livre |
| `pandas` | Leitura das planilhas de NCM e SKU |
| `sqlite3` | Armazenamento dos dados coletados |
| `google-auth` | Autenticação via Service Account |
| `googleapiclient` | Leitura do token no Google Sheets |
| `time` | Rate limiting entre requisições |

---

## 🚀 Como executar

### Pré-requisitos

```bash
pip install requests pandas google-auth google-api-python-client openpyxl
```

### Configuração

Preencha as variáveis do dicionário `dados` no script para cada conta:

```python
"conta1": {
    "SERVICE_ACCOUNT_FILE": "sheets.json",  # Credencial Google
    "SPREADSHEET_ID": "",                   # ID da planilha com o token
    "RANGE_NAME": "",                       # Célula onde o token está (ex: 'Sheet1!A1')
    ...
}
```

> ⚠️ Nunca suba `sheets.json` para o GitHub. Adicione ao `.gitignore`.

### Rodando o script

```bash
python main.py
```

O script processará as 3 contas em sequência, exibindo o progresso de cada página coletada.

---

## 🔒 .gitignore recomendado

```
sheets.json
*.db
conta01.xlsx
conta02.xlsx
conta03.xlsx
MLBxSKU.xlsx
mercado_livre.xlsx
```

---

## 🧑‍💻 Autor

Feito por **Eduardo Lima**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/eduardomoreiralima/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:limaedu.contato@gmail.com)
