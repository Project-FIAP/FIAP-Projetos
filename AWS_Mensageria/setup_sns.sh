#!/usr/bin/env bash
# ============================================================================
# Setup automatico do servico de mensageria (Amazon SNS) - FarmTech Solutions
# ----------------------------------------------------------------------------
# Cria o topico SNS e a assinatura de e-mail com UM comando.
# Use no AWS CloudShell (ja autenticado) ou com a AWS CLI configurada.
#
# Uso:
#   bash setup_sns.sh seu-email@exemplo.com
#
# Ao final, ele imprime o export do SNS_TOPIC_ARN para voce copiar.
# ============================================================================
set -e

EMAIL="${1:?Informe o e-mail. Ex: bash setup_sns.sh func@fazenda.com}"
REGIAO="${AWS_REGION:-us-east-2}"     # Ohio (ajuste se a conta usar outra)
TOPICO="alertas-farmtech"

echo ">> Criando topico SNS '$TOPICO' na regiao $REGIAO ..."
ARN=$(aws sns create-topic --name "$TOPICO" --region "$REGIAO" --output text --query TopicArn)
echo ">> Topico criado: $ARN"

echo ">> Criando assinatura de e-mail para $EMAIL ..."
aws sns subscribe \
  --topic-arn "$ARN" \
  --protocol email \
  --notification-endpoint "$EMAIL" \
  --region "$REGIAO" >/dev/null
echo ">> Pronto! Verifique a caixa de $EMAIL e clique em 'Confirm subscription'."

echo
echo "============================================================"
echo "Agora rode o monitor com:"
echo "  export SNS_TOPIC_ARN=\"$ARN\""
echo "  export AWS_REGION=\"$REGIAO\""
echo "  python alerta_sensor_sns.py"
echo "============================================================"
