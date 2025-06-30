import io
import base64
import random
from PIL import Image
from flask import Flask, jsonify
import itertools

def dividir_imagem(request):
    
    # Recebe a imagem do frontend
    imagem_data = request.json.get('imagem')
    imagem_bytes = base64.b64decode(imagem_data.split(',')[1])
    imagem = Image.open(io.BytesIO(imagem_bytes))
    
    # Recebe colunas e linhas da imagem
    linhas = request.json.get('linhas')
    colunas = request.json.get('colunas')
    
    # Divide a imagem em (colunas x linhas) partes iguais
    width, height = imagem.size
    size_width = width // colunas
    size_height = height // linhas
    
    pedacos = []
    inicial_vertical = 0
    for linha in range(linhas):
        inicial_horizontal = 0
        final_vertical = inicial_vertical + size_height
        for coluna in range(colunas):
            final_horizontal = inicial_horizontal + size_width
            pedacos.append(imagem.crop((inicial_horizontal, inicial_vertical, final_horizontal, final_vertical)))
            inicial_horizontal = final_horizontal
        inicial_vertical = final_vertical
    
    # Embaralha as peças
    random.shuffle(pedacos)
    
    # Converte as peças para base64
    pedacos_processados = []
    for pedacos in pedacos:
        buffered = io.BytesIO()
        pedacos.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        pedacos_processados.append(f"data:image/png;base64,{img_str}")
    
    return jsonify({"pedacos": pedacos_processados})