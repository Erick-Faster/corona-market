#Para executar - Comando: python app.py
#Posso add varias routes com @app.route
#/ <string:name>, <int:id> etc...
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, requests

app = Flask(__name__)
app.secret_key = 'SECRETKEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(app)

_auth_ = 'None'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default='Desconhecido')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Blog post ' + str(self.id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':

        headers = {"Authorization": "Bearer "+ _auth_}
        url = 'https://coronamarket-api.herokuapp.com//request'

        data = {'name': request.form['name'],
                'address': request.form['address'],
                'author': request.form['author'],
                'accepted': "No",
                'done': "No"
                }
        print("posted")
        response = requests.post(url, data = data, headers = headers)

        if response.status_code == 401:
            return redirect('/login')

        return redirect('/my_posts')
    else:
        response = requests.get('https://coronamarket-api.herokuapp.com//requests')
        quests = json.loads(response.content)
        return render_template('posts.html', quests=quests)

@app.route('/my_posts', methods=['GET', 'POST'])
def my_posts():
    if request.method == 'POST':
        headers = {"Authorization": "Bearer "+ _auth_}

        url = 'https://coronamarket-api.herokuapp.com//request'

        data = {'name': request.form['name'],
                'address': request.form['address'],
                'author': request.form['author'],
                'accepted': "No",
                'done': "No"
                }
        print("posted")
        
        response = requests.post(url, data = data, headers = headers)

        if response.status_code == 401:
            return redirect('/login')

        return redirect('/my_posts')
        
    else:
        headers = {"Authorization": "Bearer "+ _auth_}
        response = requests.get('https://coronamarket-api.herokuapp.com//requests_user', headers=headers)

        if response.status_code == 401:
            return redirect('/login')
        #currentuser = requests.get('http://127.0.0.1:5080/currentuser', headers=headers)

        print(response.text)
        #print(currentuser.text)

        quests = json.loads(response.content)
        #currentuser = json.loads(currentuser.content)
        return render_template('my_posts.html', quests=quests)

@app.route("/posts/<int:id>")
def get_quest(id):
    response = requests.get('https://coronamarket-api.herokuapp.com//request/'+str(id))
    quest = json.loads(response.content)
    return render_template('quest.html', quest=quest)

@app.route('/my_posts/delete/<int:id>')
def delete(id):
    headers = {"Authorization": "Bearer "+ _auth_}
    response = requests.delete('https://coronamarket-api.herokuapp.com//request/'+str(id), headers = headers)

    if response.status_code == 401:
        return redirect('/login')
    print("Deletado?")

    return redirect('/my_posts')

@app.route('/posts/accepted/<int:id>', methods=['GET', 'POST'])
def accepted(id):

    response = requests.get('https://coronamarket-api.herokuapp.com//request/'+str(id))

    response = json.loads(response.content)

    data = {'name': response['name'],
            'address': response['address'],
            'author': response['author'],
            'accepted': "Yes",
            'done': "No",
            }

    headers = {"Authorization": "Bearer "+ _auth_}
    url = 'https://coronamarket-api.herokuapp.com//request/'+str(id)
    put_response = requests.put(url, data = data, headers = headers)

    if put_response.status_code == 401:
        return redirect('/login')

    flash('O pedido foi aceito! Parabéns!')

    return redirect('/posts')

@app.route('/my_posts/done/<int:id>', methods=['GET', 'POST'])
def done(id):

    response = requests.get('https://coronamarket-api.herokuapp.com//request/'+str(id))
    response = json.loads(response.content)

    data = {'name': response['name'],
            'address': response['address'],
            'author': response['author'],
            'accepted': "Yes",
            'done': "Yes",
            }

    headers = {"Authorization": "Bearer "+ _auth_}
    url = 'https://coronamarket-api.herokuapp.com//request/'+str(id)
    put_response = requests.put(url, data = data, headers = headers)

    if put_response.status_code == 401:
        return redirect('/login')

    flash('O pedido foi encerrado! Parabéns')

    return redirect('/my_posts')


@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':

        headers = {"Authorization": "Bearer "+ _auth_}

        url = 'https://coronamarket-api.herokuapp.com//request'

        print("posted")

        data = {'name': request.form['name'],
                'address': request.form['address'],
                'author': request.form['author'],
                'accepted': "No",
                'done': "No"
                }

        x = requests.post(url, data = data, headers = headers)

        x = json.loads(x.content)

        print(x)

        quest_id = str(x['id'])


        return redirect('/posts/new_item/'+quest_id)
    else:
        return render_template('new_post.html')

@app.route('/posts/new_item/<int:quest_id>', methods=['GET', 'POST'])
def new_item(quest_id):
    if request.method == 'POST':

        data = {'quantity': request.form['quantity'],
                'price': request.form['price'],
                'request_id': quest_id
                }
        
        url = 'https://coronamarket-api.herokuapp.com//item/'+str(request.form['name'])

        headers = {"Authorization": "Bearer "+ _auth_}
        response = requests.post(url, data = data, headers = headers)

        if response.status_code == 401:
            return redirect('/login')

        return redirect('/posts/new_item/'+str(quest_id))
    else:
        response = requests.get('https://coronamarket-api.herokuapp.com//request/'+str(quest_id))
        quest = json.loads(response.content)
        return render_template('new_item.html', quest=quest)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        url = 'https://coronamarket-api.herokuapp.com//register'
        register = {'username': request.form['username'],
                    'password': request.form['password'],
                   }

        registerResponse = requests.post(url, data = register)
        response = json.loads(registerResponse.content)

        data = {'username': response['username'],
                'name': request.form['name'],
                'email': request.form['email'],
                'group': request.form['group'],
                'user_id': response['id']
                }

        url = 'https://coronamarket-api.herokuapp.com//userinfo'
        x = requests.post(url, data = data)

        print(x.text)

        return redirect('/posts')
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        url = 'https://coronamarket-api.herokuapp.com//login'
        data = {'username': request.form['username'],
                'password': request.form['password']
                }

        tokens = requests.post(url, data = data)
        tokens = json.loads(tokens.content)

        global _auth_
        _auth_ = tokens['access_token']

        print(_auth_)

        return redirect('/my_posts')
    else:
        return render_template('login.html')

if __name__ == "__main__":
    app.run(port=4000, debug=True)
