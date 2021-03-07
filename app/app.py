from flask import Flask, render_template, request, url_for, redirect
import db

app = Flask(__name__)
user = db.User()

@app.route("/")
def beginning():
    print(url_for('login'))
    print(url_for('register'))
    return redirect(url_for('login'))

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        print(request.form)
        if request.form['button'] == 'ENTRAR':
            name = request.form['name_cliente']
            email = request.form['email_cliente']
            try:
                user.get_user_info(name, email)
            except Exception as e:
                print(e)
                return render_template('login.html', login_fail=True)
        elif request.form['button'] == 'CADASTRAR':
            return redirect(url_for('register'))
    else:
        return render_template('login.html')

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        if request.form['button'] == 'CADASTRAR':
            name = request.form['name_cliente']
            email = request.form['email_cliente']
            try:
                user.insert_into_clientes(name, email)
                return render_template('register.html', register_sucess=True)
            except:
                return render_template('register.html', register_fail=True)
        elif request.form['button'] == 'LOGIN':
            return redirect(url_for('login'))
    else:
        return render_template('register.html')

if __name__ == '__main__':
    app.run()
