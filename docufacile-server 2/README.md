# DocuFacile — Serveur de conversion

Site de conversion de documents avec conversions haute fidélité :

- **Word → PDF** : LibreOffice (rendu quasi identique à l'original — polices, tableaux, en-têtes, images)
- **PDF → Word** : pdf2docx (conserve la mise en page, les tableaux et les images)
- Fusion, découpage et Images → PDF restent traités **dans le navigateur** (rapides et privés)

Si le serveur est injoignable, le site bascule automatiquement en mode « navigateur seul » (qualité réduite).

## Structure

```
docufacile-server/
├── app.py              # API Flask (2 endpoints de conversion)
├── static/index.html   # Le site complet (frontend)
├── requirements.txt
├── Dockerfile          # Image avec LibreOffice inclus
└── README.md
```

## Lancer en local

Prérequis : Python 3.10+, LibreOffice installé (`soffice` dans le PATH).

```bash
cd docufacile-server
pip install -r requirements.txt
python app.py
```

Puis ouvrez http://localhost:8000

### Ou avec Docker (recommandé — LibreOffice inclus)

```bash
docker build -t docufacile .
docker run -p 8000:8000 docufacile
```

## Déployer en ligne (gratuit pour commencer)

### Render.com

1. Poussez ce dossier sur un dépôt GitHub
2. Sur [render.com](https://render.com) : **New → Web Service** → connectez le dépôt
3. Environnement : **Docker** (détecté automatiquement grâce au Dockerfile)
4. Plan **Free** pour tester (le service s'endort après 15 min d'inactivité ; passez au plan payant ~7 $/mois pour un service permanent)

### Railway.app

1. Poussez sur GitHub
2. [railway.app](https://railway.app) : **New Project → Deploy from GitHub repo**
3. Le Dockerfile est détecté automatiquement

## API

| Endpoint            | Méthode | Corps                  | Réponse   |
|---------------------|---------|------------------------|-----------|
| `/api/word-to-pdf`  | POST    | `file` (.docx/.doc/.odt/.rtf/.txt) | PDF |
| `/api/pdf-to-word`  | POST    | `file` (.pdf)          | DOCX      |
| `/api/health`       | GET     | —                      | JSON      |

Limite : 50 Mo par fichier (modifiable dans `app.py`).

## Notes

- Les PDF scannés (images) ne contiennent pas de texte : PDF → Word nécessiterait de l'OCR (piste d'évolution : `ocrmypdf` avant conversion).
- Pour un rendu Word → PDF optimal, ajoutez au Dockerfile les polices utilisées dans vos documents (ex. `fonts-crosextra-carlito` pour un équivalent de Calibri).
