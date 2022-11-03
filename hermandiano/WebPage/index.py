from flask import Flask, request, render_template, redirect, session
from discord.ext import commands
from hermandiano import bot

app = Flask(__name__)

@app.route('/', methods = ["GET"])
def index():
  return render_template('inicio.html')

@app.route('/login', methods = ["GET"])
def login():
  return "Hola"

if __name__ == '__main__':
  app.run(debug=True)
else:
  app.run()