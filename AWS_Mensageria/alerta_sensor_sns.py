# -*- coding: utf-8 -*-
"""
FarmTech Solutions - Serviço de Mensageria na AWS (Amazon SNS)
================================================================

Lê as leituras de sensores da Fase 3 (N, P, K, temperatura, umidade, pH e
chuva), verifica se algum valor está fora da faixa ideal e, em caso de
problema, dispara um ALERTA por e-mail usando o Amazon SNS (Simple
Notification Service).

Fluxo:
    CSV de sensores (Fase 3)  ->  Regras de faixa ideal  ->  Amazon SNS  ->  E-mail

Como usar:
    1) Crie um Tópico SNS no console da AWS e uma assinatura de e-mail
       (passo a passo no README.md desta pasta).
    2) Configure as credenciais da AWS (aws configure) e a variável de
       ambiente SNS_TOPIC_ARN com o ARN do seu tópico.
    3) Rode:  python alerta_sensor_sns.py

    Modo de teste (sem AWS): mostra na tela a mensagem que SERIA enviada,
    útil para tirar prints antes de configurar a conta:
        python alerta_sensor_sns.py --simular
"""

import os
import csv
import sys
import argparse
from datetime import datetime

# Garante acentuação correta no console do Windows (evita UnicodeEncodeError).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# boto3 é o SDK oficial da AWS para Python. Só é necessário no envio real.
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None  # Continua funcionando no modo --simular


# ---------------------------------------------------------------------------
# 1) FAIXAS IDEAIS DOS SENSORES (parâmetros agronômicos)
#    Se a leitura sair destes limites, geramos um alerta.
# ---------------------------------------------------------------------------
#    Cada parâmetro também traz a AÇÃO CORRETIVA que o funcionário deve tomar
#    quando o valor está BAIXO ou ALTO (ações definidas pelo grupo IA_Underground).
FAIXAS_IDEAIS = {
    # chave: dict com limites, unidade, nome e ações corretivas
    "N": {
        "min": 30, "max": 140, "unidade": "mg/kg", "nome": "Nitrogênio",
        "acao_baixo": "Aplicar adubação nitrogenada (ureia ou sulfato de amônio).",
        "acao_alto":  "Suspender adubação nitrogenada; risco de salinização do solo.",
    },
    "P": {
        "min": 20, "max": 100, "unidade": "mg/kg", "nome": "Fósforo",
        "acao_baixo": "Aplicar fertilizante fosfatado (superfosfato simples).",
        "acao_alto":  "Reduzir a adubação fosfatada e revisar o plano de nutrição.",
    },
    "K": {
        "min": 20, "max": 100, "unidade": "mg/kg", "nome": "Potássio",
        "acao_baixo": "Aplicar cloreto ou sulfato de potássio.",
        "acao_alto":  "Suspender a aplicação de potássio nesta área.",
    },
    "temperature": {
        "min": 15, "max": 35, "unidade": "°C", "nome": "Temperatura",
        "acao_baixo": "Proteger a cultura (cobertura/estufa) e adiar plantio se possível.",
        "acao_alto":  "Reforçar irrigação/sombreamento e irrigar nas horas mais frescas.",
    },
    "humidity": {
        "min": 40, "max": 90, "unidade": "%", "nome": "Umidade",
        "acao_baixo": "Acionar a irrigação imediatamente para repor a umidade do solo.",
        "acao_alto":  "Suspender a irrigação e verificar a drenagem (risco de fungos).",
    },
    "ph": {
        "min": 5.5, "max": 7.0, "unidade": "", "nome": "pH do solo",
        "acao_baixo": "Solo ácido: aplicar calcário (calagem) para corrigir o pH.",
        "acao_alto":  "Solo alcalino: aplicar enxofre/matéria orgânica para baixar o pH.",
    },
}

# Caminho padrão para o CSV de sensores da Fase 3
CSV_PADRAO = os.path.join(
    os.path.dirname(__file__), "..", "FASE3", "produtos_agricolas.csv"
)


# ---------------------------------------------------------------------------
# 2) LEITURA DO CSV DE SENSORES
# ---------------------------------------------------------------------------
def ler_leituras(caminho_csv):
    """Lê o CSV e devolve uma lista de dicionários (uma leitura por linha)."""
    leituras = []
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            leituras.append(linha)
    return leituras


