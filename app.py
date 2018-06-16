from flask import Flask, render_template,request
from werkzeug.utils import secure_filename
#posgresqlへアクセスするモジュール
import psycopg2
import psycopg2.extras
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/web_eng'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app,db)

#データベースの構造を変えたら
# flask db update　コマンドをうってマイグレーとする。
#userのdb
class User_table(db.Model):
    id= db.Column(db.Integer,primary_key =True)
    username = db.Column(db.String(20),index=True,unique=True)
    def __repr__(self):
        return '<User %r>'%self.username

class Goods_table(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    goods_name=db.Column(db.String(40))
    rental_fee=db.Column(db.Integer)
    description=db.Column(db.String(100))
    def __repr__(self):
        return '<User %r>'%self.username

@app.route('/test')
def register():
    new_User=User_table(username='shumpei_kikuta')
    db.session.add(new_User)
    db.session.commit()
    # username = 'shumpei kikuta'
    return render_template('result.html',username = new_User)


@app.route('/')
def index():
    return render_template('home_page.html')

@app.route("/sign_up",methods=["GET"])
def sign_up():
    return render_template('sign_up.html')

@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html")

@app.route("/top_page",methods=["POST","GET"])
def login():
    goods = Goods_table.query.all()
    if request.method =="POST":
        if request.form['username'] and request.form['password']:
            username = request.form['username']
            return render_template("top_page.html",username=username,goods =goods)
        else:
            return render_template("error.html")
    elif request.method== "GET":
        username = "ゲスト"
        return render_template("top_page.html",username=username,goods=goods)

@app.route("/post_goods")
def post_goods():
    return render_template("post_goods.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/complete_post_goods",methods=["POST"])
def complete_post_goods():
    if request.form['goods_name'] and request.form['rental_fee'] and request.form["description"]:
        goods_name = request.form['goods_name']
        rental_fee = request.form['rental_fee']
        description = request.form['description']
        new_goods = Goods_table(goods_name=goods_name,rental_fee=rental_fee,description=description)
        db.session.add(new_goods)
        db.session.commit()
        return render_template("complete_post_goods.html",goods_name=goods_name,rental_fee=rental_fee,description=description)
    else:
        return render_template("error.html")

#テーブルの初期化のコマンド、これをしないとSQLAlchemyがdbにアクセスできない。
@app.cli.command('initdb')
def initdb_command():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
