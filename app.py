from flask import Flask, render_template,request, make_response ,session ,redirect, url_for
from werkzeug.utils import secure_filename
#posgresqlへアクセスするモジュール
import psycopg2
import psycopg2.extras
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, UserMixin,logout_user

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
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
    email = db.Column(db.String(60),index=True,unique=True)
    faculty = db.Column(db.String(60),index=True) # 学部
    major = db.Column(db.String(60),index=True) # 学科
    grade = db.Column(db.Integer) # 学年
    self_introduction = db.Column(db.String(140),index=True)
    password = db.Column(db.String(20),index=True)
    def __repr__(self):
        return '<User %r>'%self.username

class Goods_table(db.Model):
    goods_id = db.Column(db.Integer,primary_key=True)
    id = db.Column(db.Integer,primary_key=False)
    username = db.Column(db.String(60))
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
    goods_id = db.Column(db.Integer,primary_key=False)
    lender_id = db.Column(db.Integer,primary_key=False)
    borrower_id = db.Column(db.Integer,primary_key=False)
    price = db.Column(db.Integer,primary_key=False)
    lender_check = db.Column(db.String(60)) # "交渉中","レンタル中"．，"返却済み"．貸す人によるチェック．
    borrower_check = db.Column(db.String(60)) # "交渉中","レンタル中"．，"返却済み"．借りる人によるチェック．
    # def __repr__(self):
        # return '<User %r>'%self.username

class Chat_table(db.Model):
    chat_id = db.Column(db.Integer,primary_key=True)
    deal_id = db.Column(db.Integer,primary_key=False)
    speaker = db.Column(db.Integer,primary_key=False)
    chat_contents = db.Column(db.String(100))
    # def __repr__(self):
        # return '<User %r>'%self.username


@app.route('/',methods=["POST","GET"])
def index():
    return render_template('home_page.html')

@app.route("/sign_up",methods=["GET"])
def sign_up():
    return render_template('sign_up.html')

@app.route("/register",methods=["POST"])
def register():
    if request.form['username'] and request.form['password']:
        username = request.form['username']
        email = request.form["email"]
        password = request.form['password']
        faculty = request.form["faculty"]
        major = request.form["major"]
        grade = request.form["grade"]
        self_introduction = request.form["self_introduction"]
        new_user = User_table(username=username,email=email,password=password,
        faculty=faculty,major=major,grade=grade,self_introduction=self_introduction)
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
    goods = Goods_table.query.all()
    return render_template("top_page.html",goods=goods)


@app.route("/top_page",methods=["POST","GET"])
def top_page():
    goods = Goods_table.query.all()
    return render_template("top_page.html",goods=goods)

@app.route("/post_goods")
def post_goods():
    return render_template("post_goods.html")

@app.route("/chat/<int:id>")
def chat(id):
    lend_deal = Deal_table.query.filter(Deal_table.lender_id==id).all()
    # [Deal_table1,Deal_table2]のようにリスト型で帰って来る
    borrow_deal = Deal_table.query.filter(Deal_table.borrower_id==id).all()
    # for deal_num in range(len(lend_deal)):
        # goods_id=lend_deal[deal_num].goods_id
    user = User_table
    goods = Goods_table
    return render_template("chat.html",lend_deal=lend_deal,borrow_deal=borrow_deal,user=user,goods=goods)

@app.route("/chat/detail/<int:deal_id>")
def chat_detail(deal_id):
    deal = Deal_table.query.filter(Deal_table.deal_id==deal_id).first()
    lender_name = User_table.query.filter(User_table.id==deal.lender_id).first().username
    borrower_name = User_table.query.filter(User_table.id==deal.borrower_id).first().username
    chat=Chat_table.query.filter(Chat_table.deal_id==deal_id).all()
    chat_list=[]
    for num in range(len(chat)):
        chat_dic={}
        chat_dic["speaker"]=User_table.query.filter(User_table.id==chat[num].speaker).first().username
        chat_dic["chat_contents"]=chat[num].chat_contents
        chat_list.append(chat_dic)
    # return redirect("/chat/detail/{}".format(deal_id))
    return render_template("chat_detail.html",chat_list=chat_list,deal=deal,
        lender_name=lender_name,borrower_name=borrower_name)

