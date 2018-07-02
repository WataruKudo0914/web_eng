from flask import Flask, render_template,request, make_response ,session ,redirect, url_for
from werkzeug.utils import secure_filename
#posgresqlへアクセスするモジュール
import psycopg2
import psycopg2.extras
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, UserMixin,logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/web_eng'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ufawifyagwer1742yncs2'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User_table.query.get(id)

#データベースの構造を変えたら
# flask db upgrade　コマンドをうってマイグレートする。
#userのdb
class User_table(UserMixin,db.Model):
    id= db.Column(db.Integer,primary_key =True)
    username = db.Column(db.String(60),index=True,unique=True)
    password = db.Column(db.String(20),index=True)
    def __repr__(self):
        return '<User %r>'%self.username

class Goods_table(db.Model):
    goods_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20))
    goods_name=db.Column(db.String(40))
    rental_fee=db.Column(db.Integer)
    description=db.Column(db.String(100))
    filepath1 = db.Column(db.String(100))
    filepath2 = db.Column(db.String(100))
    filepath3 = db.Column(db.String(100))
    goods_phase = db.Column(db.String(10)) # 商品がレンタル中かどうか．
    def __repr__(self):
        return '<User %r>'%self.username

class Deal_table(db.Model):
    deal_id = db.Column(db.Integer,primary_key=True)
    lender_id = db.Column(db.Integer,primary_key=False)
    borrower_id = db.Column(db.Integer,primary_key=False)
    price = db.Column(db.Integer,primary_key=False)
    phase = db.Column(db.String(10))
    # def __repr__(self):
        # return '<User %r>'%self.username

class Chat_table(db.Model):
    chat_id = db.Column(db.Integer,primary_key=True)
    deal_id = db.Column(db.Integer,primary_key=False)
    speaker = db.Column(db.Integer,primary_key=False)
    chat_contents = db.Column(db.String(100))
    # def __repr__(self):
        # return '<User %r>'%self.username


@app.route('/',methods=["POST"])
def index():
    return render_template('home_page.html')

@app.route("/sign_up",methods=["GET"])
def sign_up():
    return render_template('sign_up.html')

@app.route("/register",methods=["POST"])
def register():
    if request.form['username'] and request.form['password']:
        username = request.form['username']
        password = request.form['password']
        new_user = User_table(username=username,password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user,True) # ユーザが新規登録されたときは，ログイン状態にする．
        return redirect('/top_page')
    else:
        return render_template("error.html")

@app.route("/sign_in")
def sign_in():
    return render_template('sign_in.html')

@app.route("/login",methods=["POST"])
def login():
    if request.form["username"] and request.form["password"]:
        posted_username = request.form["username"]
        user_in_database = User_table.query.filter_by(username=posted_username).first()
        if request.form["password"] == user_in_database.password: # 入力されたpasswordが正しい場合
            login_user(user_in_database,True)
            return redirect('/top_page')
        else:
            return render_template('error.html')
    else:
        return render_template("error.html")

@app.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return render_template("top_page.html")


@app.route("/top_page",methods=["POST","GET"])
def top_page():
    goods = Goods_table.query.all()
    return render_template("top_page.html",goods=goods)

@app.route("/post_goods")
def post_goods():
    return render_template("post_goods.html")

@app.route("/chat")
def chat():

    return render_template("chat.html")

@app.route("/complete_post_goods",methods=["POST"])
def complete_post_goods():
    if request.form['goods_name'] and request.form['rental_fee'] and request.form['description'] and request.files['image1']:
        goods_name = request.form['goods_name']
        rental_fee = request.form['rental_fee']
        description = request.form['description']
        f = request.files['image1']
        filepath1 = 'static/' + f.filename
        f.save(filepath1)
        if request.files['image2']:
            f = request.files['image2']
            filepath2 = 'static/' + f.filename
            f.save(filepath2)
            if request.files['image3']:
                f = request.files['image3']
                filepath3 = 'static/' + f.filename
                f.save(filepath3)
            else:
                filepath3=""
        else:
            filepath2=""
            filepath3=""
        new_goods = Goods_table(goods_name=goods_name,rental_fee=rental_fee,description=description,
                                filepath1=filepath1,filepath2=filepath2,filepath3=filepath3)
        db.session.add(new_goods)
        db.session.commit()
        return render_template("complete_post_goods.html",goods_name=goods_name,rental_fee=rental_fee,description=description,
                                filepath1=filepath1,filepath2=filepath2,filepath3=filepath3)
    else:
        return render_template("error.html")

@app.route('/search_result',methods=["POST"])
def search_result():
    if request.form['search_name']:
        search_name=request.form['search_name']
        goods = Goods_table.query.filter(Goods_table.goods_name==search_name)
        return render_template("search_result.html",goods=goods)
    else:
        return render_template("error.html")

@app.route("/goods_detail/<goods_id>")
def goods_detail(goods_id):
    good = Goods_table.query.filter(Goods_table.goods_id==goods_id)
    return render_template("goods_detail.html",good=good)

@app.route("/rental_done", methods=["POST"])
def rental_done():
    goods_id = request.form['goods_id']
    return render_template("rental_done.html")

#テーブルの初期化のコマンド、これをしないとSQLAlchemyがdbにアクセスできない。
@app.cli.command('initdb')
def initdb_command():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
