# FASE 7 — Sistema Integrado FarmTech Solutions

**Equipe:** IA_Underground | **FIAP ON** | 2025

---

## O que é essa fase?

A Fase 7 é o "painel de controle" de todo o projeto FarmTech. Em vez de ter que navegar em cada pasta e rodar cada script separadamente, a gente criou um sistema centralizado que permite iniciar qualquer fase com um único comando.

Resumindo: ela integra tudo que foi feito nas Fases 1 a 6 num único lugar.

---

## Estrutura dos arquivos

```
FASE7/
├── run.py            # Menu interativo no terminal (CLI)
├── launcher.py       # Dashboard visual no navegador (Streamlit)
├── config.json       # Configurações centralizadas de todas as fases
└── requirements.txt  # Dependências necessárias para rodar
```

---

## Guia de Instalação Completo

> Siga os passos na ordem. Não pule etapas. Uma máquina sem nada instalado deve seguir do passo 1 ao 6 antes de rodar qualquer fase.

---

### 1. Python 3.11

**Download:** https://www.python.org/downloads/

- Clique em **"Download Python 3.11.x"**
- Na tela de instalação, marque obrigatoriamente **"Add Python to PATH"**
- Clique em **"Install Now"** e aguarde

Verificar instalação — abra o terminal e execute:

```bash
python --version
pip --version
```

Ambos devem retornar versões sem erro.

---

### 2. Git

**Download:** https://git-scm.com/download/win

- Execute o instalador e deixe todas as opções no padrão
- Clique "Next" até finalizar

```bash
git --version
```

---

### 3. Visual Studio Code (recomendado)

**Download:** https://code.visualstudio.com/

- Execute o instalador
- Marque **"Add to PATH"** durante a instalação

**Extensões obrigatórias** — pressione `Ctrl+Shift+X` dentro do VSCode, pesquise e instale:

| Extensão | ID | Para quê |
|---|---|---|
| Python | `ms-python.python` | Rodar arquivos .py |
| Jupyter | `ms-toolsai.jupyter` | Abrir notebooks .ipynb |
| R | `REditorSupport.r` | Rodar scripts .R |

---

### 4. R 4.x

Necessário para **FASE 1** (weather_api.R, analysis.r) e **FASE 2** (codigodeanalise.r).

**Download:** https://cran.r-project.org/bin/windows/base/

- Baixe o instalador R 4.x para Windows e execute com as opções padrão

```bash
Rscript --version
```

Abra o R e instale os pacotes necessários:

```r
install.packages(c("httr", "jsonlite", "ggplot2", "dplyr", "readr"), repos="https://cran.r-project.org")
```

---

### 5. Oracle Instant Client

Necessário **apenas para FASE 2** — módulo de Gestão de Sementes com banco Oracle.

**Download:** https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html

- Baixe o pacote **"Basic Package"** (.zip)
- Extraia para `C:\oracle\instantclient`
- Adicione o caminho à variável de ambiente PATH:
  1. Pesquise "variáveis de ambiente" no menu Iniciar
  2. Em "Variáveis do Sistema" → `Path` → "Editar" → "Novo"
  3. Cole `C:\oracle\instantclient` e clique OK em tudo
  4. Feche e reabra o terminal

```bash
python -c "import oracledb; print('Oracle OK')"
```

> Você também precisará de acesso a um servidor Oracle (local ou Oracle Cloud Free Tier). Configure as credenciais no arquivo `FASE2/PythonAlem/database.py`.

---

### 6. Ambiente virtual e pacotes Python

Abra o terminal na **pasta raiz do projeto** e execute os comandos abaixo em sequência:

**Criar o ambiente virtual:**

```bash
python -m venv .venv
```

**Ativar — PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Ativar — CMD:**

```cmd
.venv\Scripts\activate.bat
```

> Se o PowerShell bloquear a ativação, execute antes:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

Após ativar, o terminal exibirá `(.venv)` no início da linha.

**Instalar todas as dependências:**

```bash
pip install -r requirements.txt
```

Esse comando instala automaticamente:

| Pacote | Versão mínima | Para quê |
|---|---|---|
| `pandas` | 2.0.0 | Manipulação de dados — todas as fases |
| `numpy` | 1.24.0 | Cálculos numéricos |
| `matplotlib` | 3.7.0 | Geração de gráficos |
| `seaborn` | 0.12.0 | Gráficos estatísticos |
| `scikit-learn` | 1.3.0 | Machine Learning — FASE 3 e 4 |
| `scipy` | 1.10.0 | Ciência de dados |
| `oracledb` | 1.3.0 | Banco de dados Oracle — FASE 2 |
| `streamlit` | 1.28.0 | Dashboard web — FASE 4 e 7 |
| `jupyter` | 1.0.0 | Notebooks interativos — FASE 5 e 6 |
| `notebook` | 7.0.0 | Interface Jupyter no navegador |
| `ipykernel` | 6.25.0 | Kernel Python para Jupyter |
| `ipython` | 8.14.0 | Terminal Python avançado |
| `openpyxl` | 3.1.0 | Leitura de arquivos .xlsx |
| `Pillow` | 10.0.0 | Processamento de imagens |
| `tqdm` | 4.65.0 | Barra de progresso |
| `PyYAML` | 6.0.0 | Arquivos de configuração |
| `requests` | 2.28.0 | Chamadas HTTP e APIs externas |

---

## Como usar

Com o ambiente virtual ativado, entre na pasta `FASE7/`:

```bash
cd FASE7
```

### Opção 1 — Terminal (mais simples)

