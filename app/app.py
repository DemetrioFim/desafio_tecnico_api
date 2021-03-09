from flask import Flask, render_template, request, url_for, redirect
import db
import requests

app = Flask(__name__)
user = db.User()

@app.route("/")
def beginning():
    return redirect(url_for('login'))

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':

        if request.form['button'] == 'ENTRAR':
            name = request.form['name_cliente']
            email = request.form['email_cliente']

            try:
                user.get_user_info(name, email)
            except:
                return render_template('login.html', login_fail=True)

            return redirect(url_for('products', page_number=1))

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

@app.route('/products/<page_number>', methods=['GET', 'POST'])
def products(page_number):
    page_number = int(page_number)
    if request.method == 'POST':
        print(request.form)
        if request.form['change_page'] == '>':
            page_number += 1
        elif request.form['change_page'] == '<':
            page_number -= 1
        return redirect(url_for('products', page_number=page_number))

    elif request.method == 'GET':
        response = requests.get(f'http://challenge-api.luizalabs.com/api/product/?page={page_number}')
        data = response.json()
        list_products = data['products']
        return render_template('products.html', list_products=list_products, page_number=page_number)

if __name__ == '__main__':
    app.run()