# ---------------------------------------------------------------------------
# 3) VERIFICAÇÃO DAS REGRAS
# ---------------------------------------------------------------------------
def verificar_leitura(leitura):
    """Compara cada valor com a faixa ideal.

    Retorna duas listas paralelas: 'problemas' (o que está errado) e
    'acoes' (a ação corretiva recomendada para cada problema).
    """
    problemas = []
    acoes = []
    for chave, regra in FAIXAS_IDEAIS.items():
        if chave not in leitura or leitura[chave] in (None, ""):
            continue
        try:
            valor = float(leitura[chave])
        except ValueError:
            continue

        nome, unidade = regra["nome"], regra["unidade"]
        if valor < regra["min"]:
            problemas.append(
                f"{nome} BAIXO: {valor}{unidade} (ideal >= {regra['min']}{unidade})"
            )
            acoes.append(regra["acao_baixo"])
        elif valor > regra["max"]:
            problemas.append(
                f"{nome} ALTO: {valor}{unidade} (ideal <= {regra['max']}{unidade})"
            )
            acoes.append(regra["acao_alto"])
    return problemas, acoes


def montar_mensagem(indice, leitura, problemas, acoes):
    """Monta o texto do alerta (com ações corretivas) enviado por e-mail."""
    cultura = leitura.get("label", "n/d")
    momento = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linhas = [
        "ALERTA FarmTech Solutions - Leitura de sensor fora do padrao",
        "=" * 55,
        f"Data/hora......: {momento}",
        f"Leitura no.....: {indice}",
        f"Cultura (label): {cultura}",
        "",
        "Problemas detectados:",
    ]
    linhas += [f"  - {p}" for p in problemas]
    linhas += ["", "ACOES CORRETIVAS RECOMENDADAS (atencao, equipe de campo):"]
    linhas += [f"  {n}) {a}" for n, a in enumerate(acoes, start=1)]
    linhas += [
        "",
        "Valores lidos:",
        f"  N={leitura.get('N')} | P={leitura.get('P')} | K={leitura.get('K')}",
        f"  Temp={leitura.get('temperature')}C | Umidade={leitura.get('humidity')}% "
        f"| pH={leitura.get('ph')} | Chuva={leitura.get('rainfall')}mm",
        "",
        "-- Mensagem automatica enviada via Amazon SNS (infra AWS - Fase 5) --",
    ]
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# 4) ENVIO PELO AMAZON SNS
# ---------------------------------------------------------------------------
def enviar_sns(assunto, mensagem, topic_arn, regiao):
    """Publica a mensagem no tópico SNS. O SNS reenvia por e-mail aos inscritos."""
    cliente = boto3.client("sns", region_name=regiao)
    resposta = cliente.publish(
        TopicArn=topic_arn,
        Subject=assunto[:100],          # SNS limita o assunto a 100 caracteres
        Message=mensagem,
    )
    return resposta["MessageId"]


# ---------------------------------------------------------------------------
# 4b) PRÉVIA DO E-MAIL EM HTML (artefato para print, sem precisar da AWS)
# ---------------------------------------------------------------------------
def gerar_html(alertas, destino):
    """Gera um HTML simulando a caixa de e-mail com os alertas recebidos."""
    cartoes = []
    for assunto, mensagem in alertas:
        corpo = mensagem.replace("<", "&lt;").replace(">", "&gt;")
        cartoes.append(
            f"""
        <div class="email">
          <div class="head">
            <span class="de">Amazon SNS &lt;no-reply@sns.amazonaws.com&gt;</span>
            <span class="assunto">{assunto}</span>
          </div>
          <pre class="corpo">{corpo}</pre>
        </div>"""
        )
    html = f"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<title>FarmTech - Alertas (prévia)</title>
