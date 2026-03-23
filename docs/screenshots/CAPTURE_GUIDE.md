# Guide de capture des screenshots

Place les screenshots dans ce dossier (`docs/screenshots/`).
Taille recommandee : **1280x800** (ou fenetre navigateur standard).
Format : **PNG** (qualite) ou **WebP** (plus leger).

## 6 screenshots a capturer

### 1. `dashboard.png`
- Vue : Dashboard principal
- Contenu ideal : 2-3 vehicules avec stats (km, depenses, alertes)
- Montrer les cartes "Prochaines echeances" et "Consommation"
- Mode clair (light mode)

### 2. `upload.png`
- Vue : Onglet Documents d'un vehicule
- Contenu ideal : zone de drag-drop visible + un batch en cours (barre de progression)
- OU : les 3 boutons de type (Auto-detect, Facture, CT) bien visibles
- Montrer quelques documents deja importes en dessous

### 3. `chat.png`
- Vue : Onglet Chat
- Contenu ideal : une conversation avec 2-3 echanges
- Question utilisateur : "Quand ai-je fait la derniere vidange ?"
- Reponse de l'assistant avec des donnees structurees
- Montrer la sidebar des conversations a gauche

### 4. `fuel.png`
- Vue : Onglet Carburant d'un vehicule
- Contenu ideal : les 3 cartes resume (conso moyenne, total, nb pleins)
- Le graphique de consommation L/100km avec quelques points
- Quelques pleins dans la liste en dessous

### 5. `taxes.png`
- Vue : Onglet Taxes d'un vehicule
- Contenu ideal : 2-3 enregistrements avec badges de statut (vert, orange, rouge)
- Une assurance valide (vert), une vignette bientot echue (orange)

### 6. `sharing.png`
- Vue : Onglet Partage d'un vehicule
- Contenu ideal : 1-2 utilisateurs partages avec roles (editor, viewer)
- Le formulaire d'invitation visible

## Bonus : GIF anime

Si tu veux un GIF pour Reddit/HN, capture ce flow en 15 secondes :
1. Clic sur "Importer" → selection d'un PDF facture
2. Barre de progression de l'extraction
3. Resultat : le document extrait avec les donnees structurees
4. Switch vers le Chat → question → reponse

Outil recommande : [ScreenToGif](https://www.screentogif.com/) (Windows, gratuit)
Sauvegarder en `docs/screenshots/demo.gif` et ajouter au README :
```markdown
![Demo](docs/screenshots/demo.gif)
```
