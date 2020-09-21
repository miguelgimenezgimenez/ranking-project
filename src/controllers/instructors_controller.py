import numpy as np
from src.app import app
from flask import request


@app.route('/')
def welcome():
    return {
        "status": "OK",
        "message": "Welcome to miapi"
    }


randomInst = lambda: np.random.choice(["Amanda", "Felipe", "Marc"])


@app.route('/getrandom')
def randomTa():
    return {
        "instructor": randomInst()
    }


# http://localhost:3000/saludo?color=rojo&idioma=en
@app.route("/saludo")
def saludaInstructor():
    print("LOS ARGS")
    print(request.args)
    lang = request.args.get("idioma","es")
    color = request.args.get("color","blue")
    if lang == "es":
        saludo = f"Hola {randomInst()} tu color favorito es el {color}"
    elif lang == "en":
        saludo = f"Hello {randomInst()} your favorite color is {color}"
    else:
        saludo = "Unsupported language"

    return {
        "saludo": saludo,
        "query_params":request.args
    }
