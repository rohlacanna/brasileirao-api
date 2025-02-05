from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ScraperConfig:
    base_url: str = "https://www.ogol.com.br"
    headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    @property
    def search_url(self) -> str:
        return f"{self.base_url}/competicao/brasileirao?search=1"

@dataclass
class Match:
    date: str
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    
    @property
    def score(self) -> str:
        return f"{self.home_goals}-{self.away_goals}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.date,
            "mandante": {"nome": self.home_team, "gols": self.home_goals},
            "visitante": {"nome": self.away_team, "gols": self.away_goals},
            "placar": self.score
        }