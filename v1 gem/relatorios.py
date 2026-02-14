import os
import sys
import pdfkit
import datetime

# =================================================================
# 🛠️ MOTOR E CONVERSOR (PREPARADO PARA O SEU MODELO)
# =================================================================

def obter_caminho_motor():
    if getattr(sys, 'frozen', False):
        caminho_base = sys._MEIPASS
    else:
        caminho_base = os.path.abspath(".")
    return os.path.join(caminho_base, "wkhtmltopdf.exe")

def gerar_recibo_folha(nome_func, dados_cabecalho, tabela_itens, totais):
    """
    Gera o PDF do Holerite com DUAS VIAS e LINHA DE CORTE.
    """
    pasta_saida = "Documentos_DP/Holerites"
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
    
    nome_arquivo = f"Holerite_{nome_func.replace(' ', '_')}_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
    c_pdf = os.path.join(pasta_saida, nome_arquivo)
    c_html = c_pdf.replace(".pdf", ".html")

    # Monta as linhas da tabela em HTML
    linhas_html = ""
    for desc, ref, prov, desc_val in tabela_itens:
        linhas_html += f"""
        <tr>
            <td style="border: 1px solid #000; padding: 4px;">{desc}</td>
            <td style="border: 1px solid #000; padding: 4px; text-align: center;">{ref}</td>
            <td style="border: 1px solid #000; padding: 4px; text-align: right;">{prov:,.2f}</td>
            <td style="border: 1px solid #000; padding: 4px; text-align: right;">{desc_val:,.2f}</td>
        </tr>"""

    # O MODELO DE DUAS VIAS (EMPREGADOR / EMPREGADO)
    html_template = f"""
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; font-size: 11px;">
        {''.join([f'''
        <div style="border: 2px solid #000; padding: 15px; margin-bottom: 10px; position: relative;">
            <div style="text-align: center; font-weight: bold; font-size: 14px; border-bottom: 2px solid #000; padding-bottom: 5px; margin-bottom: 10px;">
                RECIBO DE PAGAMENTO DE SALÁRIO - {dados_cabecalho.get('Competência', '00/0000')}
            </div>
            
            <table style="width: 100%; margin-bottom: 10px;">
                <tr>
                    <td style="width: 70%;"><b>Funcionário:</b> {nome_func}</td>
                    <td style="text-align: right;"><b>Via:</b> {'EMPREGADOR' if i == 0 else 'EMPREGADO'}</td>
                </tr>
            </table>

            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #eee;">
                        <th style="border: 1px solid #000; padding: 5px;">Descrição</th>
                        <th style="border: 1px solid #000; padding: 5px;">Ref.</th>
                        <th style="border: 1px solid #000; padding: 5px;">Vencimentos</th>
                        <th style="border: 1px solid #000; padding: 5px;">Descontos</th>
                    </tr>
                </thead>
                <tbody>{linhas_html}</tbody>
            </table>

            <table style="width: 100%; margin-top: 10px; border-collapse: collapse;">
                <tr>
                    <td style="border: 1px solid #000; padding: 5px; width: 25%;"><b>Total Bruto</b></td>
                    <td style="border: 1px solid #000; padding: 5px; width: 25%; text-align: right;">{totais['bruto']:,.2f}</td>
                    <td style="border: 1px solid #000; padding: 5px; width: 25%;"><b>Total Descontos</b></td>
                    <td style="border: 1px solid #000; padding: 5px; width: 25%; text-align: right;">{totais['descontos']:,.2f}</td>
                </tr>
                <tr>
                    <td colspan="3" style="border: 1px solid #000; padding: 8px; text-align: right; font-size: 13px;"><b>LÍQUIDO A RECEBER:</b></td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: right; font-size: 13px; font-weight: bold; background-color: #f9f9f9;">R$ {totais['liquido']:,.2f}</td>
                </tr>
            </table>

            <div style="margin-top: 40px;">
                <div style="display: inline-block; width: 45%; border-top: 1px solid #000; text-align: center; padding-top: 5px;">Data</div>
                <div style="display: inline-block; width: 8%;"></div>
                <div style="display: inline-block; width: 45%; border-top: 1px solid #000; text-align: center; padding-top: 5px;">Assinatura do Funcionário</div>
            </div>
        </div>
        {'' if i == 1 else '<div style="border-top: 1px dashed #000; text-align: center; margin: 15px 0; color: #666; font-size: 10px;">Corte Aqui</div>'}
        ''' for i in range(2)])}
    </body>
    </html>
    """

    with open(c_html, "w", encoding="utf-8") as f:
        f.write(html_template)

    try:
        motor = obter_caminho_motor()
        config = pdfkit.configuration(wkhtmltopdf=motor)
        pdfkit.from_file(c_html, c_pdf, configuration=config)
        os.remove(c_html)
        os.startfile(os.path.abspath(c_pdf))
    except Exception as e:
        print(f"Erro no PDF: {e}")