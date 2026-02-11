import webbrowser
import os
import datetime
import re
import sys
import pdfkit
from ferramentas import formatar_moeda
import calendar

# =================================================================
# 🛠️ MOTOR E CONVERSOR (NÃO MEXER)
# =================================================================

def obter_caminho_motor():
    if getattr(sys, 'frozen', False):
        caminho_base = sys._MEIPASS
    else:
        caminho_base = os.path.abspath(".")
    return os.path.join(caminho_base, "wkhtmltopdf.exe")

def converter_e_limpar(caminho_html, caminho_pdf):
    try:
        motor = obter_caminho_motor()
        config = pdfkit.configuration(wkhtmltopdf=motor)
        opcoes = {
            'encoding': "UTF-8",
            'quiet': '',
            'enable-local-file-access': None,
            'margin-top': '10mm', 'margin-bottom': '10mm',
            'margin-left': '10mm', 'margin-right': '10mm'
        }
        pdfkit.from_file(caminho_html, caminho_pdf, configuration=config, options=opcoes)
        
        if os.path.exists(caminho_html):
            os.remove(caminho_html)
            
        os.startfile(os.path.abspath(caminho_pdf))
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        webbrowser.open(f"file://{os.path.realpath(caminho_html)}")

# =================================================================
# 📑 1. HOLERITE / RECIBO DE FOLHA
# =================================================================

import webbrowser
import os
import datetime
import re
import sys
import pdfkit
from ferramentas import formatar_moeda

def obter_caminho_motor():
    if getattr(sys, 'frozen', False):
        caminho_base = sys._MEIPASS
    else:
        caminho_base = os.path.abspath(".")
    return os.path.join(caminho_base, "wkhtmltopdf.exe")

def converter_e_limpar(caminho_html, caminho_pdf):
    try:
        motor = obter_caminho_motor()
        config = pdfkit.configuration(wkhtmltopdf=motor)
        opcoes = {
            'encoding': "UTF-8",
            'quiet': '',
            'enable-local-file-access': None,
            'margin-top': '5mm', 'margin-bottom': '5mm',
            'margin-left': '5mm', 'margin-right': '5mm'
        }
        pdfkit.from_file(caminho_html, caminho_pdf, configuration=config, options=opcoes)
        if os.path.exists(caminho_html):
            os.remove(caminho_html)
        os.startfile(os.path.abspath(caminho_pdf))
    except Exception as e:
        print(f"Erro: {e}")
        webbrowser.open(f"file://{os.path.realpath(caminho_html)}")

