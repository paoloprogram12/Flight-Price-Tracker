from flask import Flask, render_template

# creates app
app = Flask(__name__)

# home page
@app.route('/')
def home():
    return render_template('index.html')

# runs the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)