<style>
  body {{ font-family: Arial, sans-serif; background:#f0f2f5; padding:24px; }}
  h1 {{ color:#1a7f37; font-size:20px; }}
  .nota {{ color:#666; font-size:13px; margin-bottom:18px; }}
  .email {{ background:#fff; border:1px solid #d0d7de; border-radius:8px;
           margin-bottom:16px; overflow:hidden; }}
  .head {{ background:#1a7f37; color:#fff; padding:10px 14px; }}
  .de {{ display:block; font-size:12px; opacity:.85; }}
  .assunto {{ display:block; font-weight:bold; font-size:15px; }}
  .corpo {{ margin:0; padding:14px; white-space:pre-wrap; font-size:13px;
           color:#24292f; }}
</style></head><body>
  <h1>📬 Caixa de entrada do funcionário — FarmTech Solutions</h1>
  <p class="nota">Prévia dos alertas enviados pelo Amazon SNS (gerada localmente
  para demonstração; ao conectar uma conta AWS, e-mails idênticos chegam de verdade).</p>
  {''.join(cartoes)}
</body></html>"""
    with open(destino, "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# 5) PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Dispara alerta de sensor (Fase 3) via Amazon SNS."
    )
    parser.add_argument("--csv", default=CSV_PADRAO,
                        help="Caminho do CSV de sensores (padrao: Fase 3).")
    parser.add_argument("--simular", action="store_true",
                        help="Nao envia para a AWS; apenas mostra o alerta na tela.")
    parser.add_argument("--limite", type=int, default=0,
                        help="Quantas leituras analisar (0 = todas).")
    parser.add_argument("--saida", default="",
                        help="Salva os alertas (texto) no arquivo informado.")
    parser.add_argument("--html", default="",
                        help="Gera uma previa dos e-mails em HTML no arquivo informado.")
    args = parser.parse_args()

    topic_arn = os.environ.get("SNS_TOPIC_ARN", "")
    regiao = os.environ.get("AWS_REGION", "sa-east-1")  # São Paulo

    print("FarmTech Solutions - Monitor de sensores (Fase 3) + Amazon SNS")
    print(f"Arquivo de leituras: {os.path.abspath(args.csv)}")
    print(f"Regiao AWS.........: {regiao}")
    print(f"Topico SNS.........: {topic_arn or '(nao definido)'}")
    print(f"Modo...............: {'SIMULACAO' if args.simular else 'ENVIO REAL'}")
    print("-" * 60)

    leituras = ler_leituras(args.csv)
    if args.limite > 0:
        leituras = leituras[: args.limite]

    total_alertas = 0
    alertas = []  # guarda (assunto, mensagem) para gravar em arquivo/HTML
    for i, leitura in enumerate(leituras, start=1):
        problemas, acoes = verificar_leitura(leitura)
        if not problemas:
            continue  # Leitura saudável: nada a alertar

        total_alertas += 1
        cultura = leitura.get("label", "n/d")
        assunto = f"[FarmTech] Alerta sensor #{i} - cultura {cultura}"
        mensagem = montar_mensagem(i, leitura, problemas, acoes)
        alertas.append((assunto, mensagem))

        if args.simular:
            print(f"\n>>> (SIMULACAO) Alerta que SERIA enviado pelo SNS:\n")
            print(mensagem)
        else:
            if boto3 is None:
                sys.exit("ERRO: boto3 nao instalado. Rode: pip install boto3")
            if not topic_arn:
                sys.exit("ERRO: defina a variavel de ambiente SNS_TOPIC_ARN.")
            try:
                msg_id = enviar_sns(assunto, mensagem, topic_arn, regiao)
                print(f">>> Alerta #{i} enviado ao SNS. MessageId: {msg_id}")
            except (BotoCoreError, ClientError) as erro:
                print(f">>> Falha ao enviar alerta #{i}: {erro}")

    print("-" * 60)
    print(f"Leituras analisadas: {len(leituras)} | Alertas gerados: {total_alertas}")
    if total_alertas == 0:
        print("Todas as leituras estao dentro da faixa ideal. Nenhum alerta enviado.")

    # Artefatos opcionais (úteis para a entrega antes de ter conta AWS)
    if args.saida and alertas:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write("\n\n".join(m for _, m in alertas))
        print(f"Alertas salvos em texto: {os.path.abspath(args.saida)}")
    if args.html and alertas:
        gerar_html(alertas, args.html)
        print(f"Previa dos e-mails (HTML): {os.path.abspath(args.html)}")


if __name__ == "__main__":
    main()
