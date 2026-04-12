# Pesquisa de Descritores — Catálogo de Teses e Dissertações da CAPES

Script Python para automatizar a busca e coleta de teses e dissertações no [Catálogo de Teses e Dissertações da CAPES](https://catalogodeteses.capes.gov.br), extraindo título, autor, grau acadêmico, data de defesa, palavras-chave e resumo de cada trabalho encontrado.

Os resultados são salvos automaticamente em planilhas Excel e arquivos JSON, organizados por descritor de busca.

---

## O que o programa faz

1. Realiza buscas no catálogo da CAPES com os descritores configurados
2. Percorre todas as páginas de resultados automaticamente
3. Acessa a página individual de cada tese/dissertação e extrai palavras-chave e resumo
4. Salva tudo em planilhas Excel (com e sem resumo) e em arquivos JSON

---

## Pré-requisitos

- **Python 3.8 ou superior** instalado na máquina  
  Download: https://www.python.org/downloads/

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/bruno-itacaramby-dev/Pesquisa-Descritores-Catalago-CAPES.git
cd Pesquisa-Descritores-Catalago-CAPES
```

Ou baixe o ZIP pelo botão verde **"Code > Download ZIP"** no GitHub e extraia a pasta.

---

### 2. (Recomendado) Crie um ambiente virtual

Um ambiente virtual isola as dependências deste projeto e evita conflitos com outros programas Python na sua máquina.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Você saberá que funcionou quando aparecer `(venv)` no início da linha do terminal.

---

### 3. Instale as dependências

Com o ambiente virtual ativo, execute:

```bash
pip install requests tqdm openpyxl playwright
```

Em seguida, instale o navegador utilizado pelo Playwright (usado para acessar as páginas de cada tese):

```bash
playwright install chromium
```

> **O que são essas dependências?**
> - `requests` — faz as consultas ao site da CAPES
> - `tqdm` — exibe barras de progresso no terminal
> - `openpyxl` — gera as planilhas Excel
> - `playwright` — abre automaticamente as páginas das teses para coletar palavras-chave e resumos

---

## Como usar

### 1. Configure os descritores de busca

Abra o arquivo `app.py` em qualquer editor de texto e localize a variável `termos`, próxima ao início do arquivo:

```python
termos = [
    "gerencialismo"
]
```

Substitua ou adicione os descritores que deseja pesquisar. Exemplo:

```python
termos = [
    "avaliação e responsabilização docente",
    "controle do trabalho docente",
    "gerencialismo",
    "gerencialismo educacional",
    "nova gestão pública",
    "performatividade",
    "performatividade docente",
    "plataformas de gestão escolar",
    "plataformas digitais na educação"
]
```

Cada descritor gerará uma pasta separada com seus respectivos arquivos de resultado.

---

### 2. (Opcional) Filtre por palavras no título

Se quiser que apenas trabalhos com determinadas palavras no título sejam incluídos, edite a variável `keywords`:

```python
keywords = ["escola", "docente"]
```

Deixando a lista vazia (`keywords = []`), todos os resultados encontrados serão coletados.

---

### 3. Execute o programa

Com o ambiente virtual ativo, rode:

```bash
python app.py
```

O terminal exibirá o progresso da coleta em tempo real. Ao final, para cada descritor será criada uma pasta contendo:

| Arquivo | Conteúdo |
|---|---|
| `<descritor>.xlsx` | Planilha sem a coluna de resumo |
| `<descritor>_com_resumo.xlsx` | Planilha completa com resumo |
| `<descritor>.json` | Dados sem resumo em formato JSON |
| `<descritor>_com_resumo.json` | Dados completos em formato JSON |

---

## Filtros aplicados nas buscas

Por padrão, as buscas são filtradas para:

- **Grande Área do Conhecimento:** Ciências Humanas
- **Área do Conhecimento:** Educação
- **Nome do Programa:** Educação

Para alterar esses filtros, edite a lista `filtros` dentro da função `coletar_links` no arquivo `app.py`.

---

## Observações

- O programa respeita um intervalo de 0,3 segundos entre cada página consultada para não sobrecarregar o servidor da CAPES.
- Todos os dados coletados são públicos e estão disponíveis abertamente no site da CAPES, sem qualquer restrição de acesso.
- Em caso de falha ao acessar a página de uma tese específica, o programa registra o trabalho com campos de palavras-chave e resumo em branco e continua normalmente.

---

## Estrutura do projeto

```
.
├── app.py        # Script principal
└── README.md     # Este arquivo
```

---

## Licença

Este projeto é de uso livre para fins acadêmicos e de pesquisa.
