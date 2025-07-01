import base64
from flask import jsonify
from PIL import Image
import io
import itertools
from numpy import array
from cv2 import GaussianBlur, Canny

def reconstrucao_2(request):
    
    # Recebe colunas e linhas da imagem
    linhas = request.json.get('linhas')
    colunas = request.json.get('colunas')
    
    # Recebe a imagem do frontend
    pedacos = []
    bordas = []
    imagens_request = request.json.get('pedacos')
    for imagem in imagens_request:
        imagem_bytes = base64.b64decode(imagem.split(',')[1])
        imagem = Image.open(io.BytesIO(imagem_bytes))
        pedacos.append(imagem)
        bordas.append(identificar_bordas(imagem))
        
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
        borda_base_carregada = bordas[indice_pedaco_base].load()
        
        # Iteração por cada um dos outros pedaços para comparação
        indice_pedaco_comparado = 0
        for pedaco_comparado in pedacos:
            if(pedaco_base != pedaco_comparado):
                borda_comparado_carregado = bordas[indice_pedaco_comparado].load()
                largura_comparado = pedaco_comparado.width
                altura_comparado = pedaco_comparado.height                
                if(largura_comparado < largura):
                    largura = largura_comparado
                if(altura_comparado < altura):
                    altura = altura_comparado
                    
                # Cálculo do indicador de bordas
                
                # Peça a direita - (x_base = largura / x_comparado = 0)
                indicador_bordas= 0
                maior_indicador = 0
                for y in range(altura):
                    g_base = borda_base_carregada[largura-1,y]
                    g_comparado = borda_comparado_carregado[0,y]
                    if(g_base == 255):
                        if(g_comparado == 255):
                            indicador_bordas +=1
                        elif (y-1>=0):
                            r_compare_up = borda_comparado_carregado[0,y-1]
                            if(r_compare_up == 255):
                                indicador_bordas +=1
                        elif(y+1<altura):
                            r_compare_bottom = borda_comparado_carregado[0,y+1]
                            if(r_compare_bottom == 255):
                                indicador_bordas +=1
                
                resultado_pedaco_base['right'][str(indice_pedaco_comparado)] = indicador_bordas
                if (indicador_bordas > maior_indicador):
                    maior_indicador = indicador_bordas
                        
                # Peça a esquerda - (x_base = 0 / x_comparado = largura)
                indicador_bordas = 0
                for y in range(altura):
                    g_base = borda_base_carregada[0,y]
                    g_comparado = borda_comparado_carregado[largura-1,y]
                    if(g_base == 255):
                        if(g_comparado == 255):
                            indicador_bordas +=1
                        elif (y-1>=0):
                            r_compare_up = borda_comparado_carregado[largura-1,y-1]
                            if(r_compare_up == 255):
                                indicador_bordas +=1
                        elif(y+1<altura):
                            r_compare_bottom = borda_comparado_carregado[largura-1,y+1]
                            if(r_compare_bottom == 255):
                                indicador_bordas +=1
                
                resultado_pedaco_base['left'][str(indice_pedaco_comparado)] = indicador_bordas
                if (indicador_bordas > maior_indicador):
                    maior_indicador = indicador_bordas
                        
                # Peça acima - (y_base = 0 / y_comparado = altura)
                indicador_bordas = 0
                for x in range(largura):
                    g_base = borda_base_carregada[x,0]
                    g_comparado = borda_comparado_carregado[x,altura - 1]
                    if(g_base == 255):
                        if(g_comparado == 255):
                            indicador_bordas +=1
                        elif (x-1>=0):
                            r_compare_up = borda_comparado_carregado[x-1,altura - 1]
                            if(r_compare_up == 255):
                                indicador_bordas +=1
                        elif(x+1<altura):
                            r_compare_bottom = borda_comparado_carregado[x-1,altura - 1]
                            if(r_compare_bottom == 255):
                                indicador_bordas +=1
                
                resultado_pedaco_base['above'][str(indice_pedaco_comparado)] = indicador_bordas
                if (indicador_bordas > maior_indicador):
                    maior_indicador = indicador_bordas
                        
                # below piece (x_base = width and x_compared = 0)
                indicador_bordas = 0
                for x in range(largura):
                    g_base = borda_base_carregada[x,altura - 1]
                    g_comparado = borda_comparado_carregado[x,0]
                    if(g_base == 255):
                        if(g_comparado == 255):
                            indicador_bordas +=1
                        elif (x-1>0):
                            r_compare_up = borda_comparado_carregado[x-1,0]
                            if(r_compare_up == 255):
                                indicador_bordas +=1
                        elif(x+1<altura):
                            r_compare_bottom = borda_comparado_carregado[x+1,0]
                            if(r_compare_bottom == 255):
                                indicador_bordas +=1
                
                resultado_pedaco_base['below'][str(indice_pedaco_comparado)] = indicador_bordas
                if (indicador_bordas > maior_indicador):
                    maior_indicador = indicador_bordas
        
            indice_pedaco_comparado += 1
        resultado[str(indice_pedaco_base)] = resultado_pedaco_base
        indice_pedaco_base += 1

        
    # Calcula o resultado para cada arranjo possível
    lista_pedacos = []
    for pedaco in range(len(pedacos)):
        lista_pedacos.append(str(pedaco))
    
    arranjos_possiveis = list(itertools.permutations(lista_pedacos))
    
    indicador_maximo = 0
        
    arranjo_encontrado = []
    resultado_arranjos = []
    
    for arranjo in arranjos_possiveis:
        linha = 1
        coluna = 1
        somatorio_indicador_arranjo = 0

        for elemento in arranjo:
            if(linha > 1):
                indice_peca_acima = colunas * (linha - 2) + coluna - 1
                valor_juncao_acima = resultado[elemento]["above"][arranjo[indice_peca_acima]]
                somatorio_indicador_arranjo += valor_juncao_acima
            if(coluna > 1):
                indice_peca_esquerda = colunas * (linha - 1) + coluna - 2
                valor_juncao_esquerda = resultado[elemento]["left"][arranjo[indice_peca_esquerda]]
                somatorio_indicador_arranjo += valor_juncao_esquerda
            if(coluna < colunas):
                coluna += 1
            else:
                coluna = 1
                linha += 1
        if(indicador_maximo < somatorio_indicador_arranjo):
            indicador_maximo = somatorio_indicador_arranjo
            arranjo_encontrado = arranjo
        resultado_arranjo = {"arranjo": arranjo, "indicador": somatorio_indicador_arranjo}
        resultado_arranjos.append(resultado_arranjo)
                
    # Converte as peças para base64
    bordas_processadas = []
    for borda in bordas:
        buffered = io.BytesIO()
        borda.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        bordas_processadas.append(f"data:image/png;base64,{img_str}")
    
    return jsonify({"resultado_junções": resultado, "arranjo_encontrado": arranjo_encontrado, "bordas": bordas_processadas, "resultado_arranjos": resultado_arranjos })
        
def identificar_bordas(pedaco: Image.Image):
    
    img_array = array(pedaco.convert('L'))
    # Aplica blur Gaussiano para reduzir ruído
    blurred = GaussianBlur(img_array, (5, 5), 0)
    
    # Detecta bordas com Canny
    edges = Canny(blurred, 50, 150)
    
    # Converte de volta para PIL.Image
    return Image.fromarray(edges)