```bash
# Abre o menu interativo com todas as fases
python run.py

# Lança uma fase específica direto (sem passar pelo menu)
python run.py 4d

# Abre o dashboard visual no navegador
python run.py dashboard

# Mostra todas as fases cadastradas (inclusive as desativadas)
python run.py --list
```

**Exemplo de menu interativo:**

```
  ══════════════════════════════════════════════════════════
  FarmTech Solutions
  Setor: Agronegócio  |  Equipe: IA_Underground
  ──────────────────────────────────────────────────────────
  [ 1]  [CLI]  Gestão de Áreas e Insumos
  [2a]  [CLI]  Gestão de Sementes (Oracle DB)
  [2b]  [ R ]  Consulta Meteorológica
  [2c]  [ R ]  Análise R — Áreas por Cultura
  [4t]  [CLI]  Treinar Modelos IoT
  [4d]  [WEB]  Dashboard ML — Irrigação  (:8502)
  [ 5]  [ NB]  Previsão de Rendimento (Cloud)
  [ 6]  [ NB]  Visão Computacional (YOLO)
  ──────────────────────────────────────────────────────────
  [ 0]  [WEB]  Dashboard Completo (Fase 7)
  [ q]         Sair
  ══════════════════════════════════════════════════════════

  Opção: _
```

### Opção 2 — Dashboard no navegador (mais visual)

```bash
streamlit run launcher.py
```

Depois acesse **http://localhost:8501** no navegador. O dashboard mostra todas as fases em cards e permite iniciar e parar cada uma com um botão.

> Se der conflito de porta com a Fase 4, use:
> `streamlit run launcher.py --server.port 8500`

---

## Fases disponíveis

| ID  | Nome                              | Tipo       | Porta |
|-----|-----------------------------------|------------|-------|
| 1   | Gestão de Áreas e Insumos         | CLI Python | —     |
| 2a  | Gestão de Sementes (Oracle DB)    | CLI Python | —     |
| 2b  | Consulta Meteorológica            | R Script   | —     |
| 2c  | Análise R — Áreas por Cultura     | R Script   | —     |
| 3   | Classificação de Culturas (ML)    | CLI Python | —     |
| 4t  | Treinar Modelos IoT               | CLI Python | —     |
| 4d  | Dashboard ML — Irrigação          | Streamlit  | 8502  |
| 5   | Previsão de Rendimento (Cloud)    | Jupyter    | —     |
| 6   | Visão Computacional (YOLO)        | Jupyter    | —     |

> **FASE 5 e FASE 6 — Alternativa via Google Colab:** acesse https://colab.research.google.com, clique em "Fazer upload de notebook" e selecione o arquivo `.ipynb` da fase correspondente. Nesse caso, não é necessária nenhuma instalação local para essas fases.

---

## Tipos de execução

O sistema suporta 4 tipos de execução diferentes:

| Tipo | Como roda | Exemplo de uso |
|---|---|---|
| `cli_python` | Abre no próprio terminal | Fases 1, 2a, 4t |
| `streamlit` | Abre no navegador (nova aba) | Fases 4d, 7 (dashboard) |
| `r_script` | Roda via Rscript (requer R instalado) | Fases 2b, 2c |
| `jupyter` | Abre o Jupyter Notebook no navegador | Fases 3, 5, 6 |

---

## Configurando o sistema — editando o config.json

O `config.json` é o coração do sistema. Qualquer mudança no projeto (nome, equipe, caminhos dos scripts) deve ser feita aqui.

### Estrutura geral

```json
{
  "sector": "Agronegócio",
  "project_name": "FarmTech Solutions",
  "team": "IA_Underground",
  "description": "Descrição do projeto",
  "phases": [ ... ]
}
```

### Estrutura de cada fase

```json
{
  "id": "4d",
  "name": "Dashboard ML — Irrigação",
  "description": "Descrição curta que aparece no dashboard.",
  "type": "streamlit",
  "path": "FASE4/CAP1/dashboard.py",
  "port": 8502,
  "enabled": true
}
```

**Campos explicados:**
- `id` — identificador único, é o que você digita no menu (ex: `4d`)
- `name` — nome que aparece no menu e no dashboard
- `description` — texto de ajuda que explica o que aquela fase faz
- `type` — tipo de execução: `cli_python`, `streamlit`, `r_script` ou `jupyter`
- `path` — caminho do script **a partir da pasta raiz do projeto** (não da FASE7)
- `port` — número da porta (só obrigatório para fases do tipo `streamlit`)
- `enabled` — `true` para aparecer no menu, `false` para esconder

---

## Fluxo de uso recomendado

Para quem está abrindo o projeto pela primeira vez:

1. Siga o **Guia de Instalação Completo** acima (passos 1 a 6)
2. Rode `python run.py` para ver o menu
3. Comece pela Fase 1 para entender o fluxo básico
4. Para as análises de ML, rode a Fase 4t primeiro (treina os modelos) e depois a 4d (dashboard)
5. Para o dashboard visual completo, escolha a opção `0` no menu ou `python run.py dashboard`

---

## Observações importantes

- **Ctrl+C** encerra qualquer processo que esteja rodando (Streamlit, scripts, etc.)
- Se um script R não abrir, verifique se o R está instalado e o `Rscript` está no PATH do sistema
- O dashboard da Fase 7 fica na porta **8501** e o da Fase 4d na **8502** — portas diferentes para não conflitar
- Mudanças no `config.json` pelo dashboard visual são salvas automaticamente no arquivo
- A Fase 3 precisa do arquivo `produtos_agricolas.csv` na pasta `FASE3/` — ele já está incluído no projeto
