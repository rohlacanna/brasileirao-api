from flask import Flask, jsonify, Response
from http import HTTPStatus
from typing import Tuple, Dict, Any
from functools import wraps
from cbf_scraper import BrasileiraoScraper, WebScraper, ScraperConfig

app = Flask(__name__)
scraper = WebScraper(ScraperConfig())

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[Response, int]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return create_error_response(
                f"Erro ao buscar dados: {str(e)}",
                HTTPStatus.INTERNAL_SERVER_ERROR
            )
    return wrapper

def create_error_response(message: str, status_code: int) -> Tuple[Response, int]:
    return jsonify({"erro": message}), status_code

def validate_brasileirao_data(data: Dict[str, Any], data_type: str, year: str) -> Tuple[Response, int]:
    if not data or not data.get(data_type):
        error_messages = {
            'jogos': f"Não foram encontrados jogos para o ano {year}",
            'campeao': f"Ainda não houve campeão para o Brasileirão {year}"
        }
        return create_error_response(error_messages[data_type], HTTPStatus.NOT_FOUND)
    return jsonify(data), HTTPStatus.OK

@app.route('/jogos/<ano>/<rodada>')
@handle_errors
def get_jogos(ano: str, rodada: str) -> Tuple[Response, int]:
    brasileirao = BrasileiraoScraper(ano, scraper)
    result = brasileirao.get_round_data(rodada)
    return validate_brasileirao_data(result, 'jogos', ano)

@app.route('/campeao/<ano>')
@handle_errors
def get_campeao(ano: str) -> Tuple[Response, int]:
    brasileirao = BrasileiraoScraper(ano, scraper)
    result = brasileirao.get_champion()
    return validate_brasileirao_data(result, 'campeao', ano)

if __name__ == '__main__':
    app.run(port=8000)