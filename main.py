from flask_cors import CORS
from flask import Flask, jsonify, request
from dividir_imagem import dividir_imagem
from metodo_1_intensidade_pixel import reconstrucao_1
from metodo_2_bordas import reconstrucao_2
from metodo_3_vgg_juncao import reconstrucao_3
from metodo_4_vgg_arranjo import reconstrucao_4

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def hello():
    return jsonify({"response":"BE do projeto de VC 93dd"}) ### Alterar versão a cada deploy 1/1

@app.route('/processar_imagem', methods=['POST'])
def processar_imagem():
    return dividir_imagem(request)

@app.route('/1_intensidade_pixel', methods=['POST'])
def reconstrucao_metodo_1():
    return reconstrucao_1(request)

@app.route('/2_bordas', methods=['POST'])
def reconstrucao_metodo_2():
    return reconstrucao_2(request)

@app.route('/3_vgg_juncao', methods=['POST'])
def reconstrucao_metodo_3():
    return reconstrucao_3(request)

@app.route('/4_vgg_arranjo', methods=['POST'])
def reconstrucao_metodo_4():
    return reconstrucao_4(request)

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=5000)