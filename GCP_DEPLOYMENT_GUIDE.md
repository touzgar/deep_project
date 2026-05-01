# 🌐 Guide de Déploiement sur Google Cloud Platform (GCP)

## Prérequis

Avant de commencer, vous aurez besoin de:
- Un compte Google Cloud Platform
- Carte de crédit (pour activer le compte, mais vous aurez $300 de crédits gratuits)
- Google Cloud SDK installé sur votre machine

---

## Étape 1: Créer un Projet GCP

### 1.1 Via Console Web
1. Allez sur: https://console.cloud.google.com/
2. Cliquez sur le sélecteur de projet en haut
3. Cliquez sur "Nouveau projet"
4. Nom du projet: `attendance-system-prod`
5. Notez l'ID du projet (ex: `attendance-system-prod-123456`)

### 1.2 Via CLI
```bash
# Créer le projet
gcloud projects create attendance-system-prod --name="Attendance System"

# Définir comme projet par défaut
gcloud config set project attendance-system-prod
```

---

## Étape 2: Activer les APIs Nécessaires

```bash
# Activer GKE (Google Kubernetes Engine)
gcloud services enable container.googleapis.com

# Activer GCR (Google Container Registry)
gcloud services enable containerregistry.googleapis.com

# Activer Cloud Storage
gcloud services enable storage.googleapis.com

# Activer Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Activer Cloud Logging
gcloud services enable logging.googleapis.com
```

---

## Étape 3: Installer Google Cloud SDK

### Windows:
1. Téléchargez: https://cloud.google.com/sdk/docs/install
2. Exécutez l'installateur
3. Suivez les instructions

### Linux/Mac:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Vérifier l'installation:
```bash
gcloud version
```

---

## Étape 4: Authentification

```bash
# Se connecter à GCP
gcloud auth login

# Configurer le projet
gcloud config set project [VOTRE-PROJECT-ID]

# Configurer la région (choisissez la plus proche)
gcloud config set compute/region europe-west1
gcloud config set compute/zone europe-west1-b

# Vérifier la configuration
gcloud config list
```

---

## Étape 5: Build et Push des Images vers GCR

### 5.1 Configurer Docker pour GCR
```bash
gcloud auth configure-docker
```

### 5.2 Build et Push Backend
```bash
cd backend

# Build l'image
docker build -t gcr.io/[PROJECT-ID]/attendance-backend:latest .

# Push vers GCR
docker push gcr.io/[PROJECT-ID]/attendance-backend:latest
```

### 5.3 Build et Push Frontend
```bash
cd frontend

# Build l'image
docker build -t gcr.io/[PROJECT-ID]/attendance-frontend:latest \
  --build-arg VITE_API_URL=http://[VOTRE-IP-EXTERNE]/api/v1 .

# Push vers GCR
docker push gcr.io/[PROJECT-ID]/attendance-frontend:latest
```

---

## Étape 6: Créer le Cluster Kubernetes (GKE)

### 6.1 Créer le cluster
```bash
gcloud container clusters create attendance-cluster \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --region=europe-west1 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=5 \
  --enable-autorepair \
  --enable-autoupgrade
```

**Note:** Cela prendra 5-10 minutes

### 6.2 Connecter kubectl au cluster
```bash
gcloud container clusters get-credentials attendance-cluster \
  --region=europe-west1
```

### 6.3 Vérifier la connexion
```bash
kubectl get nodes
```

---

## Étape 7: Mettre à Jour les Fichiers Kubernetes

### 7.1 Mettre à jour les images dans les deployments

Éditez `k8s/backend-deployment.yaml`:
```yaml
spec:
  containers:
  - name: backend
    image: gcr.io/[PROJECT-ID]/attendance-backend:latest
```

Éditez `k8s/frontend-deployment.yaml`:
```yaml
spec:
  containers:
  - name: frontend
    image: gcr.io/[PROJECT-ID]/attendance-frontend:latest
```

### 7.2 Mettre à jour les secrets

Éditez `k8s/secrets.yaml` avec vos vraies valeurs:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: attendance-system
type: Opaque
stringData:
  DATABASE_URL: "postgresql://neondb_owner:npg_hMtrjxz9qA5C@ep-green-pine-anw2pzja-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"
  SECRET_KEY: "67aa5288c88bf4499d778514fc114d79e9dfda01dac601cb15cd88f9194e78de"
  POSTGRES_PASSWORD: "TvWeIamunxz9B+pEV6g4O7h0rd4GGk4+zxVVLTQF0g4="
```

---

## Étape 8: Déployer sur GKE

### 8.1 Créer le namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### 8.2 Créer les secrets et configmaps
```bash
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
```

### 8.3 Créer les volumes
```bash
kubectl apply -f k8s/postgres-pvc.yaml
```

### 8.4 Déployer les applications
```bash
# Déployer PostgreSQL (si vous n'utilisez pas Neon)
kubectl apply -f k8s/postgres-deployment.yaml

