# -*- coding: utf-8 -*-
"""
relatorios.py
Versão MINIMALISTA e FUNCIONAL - gera apenas HTML no navegador (sem PDF)
Corrige TODOS os typos críticos que quebravam o sistema inteiro.
"""
import webbrowser
import os
import datetime
import re
from ferramentas import formatar_moeda
import calendar

def sanitizar_nome(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome).strip().replace(" ", "_")

def garantir_pasta(categoria):
    pasta = os.path.join("Documentos_DP", categoria)
    os.makedirs(pasta, exist_ok=True)
    return pasta

def gerar_recibo_folha(nome_func, dados_cabecalho, tabela_itens, totais):
    pasta = garantir_pasta("Holerites")
    nome_arq = sanitizar_nome(f"holerite_{nome_func}_{dados_cabecalho.get('Competência', 'sem_data')}")
    caminho_html = os.path.join(pasta, f"{nome_arq}.html")
    
    total_v = sum(item.get('valor', 0) for item in tabela_itens)
    total_d = sum(item.get('desconto', 0) for item in tabela_itens)
    liquido = total_v - total_d
    
    linhas = ""
    for item in tabela_itens:
        desc = item.get('descricao', '')
        ref = item.get('ref', '')
        v = formatar_moeda(item['valor']) if item.get('valor', 0) > 0 else ""
        d = formatar_moeda(item['desconto']) if item.get('desconto', 0) > 0 else ""
        linhas += f"<tr><td>{desc}</td><td>{ref}</td><td>{v}</td><td>{d}</td></tr>\n"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Recibo {nome_func}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        .liquido {{ font-size: 20px; font-weight: bold; text-align: right; margin: 20px 0; color: #2c7be5; }}
        .via {{ page-break-after: always; margin-bottom: 40px; }}
    </style>
</head>
<body>
    <div class="via">
        <h2>VIA DO EMPREGADOR</h2>
        <h3>RECIBO DE PAGAMENTO</h3>
        <p><strong>Competência:</strong> {dados_cabecalho.get('Competência', '-')}</p>
        <p><strong>Funcionário:</strong> {nome_func}</p>
        
        <table>
            <tr><th>DESCRIÇÃO</th><th>REF.</th><th>VENCIMENTOS</th><th>DESCONTOS</th></tr>
            {linhas}
            <tr><td colspan="2"><strong>TOTAIS</strong></td><td><strong>{formatar_moeda(total_v)}</strong></td><td><strong>{formatar_moeda(total_d)}</strong></td></tr>
        </table>
        
        <div class="liquido">LÍQUIDO A RECEBER: {formatar_moeda(liquido)}</div>
        
        <p>Data: ____/____/____</p>
        <p>___________________________________</p>
        <p>{nome_func}</p>
        <p>Assinatura do Funcionário</p>
    </div>
    
    <div class="via">
        <h2>VIA DO TRABALHADOR</h2>
        <h3>RECIBO DE PAGAMENTO</h3>
        <p><strong>Competência:</strong> {dados_cabecalho.get('Competência', '-')}</p>
        <p><strong>Funcionário:</strong> {nome_func}</p>
        
        <table>
            <tr><th>DESCRIÇÃO</th><th>REF.</th><th>VENCIMENTOS</th><th>DESCONTOS</th></tr>
            {linhas}
            <tr><td colspan="2"><strong>TOTAIS</strong></td><td><strong>{formatar_moeda(total_v)}</strong></td><td><strong>{formatar_moeda(total_d)}</strong></td></tr>
        </table>
        
        <div class="liquido">LÍQUIDO A RECEBER: {formatar_moeda(liquido)}</div>
        
        <p>Data: ____/____/____</p>
        <p>___________________________________</p>
        <p>{nome_func}</p>
        <p>Assinatura do Funcionário</p>
    </div>
</body>
</html>"""
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    
    webbrowser.open(f"file://{os.path.realpath(caminho_html)}")

# Compatibilidade com aba_folha.py
def gerar_recibo_html(titulo_doc, tipo_arquivo, nome_funcionario, dados_cabecalho, tabela_itens, totais):
    gerar_recibo_folha(nome_funcionario, dados_cabecalho, tabela_itens, totais)

def gerar_trct_html(dados_func, verbas, totais_res):
    pasta = garantir_pasta("Rescisoes")
    nome_arq = sanitizar_nome(f"rescisao_{dados_func['nome']}")
    caminho_html = os.path.join(pasta, f"{nome_arq}.html")
    
    linhas = ""
    for v in verbas:
        desc = v.get('descricao', '')
        valor = formatar_moeda(v['valor']) if v.get('valor', 0) > 0 else ""
        desc_val = formatar_moeda(v['desconto']) if v.get('desconto', 0) > 0 else ""
        linhas += f"<tr><td>{desc}</td><td>{valor}</td><td>{desc_val}</td></tr>\n"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TRCT {dados_func['nome']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        .liquido {{ font-size: 22px; font-weight: bold; text-align: right; margin: 25px 0; color: #2c7be5; }}
    </style>
</head>
<body>
    <h2 style="text-align:center;">TERMO DE RESCISÃO DE CONTRATO DE TRABALHO</h2>
    
    <p><strong>Nome:</strong> {dados_func['nome']}</p>
    <p><strong>Admissão:</strong> {dados_func['adm']} | <strong>Rescisão:</strong> {dados_func['rescisao']}</p>
    <p><strong>Causa:</strong> {dados_func['causa']} | <strong>Aviso:</strong> {dados_func['aviso_tipo']}</p>
    
    <table>
        <tr><th>DESCRIÇÃO</th><th>VENCIMENTOS (R$)</th><th>DESCONTOS (R$)</th></tr>
        {linhas}
        <tr><td><strong>TOTAIS DAS VERBAS</strong></td><td><strong>{formatar_moeda(totais_res['bruto'])}</strong></td><td><strong>{formatar_moeda(totais_res['descontos'])}</strong></td></tr>
    </table>
    
    <p><strong>FGTS Informado:</strong> {formatar_moeda(totais_res['fgts_informado'])}</p>
    <p><strong>Multa Rescisória ({totais_res['perc_multa']}%):</strong> {formatar_moeda(totais_res['multa_valor'])}</p>
    <p><strong>TOTAL FGTS DISPONÍVEL:</strong> {formatar_moeda(totais_res['fgts_total_geral'])}</p>
    
    <div class="liquido">LÍQUIDO FINAL A RECEBER: {formatar_moeda(totais_res['liquido_final'])}</div>
    
    <p>Data: ____/____/____</p>
    <p>___________________________________</p>
    <p>{dados_func['nome']}</p>
    <p>Assinatura do Funcionário</p>
</body>
</html>"""
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    
    webbrowser.open(f"file://{os.path.realpath(caminho_html)}")

def gerar_recibo_ferias_exclusivo(d_func, itens_calculo):
    pasta = garantir_pasta("Ferias")
    nome_arq = sanitizar_nome(f"ferias_{d_func['nome']}")
    caminho_html = os.path.join(pasta, f"{nome_arq}.html")
    
    total_v = sum(item.get('valor', 0) for item in itens_calculo)
    total_d = sum(item.get('desconto', 0) for item in itens_calculo)
    liquido = total_v - total_d
    
    linhas = ""
    for item in itens_calculo:
        desc = item.get('descricao', '')
        ref = item.get('ref', '')
        v = formatar_moeda(item['valor']) if item.get('valor', 0) > 0 else ""
        d = formatar_moeda(item['desconto']) if item.get('desconto', 0) > 0 else ""
        linhas += f"<tr><td>{desc}</td><td>{ref}</td><td>{v}</td><td>{d}</td></tr>\n"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Férias {d_func['nome']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        .liquido {{ font-size: 20px; font-weight: bold; text-align: right; margin: 20px 0; color: #2c7be5; }}
        .dados {{ background-color: #f9f9f9; padding: 10px; margin: 15px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="via">
        <h2>VIA DO EMPREGADOR</h2>
        <h3>RECIBO DE FÉRIAS</h3>
        <p><strong>Data do Pagamento:</strong> {datetime.datetime.now().strftime('%d/%m/%Y')}</p>
        
        <div class="dados">
            <p><strong>Trabalhador:</strong> {d_func['nome']} | <strong>Cargo:</strong> {d_func['cargo']}</p>
            <p><strong>Admissão:</strong> {d_func['admissao']}</p>
            <p><strong>Período Aquisitivo:</strong> {d_func['aq_ini']} a {d_func['aq_fim']}</p>
            <p><strong>Período de Gozo:</strong> {d_func['gozo_ini']} a {d_func['gozo_fim']} ({d_func['dias_gozo']} dias)</p>
        </div>
        
        <table>
            <tr><th>DESCRIÇÃO DAS VERBAS</th><th>REF.</th><th>VENCIMENTOS</th><th>DESCONTOS</th></tr>
            {linhas}
            <tr><td colspan="2"><strong>TOTAIS</strong></td><td><strong>{formatar_moeda(total_v)}</strong></td><td><strong>{formatar_moeda(total_d)}</strong></td></tr>
        </table>
        
        <div class="liquido">LÍQUIDO A RECEBER: {formatar_moeda(liquido)}</div>
        
        <p>Data: ____/____/____</p>
        <p>___________________________________</p>
        <p>{d_func['nome']}</p>
        <p>Assinatura do Funcionário</p>
    </div>
    
    <div class="via">
        <h2>VIA DO TRABALHADOR</h2>
        <h3>RECIBO DE FÉRIAS</h3>
        <p><strong>Data do Pagamento:</strong> {datetime.datetime.now().strftime('%d/%m/%Y')}</p>
        
        <div class="dados">
            <p><strong>Trabalhador:</strong> {d_func['nome']} | <strong>Cargo:</strong> {d_func['cargo']}</p>
            <p><strong>Admissão:</strong> {d_func['admissao']}</p>
            <p><strong>Período Aquisitivo:</strong> {d_func['aq_ini']} a {d_func['aq_fim']}</p>
            <p><strong>Período de Gozo:</strong> {d_func['gozo_ini']} a {d_func['gozo_fim']} ({d_func['dias_gozo']} dias)</p>
        </div>
        
        <table>
            <tr><th>DESCRIÇÃO DAS VERBAS</th><th>REF.</th><th>VENCIMENTOS</th><th>DESCONTOS</th></tr>
            {linhas}
            <tr><td colspan="2"><strong>TOTAIS</strong></td><td><strong>{formatar_moeda(total_v)}</strong></td><td><strong>{formatar_moeda(total_d)}</strong></td></tr>
        </table>
        
        <div class="liquido">LÍQUIDO A RECEBER: {formatar_moeda(liquido)}</div>
        
        <p>Data: ____/____/____</p>
        <p>___________________________________</p>
        <p>{d_func['nome']}</p>
        <p>Assinatura do Funcionário</p>
    </div>
</body>
</html>"""
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    
    webbrowser.open(f"file://{os.path.realpath(caminho_html)}")

def gerar_lista_frequencia(dados):
    pasta = garantir_pasta("Pontos")
    nome_arq = sanitizar_nome(f"ponto_{dados['nome']}_{dados['periodo']}")
    caminho_html = os.path.join(pasta, f"{nome_arq}.html")
    
    mes, ano = map(int, dados['periodo'].split('/'))
    periodo_full = f"{calendar.month_name[mes].upper()}/{ano}"
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    
    linhas = ""
    for dia in range(1, dias_no_mes + 1):
        d = datetime.date(ano, mes, dia)
        dia_sem = calendar.day_name[d.weekday()][:3].upper()
        linhas += f"<tr><td>{dia:02d}</td><td>{dia_sem}</td><td>____:____</td><td></td><td></td><td>____:____</td><td></td></tr>\n"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ponto {dados['nome']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #000; padding: 6px; text-align: center; }}
        th {{ background-color: #f5f5f5; }}
        .cabecalho {{ text-align: center; margin-bottom: 20px; }}
        .dados-empresa {{ display: flex; justify-content: space-between; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="cabecalho">
        <h2>LISTA DE FREQUÊNCIA DE {periodo_full}</h2>
        <p><strong>Trabalhador:</strong> {dados['nome']} | <strong>Cargo:</strong> {dados['cargo']}</p>
        <p><strong>CTPS/Série:</strong> {dados['ctps']} / {dados['serie']} | 
           <strong>Jornada:</strong> {dados['jornada']} | 
           <strong>Lotação:</strong> {dados['lotacao']}</p>
    </div>
    
    <div class="dados-empresa">
        <div><strong>CPF:</strong> {dados['cpf']}</div>
        <div><strong>Empresa:</strong> {dados['empresa']}</div>
    </div>
    <p>{dados['endereco']}</p>
    
    <table>
        <tr>
            <th>Dia</th><th>Dia da Semana</th><th>Entrada</th><th>Repouso</th><th>Retorno</th><th>Saída</th><th>Assinatura</th>
        </tr>
        {linhas}
    </table>
    
    <p style="margin-top:40px;">___________________________________</p>
    <p>{dados['nome']}</p>
    <p>Assinatura do Funcionário</p>
</body>
</html>"""
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    
    webbrowser.open(f"file://{os.path.realpath(caminho_html)}")

# Função placeholder para não quebrar a aba_custos.py (implementar depois)
def gerar_relatorio_custos_leigo(dados_funcionario, resumo_custos, total_projecao):
    pasta = garantir_pasta("Custos")
    nome_arq = sanitizar_nome(f"custos_{dados_funcionario.get('meses', '12')}_meses")
    caminho_html = os.path.join(pasta, f"{nome_arq}.html")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Custos - {dados_funcionario.get('meses', '12')} meses</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
        .total {{ font-size: 22px; font-weight: bold; text-align: right; margin: 25px 0; color: #2c7be5; }}
    </style>
</head>
<body>
    <h2 style="text-align:center;">EXPLICAÇÃO DE CUSTOS TRABALHISTAS</h2>
    
    <p><strong>Período Projetado:</strong> {dados_funcionario.get('meses', '12')} meses</p>
    <p><strong>Escala de Trabalho:</strong> {dados_funcionario.get('escala', '5x2')}</p>
    <p><strong>Regime Tributário:</strong> {dados_funcionario.get('regime', 'Simples Nacional')}</p>
    <p><strong>Admissão Estimada:</strong> {dados_funcionario.get('adm_estimada', '...')}</p>
    <p><strong>Data Final Projetada:</strong> {dados_funcionario.get('data_final', '...')}</p>
    
    <table>
        <tr><th>ITEM</th><th>VALOR MENSAL (R$)</th></tr>
        <tr><td>Salário Base + Adicionais</td><td>{formatar_moeda(resumo_custos.get('base', 0))}</td></tr>
        <tr><td>FGTS (8%)</td><td>{formatar_moeda(resumo_custos.get('fgts_mes', 0))}</td></tr>
        <tr><td>INSS Patronal</td><td>{formatar_moeda(resumo_custos.get('inss_patr', 0))}</td></tr>
        <tr><td>Provisão 13º Salário</td><td>{formatar_moeda(resumo_custos.get('p_13', 0))}</td></tr>
        <tr><td>Provisão Férias + 1/3</td><td>{formatar_moeda(resumo_custos.get('p_ferias', 0) + resumo_custos.get('p_terco', 0))}</td></tr>
        <tr><td>VT Empresa</td><td>{formatar_moeda(resumo_custos.get('vt_empresa', 0))}</td></tr>
        <tr><td>VR Empresa</td><td>{formatar_moeda(resumo_custos.get('vr_empresa', 0))}</td></tr>
        <tr><td>Plano Saúde</td><td>{formatar_moeda(resumo_custos.get('saude', 0))}</td></tr>
        <tr><td>Descontos Manuais</td><td>- {formatar_moeda(resumo_custos.get('debitos_manuais', 0))}</td></tr>
        <tr><td><strong>TOTAL MENSAL</strong></td><td><strong>{formatar_moeda(resumo_custos.get('total_mensal', 0))}</strong></td></tr>
    </table>
    
    <div class="total">CUSTO TOTAL PROJETADO ({dados_funcionario.get('meses', '12')} meses): {formatar_moeda(total_projecao)}</div>
    
    <p style="margin-top:30px; font-style:italic;">
        Este relatório é uma estimativa para fins de planejamento. Valores reais podem variar conforme legislação vigente.
    </p>
</body>
</html>"""
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    
    webbrowser.open(f"file://{os.path.realpath(caminho_html)}")

# Função placeholder para não quebrar a aba_ferias.py
def gerar_aviso_ferias(dados_funcionario, dados_ferias):
    pasta = garantir_pasta("Avisos_Ferias")
    nome_arq = sanitizar_nome(f"aviso_ferias_{dados_funcionario['nome']}")
    caminho_html = os.path.join(pasta, f"{nome_arq}.html")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Aviso Férias {dados_funcionario['nome']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 40px; text-align: center; }}
        .aviso {{ border: 2px solid #000; padding: 30px; margin: 20px auto; max-width: 800px; }}
        h2 {{ color: #2c7be5; margin-bottom: 30px; }}
        .dados {{ margin: 25px 0; font-size: 18px; }}
        .destaque {{ font-size: 24px; font-weight: bold; color: #d63031; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="aviso">
        <h2>AVISO DE CONCESSÃO DE FÉRIAS</h2>
        
        <p class="dados"><strong>Funcionário:</strong> {dados_funcionario['nome']}</p>
        <p class="dados"><strong>Cargo:</strong> {dados_funcionario['cargo']}</p>
        
        <div class="destaque">
            PERÍODO DE FÉRIAS: {dados_ferias['inicio']} a {dados_ferias['fim']}
        </div>
        
        <p class="dados"><strong>Retorno ao trabalho:</strong> {dados_ferias['retorno']}</p>
        
        <p class="dados" style="margin-top:30px;">{dados_ferias['obs']}</p>
        
        <p style="margin-top:50px;">
            ___________________________<br>
            Assinatura do Empregador
        </p>
        
        <p style="margin-top:40px;">
            ___________________________<br>
            {dados_funcionario['nome']}<br>
            Assinatura do Empregado
        </p>
    </div>
</body>
</html>"""
    
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html)
    
    webbrowser.open(f"file://{os.path.realpath(caminho_html)}")