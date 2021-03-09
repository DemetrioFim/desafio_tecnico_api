from flask import Flask, render_template, request, url_for, redirect
import db
import requests
from threading import Thread

app = Flask(__name__)

user = None

@app.route("/")
def beginning():
    return redirect(url_for('login'))

@app.route("/login", methods=['GET','POST'])
def login():
    global user
    global app
    if request.method == 'POST':
        if request.form['button'] == 'ENTRAR':
            user = db.User()
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

@app.route('/logout')
def logout():
    global user
    user = None
    return redirect(url_for('login'))

@app.route("/register", methods=['GET','POST'])
def register():
    global user
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
    global user
    page_number = int(page_number)
    if request.method == 'POST':
        if 'change_page' in request.form:
            if request.form['change_page'] == '>':
                page_number += 1

            elif request.form['change_page'] == '<':
                page_number -= 1

        elif 'button_favorite' in request.form:
            if request.form['button_favorite'] == 'favoritar':
                id_produto = request.form['id_produto']
                user.insert_into_favorites(id_produto=id_produto)

            elif request.form['button_favorite'] == 'desfavoritar':
                id_produto = request.form['id_produto']
                user.remove_from_favorites(id_produto=id_produto)

        elif 'my_favorites' in request.form:
            return redirect(url_for('favoritos'))

        elif 'logout' in request.form:
            return redirect(url_for('logout'))

        return redirect(url_for('products', page_number=page_number))

    elif request.method == 'GET':
        response = requests.get(f'http://challenge-api.luizalabs.com/api/product/?page={page_number}')
        data = response.json()
        list_products = data['products']
        return render_template('products.html',
                               list_products=list_products,
                               page_number=page_number,
                               favoritos=user.get_list_favorites()
                               )

@app.route('/favoritos', methods=['GET', 'POST'])
def favoritos():
    global user
    print(user)
    if request.method == 'POST':
        if 'button_favorite' in request.form:
            user.remove_from_favorites(request.form['id_produto'])
        if 'produtos' in request.form:
            return redirect(url_for('products', page_number=1))

    full_list_favoritos = [None for _ in user.get_list_favorites()]
    thread_list = []
    for index, id_produto in enumerate(user.get_list_favorites()):
        x = Thread(target=user.set_api_info_into_list, args=(id_produto, full_list_favoritos, index))
        thread_list.append(x)
        x.start()

    for thread in thread_list:
        thread.join()

    return render_template('favoritos.html',
                           full_list_favoritos=full_list_favoritos,
                           favoritos=user.get_list_favorites())

if __name__ == '__main__':
    app.run()
