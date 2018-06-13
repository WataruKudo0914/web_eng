from flask import Flask, render_template

print ("test2 routing")
app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html', message="こんにちは")



#@で始まる行:デコレータ (次の行で定義する関数に何らかの処理を行う)
# @app.route(URL):は、URLが次の行の関数のトリガーとなることをFlaskに教える
@app.route("/page1")
def page1():
    return render_template('page1.html')



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
