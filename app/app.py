from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route("/")
def beginning():
    return redirect(url_for('main'))

@app.route("/main")
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run()