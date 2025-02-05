# Brasileirão Data Scraper

Sistema para consulta de dados do Campeonato Brasileiro, composto por:
- Web scraper para coletar dados do site ogol.com.br
- API REST para disponibilizar os dados
- CLI para consultas via linha de comando

## Estrutura do Projeto

2. Criando um arquivo test.py:
```python
# test.py
from cbf_scraper import BrasileiraoScraper

def main():
    scraper = BrasileiraoScraper("2024")
    
    # Consultar campeão
    campeao = scraper.get_champion()
    print("\nCampeão:")
    print(campeao)
    
    # Consultar jogos da rodada
    jogos = scraper.get_round_data("38")
    print("\nJogos:")
    print(jogos)

if __name__ == "__main__":
    main()
```

Execute com:
```bash
python test.py
```

## Dependências

### Python
- Flask
- requests
- beautifulsoup4
- dataclasses

### Go
- Biblioteca padrão apenas

## Instalação e Execução

1. Clone o repositório e instale as dependências Python:
```bash
pip install flask requests beautifulsoup4
```

2. Adicione o diretório ao PYTHONPATH e inicie o servidor:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Linux/Mac
# ou
set PYTHONPATH=%PYTHONPATH%;%cd%      # Windows

python server/app.py
```

3. Em outro terminal, execute o cliente Go:
```bash
cd client
go run main.go -ano=2024 -rodada=38
```

## Funcionalidades

### API REST
Endpoints disponíveis:
- `GET /campeao/<ano>`: Retorna o campeão do ano especificado
- `GET /jogos/<ano>/<rodada>`: Retorna os jogos da rodada especificada

### CLI
Exemplos de uso:
```bash
# Consultar campeão
go run main.go -ano=2024

# Consultar rodada
go run main.go -ano=2024 -rodada=38
```

Exemplo de saída:
```bash
Campeão do Brasileirão 2024: Botafogo


Jogos da rodada 38 do Brasileirão 2024:

08/12: Flamengo 2-2 Vitória
08/12: Botafogo 2-1 São Paulo

```

### Teste Direto do Scraper (Opcional)
Duas opções para testar o scraper sem a API:

1. Usando código direto no Python:
```python
from cbf_scraper import BrasileiraoScraper

scraper = BrasileiraoScraper("2024")

# Consultar campeão
campeao = scraper.get_champion()
# {"ano": "2024", "campeao": "Botafogo"}

# Consultar rodada
jogos = scraper.get_round_data("38")
# {
#   "ano": "2024",
#   "rodada": "38",
#   "jogos": [
#     {
#       "data": "08/12/2024",
#       "mandante": {"nome": "Botafogo", "gols": 2},
#       "visitante": {"nome": "São Paulo", "gols": 1},
#       "placar": "2-1"
#     }
#   ]
# }
```