def gerar_recibo_folha(nome_func, dados_cabecalho, tabela_itens, totais):
    pasta = os.path.join("Documentos_DP", "Holerites")
    if not os.path.exists(pasta): os.makedirs(pasta)
    
    nome_f = re.sub(r'[\\/*?:"<>|]', "", nome_func).strip().replace(" ", "_")
    data_s = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    c_html = os.path.join(pasta, f"TEMP_{nome_f}.html")
    c_pdf = os.path.join(pasta, f"Recibo_Pagamento_{nome_f}_{data_s}.pdf")

    total_v, total_d = 0.0, 0.0
    linhas_tabela = ""
    for desc, ref, v, d in tabela_itens:
        total_v += v
        total_d += d
        v_cor = f"<span style='color: #2e7d32; font-weight: bold;'>{formatar_moeda(v)}</span>" if v > 0 else ""
        d_cor = f"<span style='color: #d32f2f; font-weight: bold;'>{formatar_moeda(d)}</span>" if d > 0 else ""
        linhas_tabela += f"<tr><td>{desc}</td><td style='text-align:center;'>{ref}</td><td class='text-right'>{v_cor}</td><td class='text-right'>{d_cor}</td></tr>"

    liquido = total_v - total_d

    estilo_css = """
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 10px; background: #fff; }
        .via { 
            border: 2px solid #000; 
            padding: 15px; 
            margin-bottom: 10px; 
            width: 100%; 
            box-sizing: border-box;
            page-break-inside: avoid; /* NÃO deixa quebrar a via no meio */
        }
        .header { width: 100%; border-bottom: 2px solid #000; margin-bottom: 10px; }
        .header td { border: none !important; padding: 2px !important; }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #000; padding: 6px; text-align: left; font-size: 13px; }
        th { background: #f2f2f2; }
        .text-right { text-align: right; }
        
        .footer-liquido { display: flex; justify-content: flex-end; margin-top: 10px; }
        .box-liquido { 
            border: 2px solid #002f6c; 
            background: #f0f4f8; 
            text-align: center; 
            padding: 8px 25px; 
            color: #002f6c;
            min-width: 200px;
        }
        
        .assinatura-area { margin-top: 40px; text-align: center; }
        .linha { border-top: 2px solid #000; width: 80%; margin: 0 auto; padding-top: 2px; font-weight: bold; }
        .nome-trabalhador { font-size: 14px; text-transform: uppercase; margin-top: 5px; }
        .linha-corte { border-top: 1px dashed #000; text-align: center; margin: 15px 0; font-size: 10px; color: #555; }
    </style>
    """

    def criar_via(label):
        return f"""
        <div class="via">
            <div style="text-align: right; font-size: 10px; color: #999; font-weight: bold;">{label}</div>
            <table class="header">
                <tr>
                    <td><b style="font-size: 20px;">RECIBO DE PAGAMENTO</b></td>
                    <td class="text-right" style="font-size: 16px;">Competência: <b>{dados_cabecalho.get('Competência', '-')}</b></td>
                </tr>
                <tr>
                    <td colspan="2" style="padding-top: 10px; font-size: 15px;"><b>Trabalhador:</b> {nome_func}</td>
                </tr>
            </table>

            <table>
                <thead>
                    <tr>
                        <th width="55%">DESCRIÇÃO</th>
                        <th width="10%" style="text-align:center;">REF.</th>
                        <th class="text-right">VENCIMENTOS</th>
                        <th class="text-right">DESCONTOS</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_tabela}
                    <tr style="background: #eee; font-weight: bold;">
                        <td colspan="2" class="text-right">TOTAIS</td>
                        <td class="text-right" style="color: #2e7d32;">{formatar_moeda(total_v)}</td>
                        <td class="text-right" style="color: #d32f2f;">{formatar_moeda(total_d)}</td>
                    </tr>
                </tbody>
            </table>

            <div class="footer-liquido">
                <div class="box-liquido">
                    <span style="font-size: 12px; font-weight: bold;">LÍQUIDO A RECEBER</span><br>
                    <span style="font-size: 22px; font-weight: bold;">{formatar_moeda(liquido)}</span>
                </div>
            </div>

            <div class="assinatura-area">
                <div style="margin-bottom: 30px;">Data: ____/____/2026</div>
                <div class="linha">Assinatura do Funcionário</div>
                <div class="nome-trabalhador">{nome_func}</div>
            </div>
        </div>
        """

    html_final = f"""
    <html>
    <head>{estilo_css}</head>
    <body>
        {criar_via("VIA DO EMPREGADOR")}
        <div class="linha-corte">------------------ CORTE AQUI ------------------</div>
        {criar_via("VIA DO TRABALHADOR")}
    </body>
    </html>
    """

    with open(c_html, "w", encoding="utf-8") as f:
        f.write(html_final)
    
    converter_e_limpar(c_html, c_pdf)

# Apelido para não quebrar a Aba de Folha se ela chamar o nome antigo
def gerar_recibo_html(titulo_doc, tipo_arquivo, nome_funcionario, dados_cabecalho, tabela_itens, totais):
    gerar_recibo_folha(nome_funcionario, dados_cabecalho, tabela_itens, totais)

# =================================================================
# 📑 2. RESCISÃO (TRCT)
# =================================================================

