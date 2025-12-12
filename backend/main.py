from flask import Flask, request, render_template
import os


app = Flask(__name__, template_folder="../frontend", static_folder="../frontend")
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

main_path = os.path.join(root_dir, 'frontend', 'main', 'main.html')


@app.route('/')
def mains():
    return render_template('main/main.html')


@app.route('/game', methods=['GET', 'POST'])
def play_game():
    if request.method == 'POST':
        pass
    else:
        return render_template('igra/igra.html')


app.run(debug=True)
