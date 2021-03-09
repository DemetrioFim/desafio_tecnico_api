from flask import Flask, render_template, request, url_for, redirect
import db
import requests
from threading import Thread

app = Flask(__name__)

user = db.User()
super_admin = db.SuperAdmin()

@app.route("/")
def beginning():
    return redirect(url_for('login'))

@app.route("/login", methods=['GET','POST'])
def login():
    global user
    global super_admin
    global app
    if request.method == 'POST':
        if request.form['button'] == 'ENTRAR':

            name = request.form['name_cliente']
            email = request.form['email_cliente']

            try:
                user = db.User()
                user.get_user_info(name, email)
            except:
                user = None
                return render_template('login.html', login_fail=True)

            return redirect(url_for('products', page_number=1))

        elif request.form['button'] == 'CADASTRAR':
            return redirect(url_for('register'))

        elif request.form['button'] == 'SUPERADMIN':
            super_admin = db.SuperAdmin()
            return redirect(url_for('superadmin'))
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    global user
    global super_admin
    user = None
    super_admin = None
    return redirect(url_for('login'))

@app.route("/register", methods=['GET','POST'])
def register():
    global user
    if request.method == 'POST':
        user = db.User()
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

@app.route('/superadmin', methods=['GET','POST'])
def superadmin():
    global super_admin
    print(request.form)
    if request.method == 'POST':
        if 'logout' in request.form:
            return redirect(url_for('logout'))
        elif 'cliente_token' in request.form:
            cliente_token = request.form['cliente_token']
            if cliente_token != '':
                columns, values = super_admin.get_favorite_by_token(cliente_token)
            else:
                columns, values = super_admin.get_all_favorite_table()
    else:
        columns, values = super_admin.get_all_favorite_table()

    favorites_columns, favorite_final_list = get_favorites_info(values=values)
    clientes_columns, clientes_values= get_clientes_info()

    return render_template('superadmin.html',
                           favorites_columns=favorites_columns,
                           favorites_values=favorite_final_list,
                           clientes_columns=clientes_columns,
                           clientes_values=clientes_values
                           )


def get_favorites_info(values):
    global super_admin
    list_favorites = [None for _ in values]
    list_threads = []
    list_tokens = []
    for index, value in enumerate(values):
        list_tokens.append(value[0])
        id_produto = value[1]
        thread = Thread(target=super_admin.set_api_info_into_list, args=(id_produto, list_favorites, index,))
        list_threads.append(thread)
        thread.start()

    for thread in list_threads:
        thread.join()

    favorite_final_list = []
    favorites_columns = ['cliente_name', 'cliente_token', 'title','brand', 'id', 'price']
    for index, row in enumerate(list_favorites):
        lista = [super_admin.get_cliente_name_by_token(list_tokens[index]),
                 list_tokens[index],
                 row['title'],
                 row['brand'],
                 row['id'],
                 row['price']
        ]
        favorite_final_list.append(lista)

    return favorites_columns, favorite_final_list

def get_clientes_info():
    global super_admin
    df = super_admin.get_all_clientes(indf=True)
    columns = ['cliente_name', 'cliente_email', 'cliente_token']
    values = df[columns].values.tolist()
    return columns, values

if __name__ == '__main__':
    app.run()
