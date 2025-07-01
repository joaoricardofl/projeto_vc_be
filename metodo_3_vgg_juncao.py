from PIL import Image
from numpy import expand_dims
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.models import load_model
import base64
import io
import itertools
from flask import jsonify
import subprocess

TAMANHO_IMAGEM = 224

def reconstrucao_3(request):
    
    # Carrega o modelo
    best_model_file = "vgg19_treinada_juncao.h5"
    model = load_model(best_model_file)
    print(model.summary())

    # Recebe colunas e linhas da imagem
    linhas = request.json.get('linhas')
    colunas = request.json.get('colunas')
    
    # Recebe a imagem do frontend
    pedacos = []
    imagens_request = request.json.get('pedacos')
    for imagem in imagens_request:
        imagem_bytes = base64.b64decode(imagem.split(',')[1])
        imagem = Image.open(io.BytesIO(imagem_bytes))
        pedacos.append(imagem)
        
    # Iteração por cada pedaço tendo ele como base
    resultado = {}
    indice_pedaco_base = 0
    for pedaco_base in pedacos:
        largura = pedaco_base.width
        altura = pedaco_base.height
        resultado_pedaco_base = {
            'above':{},
            'left': {},
        }        
        
        # Iteração por cada um dos outros pedaços para comparação
        indice_pedaco_comparado = 0
        for pedaco_comparado in pedacos:
            if(pedaco_base != pedaco_comparado):
                largura_comparado = pedaco_comparado.width
                altura_comparado = pedaco_comparado.height                
                
                # Imagem a Esquerda
                
                img = combinar_img_a_direita(pedaco_comparado, largura_comparado, altura_comparado, pedaco_base, largura, altura)
                img = preparar_imagem(img)
                descritores = model.predict(img, verbose=1)
                diferenca_descritores = float(descritores[0][0]-descritores[0][1])
                resultado_pedaco_base['left'][str(indice_pedaco_comparado)] = diferenca_descritores

                # Imagem acima

                img = combinar_img_abaixo(pedaco_comparado, largura_comparado, altura_comparado, pedaco_base, largura, altura)
                img = preparar_imagem(img)
                descritores = model.predict(img, verbose=1)
                diferenca_descritores = float(descritores[0][0]-descritores[0][1])
                resultado_pedaco_base['above'][str(indice_pedaco_comparado)] = diferenca_descritores
        
            indice_pedaco_comparado += 1
        resultado[str(indice_pedaco_base)] = resultado_pedaco_base
        indice_pedaco_base += 1
        
    # Calcula o resultado para cada arranjo possível
    lista_pedacos = []
    for pedaco in range(len(pedacos)):
        lista_pedacos.append(str(pedaco))
    
    arranjos_possiveis = list(itertools.permutations(lista_pedacos))
    
    maior_somatorio = 0
    
    resultado_arranjos = []
    for arranjo in arranjos_possiveis:
        linha = 1
        coluna = 1
        somatorio_arranjo = 0
        for elemento in arranjo:
            if(linha > 1):
                indice_peca_acima = colunas * (linha - 2) + coluna - 1
                valor_juncao_acima = resultado[elemento]["above"][arranjo[indice_peca_acima]]
                somatorio_arranjo += valor_juncao_acima
            if(coluna > 1):
                indice_peca_esquerda = colunas * (linha - 1) + coluna - 2
                valor_juncao_esquerda = resultado[elemento]["left"][arranjo[indice_peca_esquerda]]
                somatorio_arranjo += valor_juncao_esquerda
            if(coluna < colunas):
                coluna += 1
            else:
                coluna = 1
                linha += 1
        if(maior_somatorio < somatorio_arranjo):
            maior_somatorio = somatorio_arranjo
            arranjo_encontrado = arranjo
            
        resultado_arranjo = {"arranjo": arranjo, "somatorio_arranjo": somatorio_arranjo}
        resultado_arranjos.append(resultado_arranjo)
            
    return jsonify({"resultado_junções": resultado, "arranjo_encontrado": arranjo_encontrado, "resultado_arranjos": resultado_arranjos})
        
def preparar_imagem(img):
    img_resultante = img.resize((TAMANHO_IMAGEM, TAMANHO_IMAGEM), Image.LANCZOS)
    img_resultante = img_to_array(img_resultante)
    img_resultante = expand_dims(img_resultante, axis=0)
    img_resultante = img_resultante / 255
    return img_resultante


def combinar_img_a_direita(img1: Image, largura_1, altura_1, img2: Image, largura_2, altura_2):            
    largura = largura_1 + largura_2
    altura = max(altura_1, altura_2)
    imagem_resultante = Image.new("RGB", (largura, altura))
    imagem_resultante.paste(img1, (0, 0))
    imagem_resultante.paste(img2, (largura_1, 0)) 
    
    return imagem_resultante

def combinar_img_abaixo(img1: Image, largura_1, altura_1, img2: Image, largura_2, altura_2):            
    altura = altura_1 + altura_2
    largura = max(largura_1, largura_2)
    imagem_resultante = Image.new("RGB", (largura, altura))
    imagem_resultante.paste(img1, (0, 0))
    imagem_resultante.paste(img2, (0, altura_1)) 
    imagem_resultante = imagem_resultante.rotate(90, expand=True)
    
    return imagem_resultante