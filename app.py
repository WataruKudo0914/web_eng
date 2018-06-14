from flask import Flask, render_template,request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home_page.html')

@app.route("/sign_up",methods=["GET"])
def sign_up():
    return render_template('sign_up.html')

@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html")

@app.route("/top_page",methods=["POST"])
def login_success():
    if request.form['username'] and request.form['password']:
        username = request.form['username']
        return render_template("top_page.html",username=username)
    else:
        return render_template("error.html")

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
        return render_template("complete_post_goods.html",goods_name=goods_name,rental_fee=rental_fee,description=description)
    else:
        return render_template("error.html")



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
