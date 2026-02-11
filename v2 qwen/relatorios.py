import webbrowser
import os
import datetime
import re
import sys
import calendar
from ferramentas import formatar_moeda

# =================================================================
# 🛠️ DETECÇÃO SEGURA DO PDFKIT (opcional)
# =================================================================
PDFKIT_DISPONIVEL = False
try:
    import pdfkit
    PDFKIT_DISPONIVEL = True
except ImportError:
    print("ℹ️  pdfkit não instalado. Relatórios serão abertos em HTML (wkhtmltopdf.exe ainda pode ser usado manualmente).")

def obter_caminho_wkhtmltopdf():
    """Localiza wkhtmltopdf.exe na pasta do app (funciona com PyInstaller)."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "wkhtmltopdf.exe")

# =================================================================
# 📄 GERADOR DE RELATÓRIOS (PDF com fallback para HTML)
# =================================================================
def gerar_relatorio(nome_base, categoria, html_content):
    """Gera relatório em PDF (se possível) ou abre HTML como fallback."""
    pasta = os.path.join("Documentos_DP", categoria)
    os.makedirs(pasta, exist_ok=True)
    
    caminho_html = os.path.join(pasta, f"{nome_base}.html")
    caminho_pdf = os.path.join(pasta, f"{nome_base}.pdf")
    
    # Salvar HTML (sempre funciona)
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Tentar converter para PDF apenas se pdfkit estiver disponível
    if PDFKIT_DISPONIVEL:
        try:
            caminho_exe = obter_caminho_wkhtmltopdf()
            if not os.path.exists(caminho_exe):
                raise FileNotFoundError(f"wkhtmltopdf.exe não encontrado em: {caminho_exe}")
            
            config = pdfkit.configuration(wkhtmltopdf=caminho_exe)
            opcoes = {
                'encoding': "UTF-8",
                'quiet': '',
                'enable-local-file-access': None,
                'margin-top': '10mm',
                'margin-bottom': '10mm',
                'margin-left': '10mm',
                'margin-right': '10mm',
                'page-size': 'A4'
            }
            pdfkit.from_file(caminho_html, caminho_pdf, configuration=config, options=opcoes)
            
            # Remover HTML temporário e abrir PDF
            os.remove(caminho_html)
            abrir_arquivo(caminho_pdf)
            return
        except Exception as e:
            print(f"⚠️  Conversão PDF falhou ({e}). Abrindo versão HTML...")
    
    # Fallback: abrir HTML no navegador
    abrir_arquivo(caminho_html)

def abrir_arquivo(caminho):
    """Abre arquivo no visualizador padrão do sistema."""
    abs_path = os.path.abspath(caminho)
    if sys.platform == "win32":
        os.startfile(abs_path)
    elif sys.platform == "darwin":
        os.system(f"open '{abs_path}'")
    else:
        os.system(f"xdg-open '{abs_path}'")

# =================================================================
# 🎨 ESTILO CSS PADRÃO PARA TODOS OS RELATÓRIOS
# =================================================================
CSS_PADRAO = """
<style>
    @page { size: A4; margin: 0; }
    body { 
        font-family: Arial, sans-serif; 
        font-size: 12px; 
        margin: 0; 
        padding: 15px;
        color: #333;
        line-height: 1.4;
    }
    .documento { 
        width: 210mm; 
        min-height: 297mm; 
        padding: 15px;
        box-sizing: border-box;
    }
    .via { page-break-after: always; }
    .corte { 
        text-align: center; 
        margin: 25px 0; 
        font-weight: bold; 
        color: #888;
        font-size: 18px;
        page-break-after: always;
    }
    table { 
        width: 100%; 
        border-collapse: collapse; 
        margin: 10px 0;
    }
    th, td { 
        border: 1px solid #000; 
        padding: 6px 8px; 
        text-align: left;
        vertical-align: top;
    }
    th { background-color: #f5f5f5; font-weight: bold; }
    .totais { font-weight: bold; background-color: #f9f9f9; }
    .liquido { 
        font-size: 18px; 
        font-weight: bold; 
        text-align: right; 
        padding: 15px;
        background-color: #e8f5e9;
        margin: 20px 0;
    }
    .cabecalho { 
        display: flex; 
        justify-content: space-between; 
        border-bottom: 2px solid #000; 
        padding-bottom: 10px; 
        margin-bottom: 20px;
    }
    .assinatura { 
        margin-top: 50px; 
        text-align: center; 
        font-size: 14px;
    }
    .dados-contrato { 
        background-color: #f9f9f9; 
        padding: 12px; 
        border-radius: 4px; 
        margin: 20px 0;
        font-size: 11px;
    }
</style>
"""

def sanitizar_nome(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome).strip().replace(" ", "_")

# =================================================================
# 📑 1. HOLERITE / RECIBO DE FOLHA
# =================================================================
def gerar_recibo_folha(nome_func, dados_cabecalho, tabela_itens, totais):
    # Calcular totais
    total_v = sum(item.get('valor', 0) for item in tabela_itens)
    total_d = sum(item.get('desconto', 0) for item in tabela_itens)
    liquido = total_v - total_d
    
    # Gerar linhas da tabela
    linhas = []
    for item in tabela_itens:
        desc = item.get('descricao', '')
        ref = item.get('ref', '')
        v = formatar_moeda(item['valor']) if item.get('valor', 0) > 0 else ""
        d = formatar_moeda(item['desconto']) if item.get('desconto', 0) > 0 else ""
        linhas.append(f"<tr><td>{desc}</td><td>{ref}</td><td>{v}</td><td>{d}</td></tr>")
    tabela_html = "\n".join(linhas)
    
    competencia = dados_cabecalho.get('Competência', '-')
    cpf = dados_cabecalho.get('CPF', '')
    
    def criar_via(tipo_via):
        return f"""
        <div class="via documento">
            <div class="cabecalho">
                <div><strong>{tipo_via}</strong></div>
                <div><strong>RECIBO DE PAGAMENTO</strong><br>Competência: {competencia}</div>
            </div>
            
            <table>
                <tr>
                    <th colspan="2">DADOS DO TRABALHADOR</th>
                </tr>
                <tr>
                    <td><strong>Nome:</strong> {nome_func}</td>
                    <td><strong>CPF:</strong> {cpf}</td>
                </tr>
            </table>
            
            <table>
                <thead>
                    <tr>
                        <th>DESCRIÇÃO</th>
                        <th>REF.</th>
                        <th>VENCIMENTOS</th>
                        <th>DESCONTOS</th>
                    </tr>
                </thead>
                <tbody>
                    {tabela_html}
                </tbody>
                <tfoot>
                    <tr class="totais">
                        <td colspan="2"><strong>TOTAIS</strong></td>
                        <td><strong>{formatar_moeda(total_v)}</strong></td>
                        <td><strong>{formatar_moeda(total_d)}</strong></td>
                    </tr>
                </tfoot>
            </table>
            
            <div class="liquido">
                LÍQUIDO A RECEBER: {formatar_moeda(liquido)}
            </div>
            
            <div class="assinatura">
                <div>Data: ____/____/____</div>
                <div style="margin-top:30px;">___________________________________</div>
                <div>{nome_func}</div>
                <div>Assinatura do Funcionário</div>
            </div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {CSS_PADRAO}
</head>
<body>
    {criar_via("VIA DO EMPREGADOR")}
    <div class="corte">----------</div>
    {criar_via("VIA DO TRABALHADOR")}
</body>
</html>"""
    
    nome_arq = sanitizar_nome(f"holerite_{nome_func}_{competencia}")
    gerar_relatorio(nome_arq, "Holerites", html)

# Compatibilidade com código existente
def gerar_recibo_html(titulo_doc, tipo_arquivo, nome_funcionario, dados_cabecalho, tabela_itens, totais):
    gerar_recibo_folha(nome_funcionario, dados_cabecalho, tabela_itens, totais)

# =================================================================
# 📑 2. RESCISÃO (TRCT)
# =================================================================
def gerar_trct_html(dados_func, verbas, totais_res):
    # Calcular totais
    total_v = sum(v.get('valor', 0) for v in verbas)
    total_d = sum(v.get('desconto', 0) for v in verbas)
    
    # Gerar linhas da tabela
    linhas = []
    for v in verbas:
        desc = v.get('descricao', '')
        valor = formatar_moeda(v['valor']) if v.get('valor', 0) > 0 else ""
        desc_val = formatar_moeda(v['desconto']) if v.get('desconto', 0) > 0 else ""
        linhas.append(f"<tr><td>{desc}</td><td>{valor}</td><td>{desc_val}</td></tr>")
    tabela_html = "\n".join(linhas)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {CSS_PADRAO}
</head>
<body>
    <div class="documento">
        <h2 style="text-align:center; margin-bottom:25px;">TERMO DE RESCISÃO DE CONTRATO DE TRABALHO</h2>
        
        <div class="dados-contrato">
            <strong>Dados do Contrato</strong><br>
            Nome do Trabalhador: {dados_func['nome']}<br>
            Admissão: {dados_func['adm']} | Afastamento: {dados_func['rescisao']}<br>
            Causa: {dados_func['causa']} | Aviso: {dados_func['aviso_tipo']}
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>DESCRIÇÃO</th>
                    <th>VENCIMENTOS (R$)</th>
                    <th>DESCONTOS (R$)</th>
                </tr>
            </thead>
            <tbody>
                {tabela_html}
            </tbody>
            <tfoot>
                <tr class="totais">
                    <td><strong>TOTAIS DAS VERBAS</strong></td>
                    <td><strong>{formatar_moeda(totais_res['bruto'])}</strong></td>
                    <td><strong>{formatar_moeda(totais_res['descontos'])}</strong></td>
                </tr>
            </tfoot>
        </table>
        
        <div class="dados-contrato">
            <strong>FGTS e Multa</strong><br>
            Saldo Informado: {formatar_moeda(totais_res['fgts_informado'])} | 
            Multa Rescisória: {formatar_moeda(totais_res['multa_valor'])}<br>
            <strong>TOTAL DE FGTS DISPONÍVEL: {formatar_moeda(totais_res['fgts_total_geral'])}</strong>
        </div>
        
        <div class="liquido">
            LÍQUIDO FINAL A RECEBER: {formatar_moeda(totais_res['liquido_final'])}
        </div>
        
        <div class="assinatura">
            <div>Data: ____/____/____</div>
            <div style="margin-top:40px;">___________________________________</div>
            <div>{dados_func['nome']}</div>
            <div>Assinatura do Funcionário</div>
        </div>
    </div>
</body>
</html>"""
    
    nome_arq = sanitizar_nome(f"rescisao_{dados_func['nome']}")
    gerar_relatorio(nome_arq, "Rescisoes", html)

# =================================================================
# 📑 3. FÉRIAS (RECIBO)
# =================================================================
def gerar_recibo_ferias_exclusivo(d_func, itens_calculo):
    total_v = sum(i.get('valor', 0) for i in itens_calculo)
    total_d = sum(i.get('desconto', 0) for i in itens_calculo)
    liquido = total_v - total_d
    
    linhas = []
    for item in itens_calculo:
        desc = item.get('descricao', '')
        ref = item.get('ref', '')
        v = formatar_moeda(item['valor']) if item.get('valor', 0) > 0 else ""
        d = formatar_moeda(item['desconto']) if item.get('desconto', 0) > 0 else ""
        linhas.append(f"<tr><td>{desc}</td><td>{ref}</td><td>{v}</td><td>{d}</td></tr>")
    tabela_html = "\n".join(linhas)
    
    data_pagto = datetime.datetime.now().strftime('%d/%m/%Y')
    
    def criar_via(tipo_via):
        return f"""
        <div class="via documento">
            <div class="cabecalho">
                <div><strong>{tipo_via}</strong></div>
                <div><strong>RECIBO DE FÉRIAS</strong><br>Data do Pagamento: {data_pagto}</div>
            </div>
            
            <div class="dados-contrato">
                <strong>Dados da Concessão</strong><br>
                Trabalhador: {d_func['nome']} | Cargo: {d_func['cargo']}<br>
                Admissão: {d_func['admissao']} | 
                Período Aquisitivo: {d_func['aq_ini']} a {d_func['aq_fim']}<br>
                Período de Gozo: {d_func['gozo_ini']} a {d_func['gozo_fim']} ({d_func['dias_gozo']} dias)
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>DESCRIÇÃO DAS VERBAS</th>
                        <th>REF.</th>
                        <th>VENCIMENTOS</th>
                        <th>DESCONTOS</th>
                    </tr>
                </thead>
                <tbody>
                    {tabela_html}
                </tbody>
                <tfoot>
                    <tr class="totais">
                        <td colspan="2"><strong>TOTAIS</strong></td>
                        <td><strong>{formatar_moeda(total_v)}</strong></td>
                        <td><strong>{formatar_moeda(total_d)}</strong></td>
                    </tr>
                </tfoot>
            </table>
            
            <div class="liquido">
                LÍQUIDO A RECEBER: {formatar_moeda(liquido)}
            </div>
            
            <div class="assinatura">
                <div>Data: ____/____/____</div>
                <div style="margin-top:30px;">___________________________________</div>
                <div>{d_func['nome']}</div>
                <div>Assinatura do Funcionário</div>
            </div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {CSS_PADRAO}
</head>
<body>
    {criar_via("VIA DO EMPREGADOR")}
    <div class="corte">----------</div>
    {criar_via("VIA DO TRABALHADOR")}
</body>
</html>"""
    
    nome_arq = sanitizar_nome(f"ferias_{d_func['nome']}")
    gerar_relatorio(nome_arq, "Ferias", html)

# =================================================================
# 📑 4. FOLHA DE PONTO (LISTA DE FREQUÊNCIA)
# =================================================================
def gerar_lista_frequencia(dados):
    periodo = dados.get('periodo', '01/2026')
    mes, ano = map(int, periodo.split('/'))
    periodo_full = f"{calendar.month_name[mes].upper()}/{ano}"
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    
    linhas = []
    for dia in range(1, dias_no_mes + 1):
        d = datetime.date(ano, mes, dia)
        dia_sem = calendar.day_name[d.weekday()][:3].upper()
        linhas.append(
            f"<tr>"
            f"<td>{dia:02d}</td>"
            f"<td>{dia_sem}</td>"
            f"<td>____:____</td>"
            f"<td></td>"
            f"<td></td>"
            f"<td>____:____</td>"
            f"<td></td>"
            f"</tr>"
        )
    tabela_html = "\n".join(linhas)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {CSS_PADRAO[7:-8]} /* Remove tags style inicial/final */
        .cabecalho-ponto {{
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .cabecalho-ponto h2 {{ margin: 8px 0; font-size: 20px; }}
        .dados-empresa {{
            display: flex;
            justify-content: space-between;
            margin: 15px 0;
            font-size: 11px;
        }}
    </style>
</head>
<body>
    <div class="documento">
        <div class="cabecalho-ponto">
            <h2>LISTA DE FREQUÊNCIA DE {periodo_full}</h2>
            <div><strong>Trabalhador:</strong> {dados['nome']} | <strong>Cargo:</strong> {dados['cargo']}</div>
            <div>
                <strong>CTPS/Série:</strong> {dados['ctps']} / {dados['serie']} | 
                <strong>Jornada:</strong> {dados['jornada']} | 
                <strong>Lotação:</strong> {dados['lotacao']}
            </div>
        </div>
        
        <div class="dados-empresa">
            <div><strong>CPF:</strong> {dados['cpf']}</div>
            <div><strong>Empresa:</strong> {dados['empresa']}</div>
        </div>
        <div style="font-size:11px; margin-bottom:20px;">{dados['endereco']}</div>
        
        <table>
            <thead>
                <tr>
                    <th>Dia</th>
                    <th>Dia da Semana</th>
                    <th>Entrada</th>
                    <th>Repouso</th>
                    <th>Retorno</th>
                    <th>Saída</th>
                    <th>Assinatura</th>
                </tr>
            </thead>
            <tbody>
                {tabela_html}
            </tbody>
        </table>
        
        <div class="assinatura" style="margin-top:40px;">
            <div>___________________________________</div>
            <div>{dados['nome']}</div>
            <div>Assinatura do Funcionário</div>
        </div>
    </div>
</body>
</html>"""
    
    nome_arq = sanitizar_nome(f"ponto_{dados['nome']}_{periodo}")
    gerar_relatorio(nome_arq, "Pontos", html)