def gerar_trct_html(dados_func, verbas, totais_res):
    pasta = os.path.join("Documentos_DP", "Rescisoes")
    if not os.path.exists(pasta): os.makedirs(pasta)
    
    nome_f = re.sub(r'[\\/*?:"<>|]', "", dados_func["nome"]).strip().replace(" ", "_")
    c_html = os.path.join(pasta, f"TEMP_TRCT_{nome_f}.html")
    c_pdf = os.path.join(pasta, f"TRCT_{nome_f}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf")

    # Verbas com cores: Verde (Ganhos) e Vermelho (Descontos)
    linhas_verbas = ""
    for desc, v, d in verbas:
        v_cor = f"<span style='color: #2e7d32; font-weight: bold;'>{formatar_moeda(v)}</span>" if v > 0 else "-"
        d_cor = f"<span style='color: #d32f2f; font-weight: bold;'>{formatar_moeda(d)}</span>" if d > 0 else "-"
        linhas_verbas += f"<tr><td>{desc}</td><td class='text-right'>{v_cor}</td><td class='text-right'>{d_cor}</td></tr>"

    html = f"""
    <html>
    <head>
        <style>
            /* CONFIGURAÇÃO DA FOLHA: Tira as margens que criam o espaço branco */
            @page {{ size: A4; margin: 8mm; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #fff; }}
            
            /* LARGURA TOTAL: Força o documento a ocupar 100% do papel */
            .documento-full {{ width: 100% !important; border: 2.5px solid #000; padding: 15px; box-sizing: border-box; min-height: 270mm; }}
            
            .header-trct {{ width: 100%; border-bottom: 3px solid #000; margin-bottom: 10px; padding-bottom: 5px; }}
            .faixa-preta {{ background: #333; color: #fff; border: 1px solid #000; padding: 8px; font-weight: bold; text-transform: uppercase; margin-top: 15px; font-size: 13px; }}
            
            .dados-box {{ border: 1px solid #000; padding: 10px; margin-top: -1px; font-size: 14px; line-height: 1.8; width: 100%; box-sizing: border-box; }}
            
            /* Tabela ocupando toda a largura disponível */
            table {{ width: 100% !important; border-collapse: collapse; margin-top: 5px; }}
            th, td {{ border: 1px solid #000; padding: 8px; text-align: left; font-size: 13px; }}
            th {{ background: #f2f2f2; font-weight: bold; }}
            .text-right {{ text-align: right; }}
            
            /* Valor Final em Azul na Direita */
            .wrapper-final {{ display: flex; justify-content: flex-end; margin-top: 20px; width: 100%; }}
            .card-azul {{ border: 3px solid #002f6c; background: #f0f4f8; padding: 15px 40px; text-align: center; color: #002f6c; min-width: 280px; }}
            
            .assinatura-box {{ margin-top: 60px; text-align: center; width: 100%; }}
            .linha-assinatura {{ border-top: 2px solid #000; width: 70%; margin: 0 auto; padding-top: 5px; font-weight: bold; }}
            .nome-funcionario {{ font-size: 16px; font-weight: bold; text-transform: uppercase; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="documento-full">
            <div class="header-trct">
                <b style="font-size: 22px;">TERMO DE RESCISÃO DE CONTRATO DE TRABALHO</b>
            </div>
            
            <div class="faixa-preta">Dados do Contrato</div>
            <div class="dados-box">
                <strong>Nome do Trabalhador:</strong> {dados_func['nome']} <br>
                <strong>Admissão:</strong> {dados_func['adm']} | <strong>Afastamento:</strong> {dados_func['rescisao']} <br>
                <strong>Causa:</strong> {dados_func['causa']} | <strong>Aviso:</strong> {dados_func['aviso_tipo']}
            </div>

            <div class="faixa-preta">Verbas Rescisórias</div>
            <table>
                <thead>
                    <tr>
                        <th width="60%">DESCRIÇÃO</th>
                        <th class="text-right">VENCIMENTOS (R$)</th>
                        <th class="text-right">DESCONTOS (R$)</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_verbas}
                    <tr style="background: #eee; font-weight: bold;">
                        <td>TOTAIS DAS VERBAS</td>
                        <td class="text-right" style="color: #2e7d32;">{formatar_moeda(totais_res['bruto'])}</td>
                        <td class="text-right" style="color: #d32f2f;">{formatar_moeda(totais_res['descontos'])}</td>
                    </tr>
                </tbody>
            </table>

            <div class="faixa-preta">FGTS e Multa</div>
            <div class="dados-box">
                Saldo Informado: {formatar_moeda(totais_res['fgts_informado'])} | 
                Multa Rescisória: {formatar_moeda(totais_res['multa_valor'])} <br>
                <b style="font-size: 15px;">TOTAL DE FGTS DISPONÍVEL: {formatar_moeda(totais_res['fgts_total_geral'])}</b>
            </div>

            <div class="wrapper-final">
                <div class="card-azul">
                    <span style="font-size: 12px; font-weight: bold; text-transform: uppercase;">Líquido Final a Receber</span><br>
                    <span style="font-size: 26px; font-weight: bold;">{formatar_moeda(totais_res['liquido_final'])}</span>
                </div>
            </div>

            <div class="assinatura-box">
                <div style="margin-bottom: 35px; font-size: 14px;">Data: ____/____/2026</div>
                <div class="linha-assinatura">Assinatura do Funcionário</div>
                <div class="nome-funcionario">{dados_func['nome']}</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(c_html, "w", encoding="utf-8") as f: 
        f.write(html)
    converter_e_limpar(c_html, c_pdf)
# =================================================================
# 📑 4. FÉRIAS (AVISO E RECIBO)
# =================================================================

def gerar_recibo_ferias_exclusivo(d_func, itens_calculo):
    pasta = os.path.join("Documentos_DP", "Ferias")
    if not os.path.exists(pasta): os.makedirs(pasta)
    
    nome_f = re.sub(r'[\\/*?:"<>|]', "", d_func["nome"]).strip().replace(" ", "_")
    data_s = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    c_html = os.path.join(pasta, f"TEMP_RECIBO_{nome_f}.html")
    c_pdf = os.path.join(pasta, f"Recibo_Ferias_{nome_f}_{data_s}.pdf")

    # Cores DNA Je: Verde para Vencimentos e Vermelho para Descontos
    total_v, total_d = 0.0, 0.0
    linhas_tabela = ""
    for desc, ref, v, d in itens_calculo:
        total_v += v; total_d += d
        v_cor = f"<span style='color: #2e7d32; font-weight: bold;'>{formatar_moeda(v)}</span>" if v > 0 else "-"
        d_cor = f"<span style='color: #d32f2f; font-weight: bold;'>{formatar_moeda(d)}</span>" if d > 0 else "-"
        linhas_tabela += f"<tr><td>{desc}</td><td style='text-align:center;'>{ref}</td><td class='text-right'>{v_cor}</td><td class='text-right'>{d_cor}</td></tr>"

    estilo_css = """
    <style>
        /* CONFIGURAÇÃO DA FOLHA: Força margens mínimas */
        @page { size: A4; margin: 5mm; }
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #fff; width: 100%; }
        
        /* LARGURA TOTAL: Agora o container ocupa 100% da folha */
        .container { width: 100% !important; padding: 0; margin: 0; box-sizing: border-box; }
        
        .via { 
            border: 2.5px solid #000; 
            padding: 20px; 
            margin-bottom: 15px; 
            width: 100%; 
            box-sizing: border-box; 
            background: #fff; 
        }
        
        .linha-corte { border-top: 2px dashed #000; text-align: center; margin: 10px 0; font-size: 11px; font-weight: bold; }
        
        .header { width: 100%; border-bottom: 3px solid #000; margin-bottom: 10px; }
        .sec-titulo { background: #333; color: #fff; padding: 8px; font-weight: bold; text-transform: uppercase; margin-top: 10px; font-size: 12px; border: 1px solid #000; }
        .box-dados { border: 1px solid #000; padding: 12px; margin-top: -1px; font-size: 14px; line-height: 1.6; }
        
        /* Tabela com quadradinhos ocupando tudo */
        table { width: 100% !important; border-collapse: collapse; margin-top: 5px; }
        th, td { border: 1px solid #000; padding: 10px; text-align: left; font-size: 13px; }
        th { background: #f2f2f2; font-weight: bold; }
        .text-right { text-align: right; }
        
        .footer-area { display: flex; justify-content: flex-end; margin-top: 15px; }
        
        /* Card de Líquido Azul na Direita */
        .box-azul { 
            border: 3px solid #002f6c; 
            background: #f0f4f8; 
            text-align: center; 
            padding: 12px 40px; 
            color: #002f6c;
            min-width: 280px;
        }
        
        .assinatura-area { margin-top: 50px; text-align: center; }
        .linha { border-top: 2.5px solid #000; width: 80%; margin: 0 auto; padding-top: 5px; font-weight: bold; }
        .nome-trabalhador { font-size: 16px; font-weight: bold; text-transform: uppercase; margin-top: 5px; }
    </style>
    """

    def criar_via(label):
        return f"""
        <div class="via">
            <div style="text-align: right; font-size: 10px; color: #888; font-weight: bold; margin-bottom: 5px;">{label}</div>
            <table class="header" style="border:none;">
                <tr style="border:none;">
                    <td style="border:none;"><b style="font-size: 22px;">RECIBO DE FÉRIAS</b></td>
                    <td style="border:none; text-align: right; font-size: 16px;">Data do Pagamento: <b>{datetime.datetime.now().strftime('%d/%m/%Y')}</b></td>
                </tr>
            </table>

            <div class="sec-titulo">Dados da Concessão</div>
            <div class="box-dados">
                <b>Trabalhador:</b> {d_func['nome']} | <b>Cargo:</b> {d_func['cargo']} <br>
                <b>Admissão:</b> {d_func['admissao']} | <b>Período Aquisitivo:</b> {d_func['aq_ini']} a {d_func['aq_fim']} <br>
                <b>Período de Gozo:</b> {d_func['gozo_ini']} a {d_func['gozo_fim']} ({d_func['dias_gozo']} dias)
            </div>

            <table>
                <thead>
                    <tr>
                        <th width="55%">DESCRIÇÃO DAS VERBAS</th>
                        <th width="10%" style="text-align:center;">REF.</th>
                        <th class="text-right">VENCIMENTOS</th>
                        <th class="text-right">DESCONTOS</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_tabela}
                    <tr style="background: #eee; font-weight: bold;">
                        <td colspan="2" class="text-right">TOTAIS</td>
                        <td class="text-right" style="color: #2e7d32;">{formatar_moeda(total_v)}</td>
                        <td class="text-right" style="color: #d32f2f;">{formatar_moeda(total_d)}</td>
                    </tr>
                </tbody>
            </table>

            <div class="footer-area">
                <div class="box-azul">
                    <span style="font-size: 12px; font-weight: bold; text-transform: uppercase;">Líquido a Receber</span><br>
                    <span style="font-size: 24px; font-weight: bold;">{formatar_moeda(total_v - total_d)}</span>
                </div>
            </div>

            <div class="assinatura-area">
                <div style="margin-bottom: 30px; font-size: 14px;">Data: ____/____/2026</div>
                <div class="linha">Assinatura do Funcionário</div>
                <div class="nome-trabalhador">{d_func['nome']}</div>
            </div>
        </div>
        """

    html_final = f"""
    <html>
        <head>{estilo_css}</head>
        <body>
            <div class="container">
                {criar_via("VIA DO EMPREGADOR")}
                <div class="linha-corte">------------------ CORTE AQUI ------------------</div>
                {criar_via("VIA DO TRABALHADOR")}
            </div>
        </body>
    </html>
    """
    
    with open(c_html, "w", encoding="utf-8") as f: f.write(html_final)
    converter_e_limpar(c_html, c_pdf)

# =================================================================
# 📑 5. FOLHA DE PONTO
# =================================================================



def gerar_lista_frequencia(dados):
    pasta = os.path.join("Documentos_DP", "Pontos")
    if not os.path.exists(pasta): os.makedirs(pasta)
    
    nome_f = re.sub(r'[\\/*?:"<>|]', "", dados["nome"]).strip().replace(" ", "_")
    # Gera um nome único para o arquivo não ser sobreposto
    c_html = os.path.join(pasta, f"TEMP_PONTO_{nome_f}.html")
    c_pdf = os.path.join(pasta, f"Folha_Ponto_{nome_f}.pdf")

    # 1. INTELIGÊNCIA DE CALENDÁRIO
    ultimo_dia = calendar.monthrange(dados['ano'], dados['mes'])[1]
    periodo_full = f"01/{str(dados['mes']).zfill(2)}/{dados['ano']} A {str(ultimo_dia).zfill(2)}/{str(dados['mes']).zfill(2)}/{dados['ano']}"
    dias_semana_pt = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    
    linhas = ""
    for dia in range(1, ultimo_dia + 1):
        data_obj = datetime.date(dados['ano'], dados['mes'], dia)
        d_sem = dias_semana_pt[data_obj.weekday()]
        # Destaque para finais de semana para facilitar a localização visual
        cor_fundo = "background-color: #f5f5f5;" if data_obj.weekday() >= 5 else ""
        linhas += f"<tr style='{cor_fundo}'><td style='text-align:center; font-weight:bold;'>{dia}</td><td>{d_sem}</td><td></td><td></td><td></td><td></td><td></td></tr>"

    # 2. HTML E CSS DE ALTO PADRÃO (OCUPA A FOLHA TODA)
    html = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 8mm 6mm; }}
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; width: 100%; color: #000; }}
            .container {{ width: 100% !important; box-sizing: border-box; }}
            
            /* CABEÇALHO EM DUAS COLUNAS - LARGURA TOTAL */
            .header-master {{ display: table; width: 100%; margin-bottom: 15px; border-collapse: collapse; }}
            .col-esquerda {{ display: table-cell; width: 66%; vertical-align: top; }}
            .col-box-empresa {{ display: table-cell; width: 33%; border: 1.5px solid #000; padding: 10px; text-align: center; vertical-align: middle; font-size: 11px; }}
            
            .nome-destaque {{ font-size: 26px; font-weight: bold; text-transform: uppercase; border-bottom: 3px solid #000; display: inline-block; margin-bottom: 4px; }}
            .titulo-frequencia {{ font-size: 15px; font-weight: bold; margin: 6px 0; }}
            .detalhes-texto {{ font-size: 12px; line-height: 1.5; }}
            
            /* TABELA OTIMIZADA PARA 1 PÁGINA */
            table {{ width: 100% !important; border-collapse: collapse; table-layout: fixed; }}
            th, td {{ border: 1.2px solid #000; padding: 4px; font-size: 12px; }}
            td {{ height: 26px; }} /* Altura ideal para caber 31 dias + cabeçalho em 1 folha */
            th {{ background: #eeeeee; font-size: 10px; text-transform: uppercase; font-weight: bold; }}
            
            /* RODAPÉ LIMPO SÓ COM ASSINATURA */
            .assinatura-container {{ margin-top: 35px; text-align: center; width: 100%; }}
            .linha-ass {{ border-top: 2px solid #000; width: 60%; margin: 0 auto; padding-top: 4px; font-weight: bold; font-size: 13px; }}
            .nome-final {{ text-transform: uppercase; font-weight: bold; font-size: 14px; margin-top: 2px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-master">
                <div class="col-esquerda">
                    <div class="nome-destaque">{dados['nome']}</div>
                    <div class="titulo-frequencia">LISTA DE FREQUÊNCIA DE {periodo_full}</div>
                    <div class="detalhes-texto">
                        <b>Trabalhador:</b> {dados['nome']}<br>
                        <b>Cargo:</b> {dados['cargo']}<br>
                        <b>CTPS / Série:</b> {dados['ctps']} / {dados['serie']}<br>
                        <b>Descr. Jornada:</b> {dados['jornada']}<br>
                        <b>Lotação:</b> {dados['lotacao']}
                    </div>
                </div>
                <div class="col-box-empresa">
                    <b>CPF / CNPJ: {dados['cpf']}</b><br><br>
                    <b style="font-size: 13px;">{dados['empresa']}</b><br>
                    {dados['endereco']}
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 7%;">Dia</th>
                        <th style="width: 17%;">Dia da Semana</th>
                        <th style="width: 11%;">Entrada</th>
                        <th style="width: 11%;">Repouso</th>
                        <th style="width: 11%;">Retorno</th>
                        <th style="width: 11%;">Saída</th>
                        <th>Assinatura</th>
                    </tr>
                </thead>
                <tbody>{linhas}</tbody>
            </table>
            <br>
            <div class="assinatura-container">
                <div class="linha-ass">Assinatura do Funcionário</div>
                <div class="nome-final">{dados['nome']}</div>
            </div>
        </div>
    </body>
    </html>
    """
    with open(c_html, "w", encoding="utf-8") as f:
        f.write(html)
        
    converter_e_limpar(c_html, c_pdf)