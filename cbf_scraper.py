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

    @staticmethod
    def _create_error(message: str) -> Dict[str, str]:
        return {"erro": message}

    @staticmethod
    def _handle_error(message: str) -> None:
        print(json.dumps({"erro": message}, ensure_ascii=False))

def main():
    if len(sys.argv) != 2:
        print("Uso: python cbf_scraper.py <ano>")
        sys.exit(1)

    scraper = BrasileiraoScraper(sys.argv[1])
    result = scraper.get_champion()
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()