# Déployer Backend
kubectl apply -f k8s/backend-deployment.yaml

# Déployer Frontend
kubectl apply -f k8s/frontend-deployment.yaml
```

### 8.5 Créer les services
```bash
kubectl apply -f k8s/ingress.yaml
```

### 8.6 Configurer l'autoscaling
```bash
kubectl apply -f k8s/hpa.yaml
```

---

## Étape 9: Vérifier le Déploiement

### 9.1 Vérifier les pods
```bash
kubectl get pods -n attendance-system
```

Vous devriez voir:
```
NAME                                  READY   STATUS    RESTARTS   AGE
attendance-backend-xxx                1/1     Running   0          2m
attendance-frontend-xxx               1/1     Running   0          2m
```

### 9.2 Vérifier les services
```bash
kubectl get services -n attendance-system
```

### 9.3 Obtenir l'IP externe
```bash
kubectl get ingress -n attendance-system
```

Attendez que l'IP externe soit assignée (peut prendre 5-10 minutes)

---

## Étape 10: Accéder à l'Application

Une fois l'IP externe assignée:

1. **Frontend**: http://[IP-EXTERNE]
2. **Backend API**: http://[IP-EXTERNE]/api/v1

---

## Étape 11: Configurer le Monitoring

### 11.1 Activer Cloud Monitoring
```bash
gcloud services enable monitoring.googleapis.com
```

### 11.2 Voir les logs
```bash
# Logs du backend
kubectl logs -f deployment/attendance-backend -n attendance-system

# Logs du frontend
kubectl logs -f deployment/attendance-frontend -n attendance-system
```

### 11.3 Accéder au Dashboard GCP
1. Allez sur: https://console.cloud.google.com/
2. Menu → Kubernetes Engine → Workloads
3. Cliquez sur votre déploiement pour voir les métriques

---

## Étape 12: Configurer un Domaine (Optionnel)

### 12.1 Réserver une IP statique
```bash
gcloud compute addresses create attendance-ip --global
```

### 12.2 Obtenir l'IP
```bash
gcloud compute addresses describe attendance-ip --global
```

### 12.3 Configurer votre DNS
Ajoutez un enregistrement A pointant vers cette IP

### 12.4 Mettre à jour l'ingress
Éditez `k8s/ingress.yaml`:
```yaml
spec:
  rules:
  - host: votre-domaine.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

Appliquez:
```bash
kubectl apply -f k8s/ingress.yaml
```

---

## Commandes Utiles

### Voir les ressources
```bash
kubectl get all -n attendance-system
```

### Redémarrer un déploiement
```bash
kubectl rollout restart deployment/attendance-backend -n attendance-system
```

### Scaler manuellement
```bash
kubectl scale deployment/attendance-backend --replicas=5 -n attendance-system
```

### Voir les événements
```bash
kubectl get events -n attendance-system --sort-by='.lastTimestamp'
```

### Accéder à un pod
```bash
kubectl exec -it [POD-NAME] -n attendance-system -- /bin/bash
```

---

## Coûts Estimés

Avec la configuration par défaut (3 nodes e2-medium):
- **Cluster GKE**: ~$150/mois
- **Load Balancer**: ~$20/mois
- **Stockage**: ~$5/mois
- **Total**: ~$175/mois

**Note**: Vous avez $300 de crédits gratuits pour commencer!

---

## Nettoyage (Pour éviter les frais)

### Supprimer le cluster
```bash
gcloud container clusters delete attendance-cluster --region=europe-west1
```

### Supprimer les images
```bash
gcloud container images delete gcr.io/[PROJECT-ID]/attendance-backend:latest
gcloud container images delete gcr.io/[PROJECT-ID]/attendance-frontend:latest
```

### Supprimer le projet
```bash
gcloud projects delete [PROJECT-ID]
```

---

## Troubleshooting

### Les pods ne démarrent pas
```bash
kubectl describe pod [POD-NAME] -n attendance-system
kubectl logs [POD-NAME] -n attendance-system
```

### Problème d'image
```bash
# Vérifier que l'image existe dans GCR
gcloud container images list

# Vérifier les permissions
gcloud projects get-iam-policy [PROJECT-ID]
```

### Problème de connexion à la base de données
```bash
# Tester depuis un pod
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -- psql [DATABASE_URL]
```

---

## Informations Importantes à Fournir

Pour compléter le déploiement, j'ai besoin de:

1. **Project ID GCP**: Quel ID voulez-vous utiliser?
2. **Région**: Où voulez-vous déployer? (europe-west1, us-central1, etc.)
3. **Domaine**: Avez-vous un nom de domaine? (optionnel)
4. **Budget**: Quel est votre budget mensuel?

---

**Prêt à déployer sur GCP?** Donnez-moi ces informations et je vous guiderai étape par étape! 🚀
