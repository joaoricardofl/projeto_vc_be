import base64
from flask import jsonify
from PIL import Image
import io
import itertools

def reconstrucao_1(request):
    
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
    diferenca_maxima_juncoes = 0
    indice_pedaco_base = 0
    for pedaco_base in pedacos:
        largura = pedaco_base.width
        altura = pedaco_base.height
        resultado_pedaco_base = {
            'below':{},
            'above':{},
            'left': {},
            'right': {}
        }
        pedaco_base_carregado = pedaco_base.load()
        
        # Iteração por cada um dos outros pedaços para comparação
        indice_pedaco_comparado = 0
        for pedaco_comparado in pedacos:
            if(pedaco_base != pedaco_comparado):
                pedaco_comparado_carregado = pedaco_comparado.load()
                largura_comparado = pedaco_comparado.width
                altura_comparado = pedaco_comparado.height                
                if(largura_comparado < largura):
                    largura = largura_comparado
                if(altura_comparado < altura):
                    altura = altura_comparado

                diferencas = 0
                
                # Cálculo das diferenças das intensidades dos pixels
                
                # Peça a direita - (x_base = largura / x_comparado = 0)
                for y in range(altura):
                    r_base, g_base, b_base = pedaco_base_carregado[largura-1,y]
                    r_compare, g_compare, b_compare = pedaco_comparado_carregado[0,y]
                    diferencas = abs(r_base - r_compare) + abs(g_base + g_compare) + abs(b_base + b_compare) + diferencas
                
                resultado_pedaco_base['right'][str(indice_pedaco_comparado)] = diferencas
                if(diferencas > diferenca_maxima_juncoes):
                    diferenca_maxima_juncoes = diferencas
                    
                    
                # Peça a esquerda - (x_base = 0 / x_comparado = largura)
                diferencas = 0
                for y in range(altura):
                    r_base, g_base, b_base = pedaco_base_carregado[0,y]
                    r_compare, g_compare, b_compare = pedaco_comparado_carregado[largura-1,y]
                    diferencas = abs(r_base - r_compare) + abs(g_base + g_compare) + abs(b_base + b_compare) + diferencas
                
                resultado_pedaco_base['left'][str(indice_pedaco_comparado)] = diferencas
                if(diferencas > diferenca_maxima_juncoes):
                    diferenca_maxima_juncoes = diferencas
                    
                    
                # Peça acima - (y_base = 0 / y_comparado = altura)
                diferencas = 0
                for x in range(largura):
                    r_base, g_base, b_base = pedaco_base_carregado[x,0]
                    r_compare, g_compare, b_compare = pedaco_comparado_carregado[x,altura-1]
                    diferencas = abs(r_base - r_compare) + abs(g_base + g_compare) + abs(b_base + b_compare) + diferencas
                
                resultado_pedaco_base['above'][str(indice_pedaco_comparado)] = diferencas
                if(diferencas > diferenca_maxima_juncoes):
                    diferenca_maxima_juncoes = diferencas
                    
                    
                # Peça abaixo - (y_base = altura / y_comparado = 0)
                diferencas = 0
                for x in range(largura):
                    r_base, g_base, b_base = pedaco_base_carregado[x,altura-1]
                    r_compare, g_compare, b_compare = pedaco_comparado_carregado[x,0]
                    diferencas = abs(r_base - r_compare) + abs(g_base + g_compare) + abs(b_base + b_compare) + diferencas
                
                resultado_pedaco_base['below'][str(indice_pedaco_comparado)] = diferencas
                if(diferencas > diferenca_maxima_juncoes):
                    diferenca_maxima_juncoes = diferencas
                    
            indice_pedaco_comparado += 1
        resultado[str(indice_pedaco_base)] = resultado_pedaco_base
        indice_pedaco_base += 1
    
    
    # Normalização das diferenças
    for pedaco_base in resultado:
        for direcao in resultado[pedaco_base]:
            for pedaco_comparado in resultado[pedaco_base][direcao]:
                resultado[pedaco_base][direcao][pedaco_comparado] = resultado[pedaco_base][direcao][pedaco_comparado] / diferenca_maxima_juncoes
    
    # Calcula o resultado para cada arranjo possível
    lista_pedacos = []
    for pedaco in range(len(pedacos)):
        lista_pedacos.append(str(pedaco))
    
    arranjos_possiveis = list(itertools.permutations(lista_pedacos))
    
    diferença_minima_do_arranjo = colunas * linhas
    
    resultado_arranjos = []
    for arranjo in arranjos_possiveis:
        resultado_arranjo = {}
        linha = 1
        coluna = 1
        diferenca_arranjo = 0
        for elemento in arranjo:
            if(linha > 1):
                indice_peca_acima = colunas * (linha - 2) + coluna - 1
                valor_juncao_acima = resultado[elemento]["above"][arranjo[indice_peca_acima]]
                diferenca_arranjo += valor_juncao_acima
            if(coluna > 1):
                indice_peca_esquerda = colunas * (linha - 1) + coluna - 2
                valor_juncao_esquerda = resultado[elemento]["left"][arranjo[indice_peca_esquerda]]
                diferenca_arranjo += valor_juncao_esquerda
            if(coluna < colunas):
                coluna += 1
            else:
                coluna = 1
                linha += 1
        if(diferença_minima_do_arranjo > diferenca_arranjo):
            diferença_minima_do_arranjo = diferenca_arranjo
            arranjo_encontrado = arranjo
        resultado_arranjo = {"arranjo": arranjo, "diferenca": diferenca_arranjo}
        resultado_arranjos.append(resultado_arranjo)
                
    
    return jsonify({"resultado_junções": resultado, "arranjo_encontrado": arranjo_encontrado, "resultado_arranjos": resultado_arranjos})