@app.route("/chat_update",methods=["POST"])
def chat_result():
    deal_id = request.form["deal_id"]
    chat_contents=request.form["one_chat"]
    speaker = request.form["speaker"]
    new_chat = Chat_table(deal_id=deal_id,speaker=speaker,chat_contents=chat_contents)
    db.session.add(new_chat)
    db.session.commit()
    return redirect("/chat/detail/{}".format(deal_id))


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
            filepath2 = 'static/'+ f.filename
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
        username = request.form['username']
        id = request.form['id']
        new_goods = Goods_table(id=id,goods_name=goods_name,rental_fee=rental_fee,description=description,
                                filepath1=filepath1,filepath2=filepath2,filepath3=filepath3,username=username)
        db.session.add(new_goods)
        db.session.commit()
        return render_template("complete_post_goods.html",goods_name=goods_name,rental_fee=rental_fee,description=description,
                                filepath1=filepath1,filepath2=filepath2,filepath3=filepath3,username=username)
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

@app.route("/goods_detail/<int:goods_id>")
def goods_detail(goods_id):
    good = Goods_table.query.filter(Goods_table.goods_id==goods_id)
    return render_template("goods_detail.html",good=good)

@app.route("/rental_done", methods=["POST"])
def rental_done():
    goods_id = request.form['goods_id']
    lender_id = request.form["lender_id"]
    borrower_id = request.form["borrower_id"]
    price = request.form["price"]
    lender_check = "交渉中" # 初期値はFalse
    borrower_check = "交渉中"
    new_deal = Deal_table(goods_id=goods_id,lender_id=lender_id,borrower_id=borrower_id,
    price=price,lender_check=lender_check,borrower_check=borrower_check)
    db.session.add(new_deal)
    db.session.commit()
    return render_template("rental_done.html",new_deal=new_deal)

@app.route("/mypage",methods=["POST"])
def mypage():
    id = request.form["id"]
    user_information = User_table.query.filter(User_table.id==id).first()
    posted_goods = Goods_table.query.filter(Goods_table.id==id).all()
    rental_goods_id = Deal_table.query.filter(Deal_table.borrower_id==id).all()
    if len(rental_goods_id) != 0:
        for i in rental_goods_id:
            rental_goods = Goods_table.query.filter(Goods_table.goods_id == i.goods_id).all()
    else:
        rental_goods = []

    lend_goods_id = Deal_table.query.filter(Deal_table.lender_id==id).all()
    if len(lend_goods_id) != 0:
        for i in lend_goods_id:
            lend_goods = Goods_table.query.filter(Goods_table.goods_id == i.goods_id).all()
    else:
        lend_goods = []
    return render_template("mypage.html",user_information=user_information,posted_goods=posted_goods,rental_goods=rental_goods,lend_goods=lend_goods,Deal_table=Deal_table)

@app.route("/update_phase",methods=["POST"])
def update_phase():
    submitter_id = int(request.form["submitter_id"]) # formからstrで入ってくる
    deal_id = request.form["deal_id"]
    selected_phase = request.form["phase"] # "交渉中" or "レンタル中" or "返却済み"
    new_deal = Deal_table.query.filter(Deal_table.deal_id==deal_id).first()
    if submitter_id == new_deal.lender_id: # 状態変更を申し出たのがlenderだったら
        new_deal.lender_check = selected_phase
    elif submitter_id == new_deal.borrower_id:
        new_deal.borrower_check = selected_phase
    else:
        return render_template("error.html")
    db.session.add(new_deal)
    db.session.commit()
    return redirect("/chat/detail/{}".format(deal_id))



#テーブルの初期化のコマンド、これをしないとSQLAlchemyがdbにアクセスできない。
@app.cli.command('initdb')
def initdb_command():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
