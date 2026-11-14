# ☁️ Encurtador de URL Serverless no Cloud Run

API de encurtamento de links rodando em **container no Google Cloud Run**, com dados no **Firestore** e deploy automático via **Cloud Build**.

## 🏗️ Arquitetura
```
Usuário ──HTTPS──► Cloud Run (Flask + Gunicorn) ──► Firestore (coleção "links")
                          ▲
GitHub push ──► Cloud Build ──► Artifact Registry ──┘ (deploy automático)
```

## 🔌 Endpoints
| Método | Rota | Descrição |
|---|---|---|
| POST | `/shorten` | Body `{"url": "https://..."}` e devolve o código curto |
| GET | `/<codigo>` | Redireciona para a URL original (e conta cliques) |
| GET | `/stats/<codigo>` | Mostra o número de cliques |
| GET | `/health` | Health check |

## 🧰 Tecnologias
Python · Flask · Docker · Cloud Run · Firestore · Cloud Build · Artifact Registry

## 🚀 Deploy passo a passo
```bash
export PROJECT_ID=seu-projeto
export REGION=southamerica-east1     # São Paulo

gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com firestore.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud firestore databases create --location=$REGION

# Deploy direto do código-fonte (o Cloud Build gera a imagem pelo Dockerfile)
gcloud run deploy url-shortener --source . --region $REGION --allow-unauthenticated
```

### CI/CD com Cloud Build
Crie antes o repositório de imagens:
```bash
gcloud artifacts repositories create apps --repository-format=docker --location=$REGION
```
Depois conecte este repositório em **Cloud Build → Triggers** e aponte para o `cloudbuild.yaml`. Cada push na `main` faz build e deploy.

## 🧪 Testando
```bash
URL=$(gcloud run services describe url-shortener --region $REGION --format 'value(status.url)')
curl -X POST $URL/shorten -H "Content-Type: application/json" -d '{"url":"https://cloud.google.com"}'
```

## 💸 Custos
Cloud Run escala a zero e o Firestore tem cota gratuita, então para estudos o custo tende a ser zero ou próximo disso.

## 📚 O que pratiquei
- Containers e serverless
- Banco NoSQL gerenciado
- CI/CD nativo do Google Cloud

## 🗺️ Próximos passos
- [ ] Domínio personalizado
- [ ] Autenticação com API key (API Gateway)
- [ ] Expiração de links
