from flask import Flask, jsonify
from cbf_scraper import BrasileiraoScraper

app = Flask(__name__)

@app.route('/jogos/<ano>/<rodada>')
def get_jogos(ano, rodada):
    try:
        scraper = BrasileiraoScraper(ano)
        result = scraper.get_round_data(rodada)
        
        if not result or not result.get('jogos'):
            return jsonify({
                "erro": f"Não foram encontrados jogos para o ano {ano} e rodada {rodada}"
            }), 404
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "erro": f"Erro ao buscar dados: {str(e)}"
        }), 500

@app.route('/campeao/<ano>')
def get_campeao(ano):
    try:
        scraper = BrasileiraoScraper(ano)
        result = scraper.get_champion()
        
        if not result or not result.get('campeao'):
            return jsonify({
                "erro": f"Ainda não houve campeão para o Brasileirão {ano}"
            }), 404
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "erro": f"Erro ao buscar dados: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(port=8000) 