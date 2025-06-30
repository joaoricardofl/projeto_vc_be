import itertools
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import img_to_array
import base64
import io
from numpy import expand_dims
from flask import jsonify

TAMANHO_IMAGEM = 224

def reconstrucao_4(request):
    
    # Carrega o modelo
    best_model_file = "vgg19_treinada_arranjo.h5"
    model = load_model(best_model_file)
    print(model.summary())

    # Recebe colunas e linhas da imagem
    linhas = request.json.get('linhas')
    colunas = request.json.get('colunas')
    
    # Recebe a imagem do frontend
    pedacos = []
    resultado = []
    imagens_request = request.json.get('pedacos')
    for imagem in imagens_request:
        imagem_bytes = base64.b64decode(imagem.split(',')[1])
        imagem = Image.open(io.BytesIO(imagem_bytes))
        pedacos.append(imagem)
        
    arranjos_possiveis = list(itertools.permutations(range(linhas * colunas)))
    
    index_arranjo = 0
    maior_descritor_certo = 0
    arranjo_encontrado = []
    
    for arranjo in arranjos_possiveis:
        
        resultado_arranjo = {}
        
        linha = 0
        coluna = 0
        larguras = []
        alturas = []
        for pedaco in arranjo:
            altura_pedaco = pedacos[pedaco].height
            largura_pedaco = pedacos[pedaco].width
            
            if(coluna == 0):
                larguras.append(largura_pedaco)
            else:
                larguras[linha] += largura_pedaco
                
            if(linha == 0):
                alturas.append(altura_pedaco)
            else:
                alturas[coluna] += altura_pedaco
                
            if(coluna < colunas - 1):
                coluna += 1
            else:
                coluna = 0
                linha += 1
                
        largura = max(larguras)
        altura = max(alturas)
        imagem_resultante = Image.new("RGB", (largura, altura))
        
        linha = 0
        coluna = 0
        posicao_horizontal = 0
        posicao_vertical = 0
        alturas = []
        for pedaco in arranjo:
            
            if(linha != 0):
                posicao_vertical = alturas[coluna]
            
            imagem_resultante.paste(pedacos[pedaco], (posicao_horizontal, posicao_vertical))
            altura_pedaco = pedacos[pedaco].height
            largura_pedaco = pedacos[pedaco].width
            
            if(linha == 0):
                alturas.append(altura_pedaco)
            else:
                alturas[coluna] += altura_pedaco
                
            if(coluna < colunas - 1):
                posicao_horizontal += largura_pedaco
                coluna += 1
            else:
                posicao_horizontal = 0 
                coluna = 0
                linha += 1
        
        img = preparar_imagem(imagem_resultante)
        descritores = model.predict(img, verbose=1)
        
        resultado_arranjo["arranjo"] = arranjo
        resultado_arranjo["descritor_certo"] = float(descritores[0][0])
        resultado_arranjo["descritor_errado"] = float(descritores[0][1])
        
        if(resultado_arranjo["descritor_certo"] > maior_descritor_certo ):
            maior_descritor_certo = resultado_arranjo["descritor_certo"]
            arranjo_encontrado = arranjo
        
        resultado.append(resultado_arranjo)
        index_arranjo+= 1
            
    return jsonify({"resultado_arranjos": resultado, "arranjo_encontrado": arranjo_encontrado})


def preparar_imagem(img):
    img_resultante = img.resize((TAMANHO_IMAGEM, TAMANHO_IMAGEM), Image.LANCZOS)
    img_resultante = img_to_array(img_resultante)
    img_resultante = expand_dims(img_resultante, axis=0)
    img_resultante = img_resultante / 255
    return img_resultante