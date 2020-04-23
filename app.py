#Para executar - Comando: python app.py
#Posso add varias routes com @app.route
#/ <string:name>, <int:id> etc...
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, requests

app = Flask(__name__)
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


@app.route('/home/users/<string:name>/posts/<int:id>') #Localhost
def hello(name, id):
    return "Hello, "+name+", your stupid number is " + str(id)

@app.route('/onlyget', methods=['GET']) #Unicos metodos permitidos
def get_req():
    response = requests.get('http://127.0.0.1:5000/requests')
    print(response.status_code)

    quests = json.loads(response.content)

    for quest in quests:
        print(quest['name'])

    return response.content

@app.route('/posts', methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':

        headers = {"Authorization": "Bearer "+ _auth_}

        url = 'http://127.0.0.1:5000/request'

        data = {'name': request.form['name'],
                'address': request.form['address'],
                'author': request.form['author'],
                'accepted': "No",
                'done': "No"
                }
        print("posted")
        x = requests.post(url, data = data, headers = headers)

        return redirect('/my_posts')
    else:
        response = requests.get('http://127.0.0.1:5000/requests')
        quests = json.loads(response.content)
        return render_template('posts.html', quests=quests)

@app.route('/my_posts', methods=['GET', 'POST'])
def my_posts():
    if request.method == 'POST':
        headers = {"Authorization": "Bearer "+ _auth_}

        url = 'http://127.0.0.1:5000/request'

        data = {'name': request.form['name'],
                'address': request.form['address'],
                'author': request.form['author'],
                'accepted': "No",
                'done': "No"
                }
        print("posted")
        x = requests.post(url, data = data, headers = headers)

        return redirect('/my_posts')
        
    else:
        headers = {"Authorization": "Bearer "+ _auth_}
        response = requests.get('http://127.0.0.1:5000/requests_user', headers=headers)
        currentuser = requests.get('http://127.0.0.1:5000/currentuser', headers=headers)

        print(response.text)
        print(currentuser.text)

        quests = json.loads(response.content)
        currentuser = json.loads(currentuser.content)
        return render_template('my_posts.html', quests=quests)

@app.route("/posts/<int:id>")
def get_quest(id):
    response = requests.get('http://127.0.0.1:5000/request/'+str(id))
    quest = json.loads(response.content)
    return render_template('quest.html', quest=quest)

@app.route('/posts/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/posts')

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('edit.html', post = post)

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':

        headers = {"Authorization": "Bearer "+ _auth_}

        url = 'http://127.0.0.1:5000/request'

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
        
        url = 'http://127.0.0.1:5000/item/'+str(request.form['name'])

        headers = {"Authorization": "Bearer "+ _auth_}
        requests.post(url, data = data, headers = headers)
        return redirect('/posts/new_item/'+str(quest_id))
    else:
        response = requests.get('http://127.0.0.1:5000/request/'+str(quest_id))
        quest = json.loads(response.content)
        return render_template('new_item.html', quest=quest)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        url = 'http://127.0.0.1:5000/register'
        data = {'username': request.form['username'],
                'password': request.form['password'],
                'name': request.form['name'],
                'email': request.form['email']
                }

        x = requests.post(url, data = data)

        print(x.text)

        return redirect('/posts')
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        url = 'http://127.0.0.1:5000/login'
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