from flask import Flask , render_template , request , redirect , url_for
from markupsafe import escape

app = Flask(__name__)


@app.route("/",methods=["GET","POST"])
def index():
    if request.method == 'POST':
        
        return render_template("result.html",data = request.form)
         
    return render_template("index.html",name = "mohammad")


if __name__ == '__main__':
    app.run(debug = True)