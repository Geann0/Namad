
from flask import Flask, render_template, request, jsonify, session
import random
import json
import unicodedata
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

class HistoricalFigureGameWeb:
    def __init__(self):
        self.figures = self.load_figures_from_file("historical_figures.json")
        
    def get_figure_image_url(self, character_name):
        # Aqui você pode definir um mecanismo para mapear nomes para URLs de imagens.
        # No exemplo, vamos supor que as imagens têm o mesmo nome do personagem.
        return f"https://meusite.com/imagens/{character_name.replace(' ', '_').lower()}.jpg"
        try:
            with open(filename, "r", encoding='utf-8') as file:
                figures = json.load(file)
            return figures
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def normalize_string(self, s):
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8').lower()

    def calculate_score(self, figure_name):
        difficulty_factor = 1.0 + len(figure_name) / 10.0
        return int(10 * difficulty_factor)

game = HistoricalFigureGameWeb()

@app.route('/')
def index():
    if 'score' not in session:
        session['score'] = 0
        session['money'] = 0
        session['lives'] = 3
        session['advantages'] = {
            "dicas": {"quantidade": 3, "custo": 5},
            "pulo": {"quantidade": 2, "custo": 10},
            "pesquisa": {"quantidade": 1, "custo": 20}
        }
        session['hints_used'] = 0
    
    if 'current_figure' not in session or not session['current_figure']:
        new_figure()
    
    return render_template('index.html')

def new_figure():
    if game.figures:
        session['current_figure'] = random.choice(game.figures)
        session['hints_used'] = 0

@app.route('/get_game_state')
def get_game_state():
    return jsonify({
        'fact': session.get('current_figure', {}).get('fact', ''),
        'score': session.get('score', 0),
        'money': session.get('money', 0),
        'lives': session.get('lives', 3),
        'advantages': session.get('advantages', {}),
        'hints_used': session.get('hints_used', 0)
    })

@app.route('/guess', methods=['POST'])
def guess():
    data = request.json
    guessed_name = game.normalize_string(data.get('guess', '').strip())
    
    if not guessed_name:
        return jsonify({'success': False, 'message': 'Digite o nome do personagem!'})
    
    current_figure = session.get('current_figure', {})
    correct_name = game.normalize_string(current_figure.get('name', ''))
    
    if guessed_name == correct_name:
        score_gained = game.calculate_score(current_figure.get('name', ''))
        session['score'] += score_gained
        session['money'] += 10
        new_figure()
        return jsonify({
            'success': True, 
            'correct': True,
            'message': f'Parabéns! Você acertou.\n{current_figure.get("name")}: {current_figure.get("fact")}',
            'score_gained': score_gained
        })
    else:
        session['lives'] -= 1
        if session['lives'] <= 0:
            session['score'] = 0
            session['lives'] = 3
            session['money'] = 0
            session['advantages'] = {
                "dicas": {"quantidade": 3, "custo": 5},
                "pulo": {"quantidade": 2, "custo": 10},
                "pesquisa": {"quantidade": 1, "custo": 20}
            }
            new_figure()
            return jsonify({
                'success': True,
                'correct': False,
                'game_over': True,
                'message': f'Fim de jogo! A resposta era: {current_figure.get("name")}'
            })
        else:
            new_figure()
            return jsonify({
                'success': True,
                'correct': False,
                'message': f'Incorreto! A resposta era: {current_figure.get("name")}'
            })

@app.route('/use_hint', methods=['POST'])
def use_hint():
    advantages = session.get('advantages', {})
    if advantages.get('dicas', {}).get('quantidade', 0) > 0:
        session['hints_used'] += 1
        advantages['dicas']['quantidade'] -= 1
        session['advantages'] = advantages
        
        current_figure = session.get('current_figure', {})
        hint = current_figure.get('name', '')[:session['hints_used']]
        hint += '_' * (len(current_figure.get('name', '')) - session['hints_used'])
        
        return jsonify({'success': True, 'hint': hint})
    else:
        return jsonify({'success': False, 'message': 'Você não possui mais dicas!'})

@app.route('/use_skip', methods=['POST'])
def use_skip():
    advantages = session.get('advantages', {})
    if advantages.get('pulo', {}).get('quantidade', 0) > 0:
        advantages['pulo']['quantidade'] -= 1
        session['advantages'] = advantages
        new_figure()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Você não possui mais pulos!'})

@app.route('/buy_item', methods=['POST'])
def buy_item():
    data = request.json
    item = data.get('item')
    
    advantages = session.get('advantages', {})
    money = session.get('money', 0)
    
    if item in advantages and money >= advantages[item]['custo']:
        advantages[item]['quantidade'] += 1
        session['money'] -= advantages[item]['custo']
        session['advantages'] = advantages
        return jsonify({'success': True, 'message': f'{item.capitalize()} comprado com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Dinheiro insuficiente!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
