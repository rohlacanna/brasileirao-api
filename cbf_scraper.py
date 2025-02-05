import requests
from bs4 import BeautifulSoup
import json
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class Config:
    BASE_URL = "https://www.ogol.com.br"
    SEARCH_URL = f"{BASE_URL}/competicao/brasileirao?search=1"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Config.HEADERS)

    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            self._handle_error(f"Erro ao acessar a página: {str(e)}")
            return None

class BrasileiraoScraper(WebScraper):
    def __init__(self, ano: str):
        super().__init__()
        self.ano = ano

    def get_champion(self) -> Dict[str, Any]:
        try:
            form_value = self._get_form_value()
            if not form_value:
                return self._create_error(f"Valor não encontrado para o ano {self.ano}")

            champion_data = self._get_champion_data(form_value)
            if not champion_data:
                return self._create_error("Dados do campeão não encontrados")

            return {"ano": self.ano, "campeao": champion_data}

        except Exception as e:
            return self._create_error(f"Erro inesperado: {str(e)}")

    def get_round_data(self, rodada: str) -> Dict[str, Any]:
        try:
            form_value = self._get_form_value()
            if not form_value:
                return self._create_error(f"Valor não encontrado para o ano {self.ano}")

            fase_id = self._get_fase_id(form_value)
            if not fase_id:
                return self._create_error("ID da fase não encontrado")

            round_data = self._get_matches_data(form_value, rodada, fase_id)
            if not round_data:
                return self._create_error(f"Dados da rodada {rodada} não encontrados")

            return {
                "ano": self.ano,
                "rodada": rodada,
                "jogos": round_data
            }

        except Exception as e:
            return self._create_error(f"Erro inesperado: {str(e)}")

    def _get_form_value(self) -> Optional[str]:
        soup = self.get_page(Config.SEARCH_URL)
        if not soup:
            return None

        form = soup.find('select', id='id_edicao')
        if not form:
            return None

        for option in form.find_all('option'):
            if option.text.strip() == str(self.ano):
                return option['value']
        return None

    def _get_champion_data(self, form_value: str) -> Optional[str]:
        url = f"{Config.BASE_URL}/edicao/brasileirao-serie-a-{self.ano}/{form_value}"
        soup = self.get_page(url)
        if not soup:
            return None

        table = soup.find('div', id='edition_table')
        if not table:
            return None

        first_row = table.find('tbody').find('tr')
        if not first_row:
            return None

        champion_cell = first_row.find_all('td')[2].find('a')
        return champion_cell.text.strip() if champion_cell else None

    def _get_fase_id(self, form_value: str) -> Optional[str]:
        url = f"{Config.BASE_URL}/edicao/brasileirao-serie-a-{self.ano}/{form_value}"
        soup = self.get_page(url)
        if not soup:
            return None

        fase_input = soup.find('input', {'name': 'fase'})
        return fase_input.get('value') if fase_input else None

    def _get_matches_data(self, form_value: str, rodada: str, fase_id: str) -> Optional[list]:
        url = f"{Config.BASE_URL}/edicao/campeonato-brasileiro-{self.ano}/{form_value}?jornada_in={rodada}&fase={fase_id}"
        
        soup = self.get_page(url)
        if not soup:
            return None

        fixture_div = soup.find('div', id='fixture_games')
        if not fixture_div:
            return None

        games_table = fixture_div.find('table', class_='zztable stats')
        if not games_table:
            return None

        matches = []
        last_date = None
        
        for row in games_table.find_all('tr'):
            try:
                cells = row.find_all('td')
                if len(cells) < 6:
                    continue
                
                date_text = cells[0].text.strip()
                if date_text:
                    last_date = date_text
                
                mandante = cells[1].find('a').text.strip()
                placar = cells[3].find('a').text.strip()
                visitante = cells[5].find('a').text.strip()
                
                if mandante and visitante and placar and '-' in placar:
                    gols = placar.split('-')
                    matches.append({
                        "data": last_date,
                        "mandante": {
                            "nome": mandante,
                            "gols": int(gols[0].strip())
                        },
                        "visitante": {
                            "nome": visitante,
                            "gols": int(gols[1].strip())
                        },
                        "placar": placar
                    })
            
            except Exception as e:
                continue

        return matches if matches else None

    @staticmethod
    def _create_error(message: str) -> Dict[str, str]:
        return {"erro": message}

    @staticmethod
    def _handle_error(message: str) -> None:
        print(json.dumps({"erro": message}, ensure_ascii=False))

def main():
    if len(sys.argv) < 2:
        print("Uso: python cbf_scraper.py <ano> [rodada]")
        sys.exit(1)

    scraper = BrasileiraoScraper(sys.argv[1])
    
    if len(sys.argv) == 3:
        result = scraper.get_round_data(sys.argv[2])
    else:
        result = scraper.get_champion()
        
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()