from typing import Optional, Dict, Any, List
import requests
from bs4 import BeautifulSoup, Tag
from .models import Match, ScraperConfig

class WebScraper:
    def __init__(self, config: ScraperConfig = ScraperConfig()):
        self.config = config
        self.session = self._initialize_session()
    
    def _initialize_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(self.config.headers)
        return session

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException:
            return None

class BrasileiraoScraper:
    def __init__(self, year: str, scraper: WebScraper = None):
        self.year = year
        self.scraper = scraper or WebScraper()
        self.config = self.scraper.config

    def get_champion(self) -> Dict[str, Any]:
        form_value = self._fetch_form_value()
        if not form_value:
            return self._error_response(f"Valor não encontrado para o ano {self.year}")

        champion_name = self._fetch_champion_name(form_value)
        if not champion_name:
            return self._error_response("Dados do campeão não encontrados")

        return {"ano": self.year, "campeao": champion_name}

    def get_round_data(self, round_number: str) -> Dict[str, Any]:
        form_value = self._fetch_form_value()
        if not form_value:
            return self._error_response(f"Valor não encontrado para o ano {self.year}")

        phase_id = self._fetch_phase_id(form_value)
        if not phase_id:
            return self._error_response("ID da fase não encontrado")

        matches = self._fetch_matches(form_value, round_number, phase_id)
        if not matches:
            return self._error_response(f"Dados da rodada {round_number} não encontrados")

        return {
            "ano": self.year,
            "rodada": round_number,
            "jogos": [match.to_dict() for match in matches]
        }

    def _fetch_form_value(self) -> Optional[str]:
        soup = self.scraper.get_soup(self.config.search_url)
        if not soup:
            return None

        form = soup.find('select', id='id_edicao')
        if not form:
            return None

        return next(
            (option['value'] for option in form.find_all('option')
             if option.text.strip() == str(self.year)),
            None
        )

    def _fetch_champion_name(self, form_value: str) -> Optional[str]:
        url = f"{self.config.base_url}/edicao/brasileirao-serie-a-{self.year}/{form_value}"
        soup = self.scraper.get_soup(url)
        if not soup:
            return None

        champion_cell = self._find_champion_cell(soup)
        return champion_cell.text.strip() if champion_cell else None

    def _find_champion_cell(self, soup: BeautifulSoup) -> Optional[Tag]:
        table = soup.find('div', id='edition_table')
        if not table:
            return None

        first_row = table.find('tbody').find('tr')
        if not first_row:
            return None

        return first_row.find_all('td')[2].find('a')

    def _fetch_phase_id(self, form_value: str) -> Optional[str]:
        url = f"{self.config.base_url}/edicao/brasileirao-serie-a-{self.year}/{form_value}"
        soup = self.scraper.get_soup(url)
        if not soup:
            return None

        phase_input = soup.find('input', {'name': 'fase'})
        return phase_input.get('value') if phase_input else None

    def _fetch_matches(self, form_value: str, round_number: str, phase_id: str) -> Optional[List[Match]]:
        url = self._build_matches_url(form_value, round_number, phase_id)
        soup = self.scraper.get_soup(url)
        if not soup:
            return None

        return self._parse_matches_table(soup)

    def _build_matches_url(self, form_value: str, round_number: str, phase_id: str) -> str:
        return f"{self.config.base_url}/edicao/campeonato-brasileiro-{self.year}/{form_value}?jornada_in={round_number}&fase={phase_id}"

    def _parse_matches_table(self, soup: BeautifulSoup) -> Optional[List[Match]]:
        games_table = self._find_games_table(soup)
        if not games_table:
            return None

        matches = []
        current_date = None

        for row in games_table.find_all('tr'):
            match = self._parse_match_row(row, current_date)
            if match:
                matches.append(match)
                current_date = match.date

        return matches if matches else None

    def _find_games_table(self, soup: BeautifulSoup) -> Optional[Tag]:
        fixture_div = soup.find('div', id='fixture_games')
        if not fixture_div:
            return None
        return fixture_div.find('table', class_='zztable stats')

    def _parse_match_row(self, row: Tag, current_date: str) -> Optional[Match]:
        try:
            cells = row.find_all('td')
            if len(cells) < 6:
                return None

            date = cells[0].text.strip() or current_date
            if not date:
                return None

            home_team = cells[1].find('a').text.strip()
            score = cells[3].find('a').text.strip()
            away_team = cells[5].find('a').text.strip()

            if not (home_team and away_team and score and '-' in score):
                return None

            home_goals, away_goals = map(lambda x: int(x.strip()), score.split('-'))
            
            return Match(date, home_team, away_team, home_goals, away_goals)

        except (AttributeError, ValueError, IndexError):
            return None

    @staticmethod
    def _error_response(message: str) -> Dict[str, str]:
        return {"erro": message}