# ============================================================================
# Setup automatico do servico de mensageria (Amazon SNS) - FarmTech Solutions
# ----------------------------------------------------------------------------
# Cria o topico SNS e a assinatura de e-mail com UM comando (Windows).
# Requer a AWS CLI instalada e configurada (aws configure).
#
# Uso:
#   .\setup_sns.ps1 -Email "func@fazenda.com"
# ============================================================================
param(
    [Parameter(Mandatory = $true)] [string]$Email,
    [string]$Regiao = "us-east-2",      # Ohio (ajuste se a conta usar outra)
    [string]$Topico = "alertas-farmtech"
)

Write-Host ">> Criando topico SNS '$Topico' na regiao $Regiao ..."
$Arn = aws sns create-topic --name $Topico --region $Regiao --output text --query TopicArn
Write-Host ">> Topico criado: $Arn"

Write-Host ">> Criando assinatura de e-mail para $Email ..."
aws sns subscribe --topic-arn $Arn --protocol email --notification-endpoint $Email --region $Regiao | Out-Null
Write-Host ">> Pronto! Verifique a caixa de $Email e clique em 'Confirm subscription'."

Write-Host ""
Write-Host "============================================================"
Write-Host "Agora rode o monitor com:"
Write-Host "  `$env:SNS_TOPIC_ARN = `"$Arn`""
Write-Host "  `$env:AWS_REGION = `"$Regiao`""
Write-Host "  python alerta_sensor_sns.py"
Write-Host "============================================================"
