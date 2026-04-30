# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

## IA_Underground

## 👨‍🎓 Integrantes: 

- <a href="https://www.linkedin.com/in/marlonmarinho/">Marlon Paulino Marinho</a>
- <a href="https://www.linkedin.com/in/pedro-carvalho-cea-149658137/">Pedro Carvalho Rocha Lima</a> 
- <a href="https://www.linkedin.com/in/vinigama">Vinicius de Santana Gama</a>

# Projeto Fase 6 - Visão Computacional com YOLO

## Sobre o Projeto

Este projeto foi desenvolvido para a **Fase 6 da FIAP**, com o objetivo de aplicar conceitos de **Redes Neurais** e **Visão Computacional** utilizando o modelo **YOLO** para detecção de objetos em imagens.

O desafio proposto consistiu em construir uma base de dados própria, rotular imagens manualmente e treinar um modelo capaz de identificar dois objetos distintos.

Neste projeto, os objetos escolhidos foram:

- Banana
- Apple (Maçã)

---

## Objetivo

Treinar um modelo de Inteligência Artificial capaz de reconhecer bananas e maçãs em imagens, comparando diferentes configurações de treinamento e avaliando a performance obtida.

---

## Tecnologias Utilizadas

- Python
- Google Colab
- YOLOv5
- MakeSense AI
- Google Drive
- GitHub

---

## Estrutura do Dataset

Foram utilizadas **80 imagens no total**, sendo:

- 40 imagens de Banana
- 40 imagens de Apple

Cada classe foi dividida em:

| Tipo | Quantidade |
|------|------------|
| Treino | 32 |
| Validação | 4 |
| Teste | 4 |

---

## Rotulação das Imagens

As imagens foram rotuladas manualmente utilizando a plataforma **MakeSense AI**, gerando arquivos no formato YOLO para treinamento supervisionado.

---

## Treinamento do Modelo

Foram realizados testes com diferentes quantidades de épocas para comparar desempenho:

- 30 épocas
- 60 épocas

Durante os treinamentos foram analisados:

- Precisão
- Loss
- Tempo de treinamento
- Qualidade das detecções

---

## Resultados

O modelo demonstrou capacidade de identificar corretamente bananas em imagens nunca vistas anteriormente, validando o uso da arquitetura YOLO em bases personalizadas.

Os resultados completos, métricas e prints das predições estão disponíveis no notebook do projeto.

---

## Notebook Completo

Acesse o notebook com todo o passo a passo, código e análises:

**(https://colab.research.google.com/drive/17Hr5VUt_QfyA_7Q2z_-0FCRyp8akHVv4#scrollTo=5gfQTRPGYQxf)**

---

## Vídeo Demonstrativo

Vídeo de apresentação com até 5 minutos mostrando o funcionamento do projeto:

**(https://youtu.be/Q259cmu6Rg4)**


## Considerações Finais

Este projeto permitiu aplicar na prática conceitos de:

- Deep Learning
- Redes Neurais Convolucionais
- Detecção de Objetos
- Preparação de Dataset
- Treinamento de Modelos de IA

Além disso, reforçou a importância da qualidade dos dados e da rotulação correta para o sucesso de soluções em Visão Computacional.