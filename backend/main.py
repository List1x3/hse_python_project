from flask import Flask, request, render_template
import os
import web_api


app = Flask(__name__, template_folder="../frontend", static_folder="../frontend")
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

main_path = os.path.join(root_dir, 'frontend', 'main', 'main.html')
app.register_blueprint(web_api.bp)

@app.route('/')
def mains():
    return render_template('main/main.html')


@app.route('/game/<n>', methods=['GET', 'POST'])
def play_game(n):
    if request.method == 'POST':
        pass
    else:
        return render_template('igra/igra.html', N=n)


@app.route('/game_bot/<n>', methods=['GET', 'POST'])
def play_game_bot(n):
    if request.method == 'POST':
        pass
    else:
        return render_template('igra_bot/igra_bot.html', N=n)


@app.route('/game_bot_mcts/<n>', methods=['GET', 'POST'])
def play_game_bot_mcts(n):
    if request.method == 'POST':
        pass
    else:
        return render_template('igra_bot_mcts/igra_bot_mcts.html', N=n)


app.run(debug=True)
