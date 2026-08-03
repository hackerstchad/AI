# 🛡️ CHADSECURE v2.0.0 — CENTRE DE CYBERSÉCURITÉ ÉTHIQUE & ÉDUCATIF

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&duration=3000&pause=1000&color=00F7FF&center=true&vCenter=true&width=800&lines=CHADSECURE;Centre+de+Cybersécurité+Éthique;Plus+de+1000+menus;Simulation+%C3%A9ducative+avancée;Hacker+Tchadien+%F0%9F%87%B9%F0%9F%87%AC" alt="Typing SVG" />
</p>

<p align="center">
  <a href="#installation"><img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="#modules"><img src="https://img.shields.io/badge/Menus-1000%2B-success?style=for-the-badge"></a>
  <a href="#ethique"><img src="https://img.shields.io/badge/Éthique-100%25-red?style=for-the-badge"></a>
  <a href="#licence"><img src="https://img.shields.io/badge/Licence-MIT-yellow?style=for-the-badge"></a>
</p>

---

## 🌍 Présentation

**CHADSECURE** est un simulateur éducatif de cybersécurité avancé, créé par **Hacker Tchadien 🇹🇩**.  
Il regroupe **plus de 1000 menus et options** répartis en **modules thématiques**, avec un style proche des outils professionnels de cybersécurité, mais **100% simulé et éthique**.

> 🎯 Objectif : apprendre, s'entraîner, auditer ses propres systèmes et sensibiliser aux bonnes pratiques de sécurité.

---

## ⚠️ Avertissement Légal & Éthique

```diff
- CE LOGICIEL EST UN SIMULATEUR ÉDUCATIF.
- AUCUNE ATTAQUE RÉELLE N'EST EFFECTUÉE.
- AUCUNE SURVEILLANCE D'INDIVIDU N'EST POSSIBLE.
- AUCUNE EXTRACTION DE DONNÉES PRIVÉES N'EST RÉALISÉE.
```

**Utilisez CHADSECURE uniquement :**
- Sur vos propres machines et réseaux.
- Dans des environnements de labo autorisés.
- Pour des CTF (Capture The Flag) légaux.
- Pour de la sensibilisation et de la formation.

L'auteur décline **toute responsabilité** en cas d'usage malveillant ou illégal.

---

## 📦 Installation

### Prérequis

- Python 3.8 ou supérieur
- Terminal supportant Unicode et les couleurs (recommandé)

### Étapes

```bash
# Cloner ou copier le projet
cd chadsecure

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer CHADSECURE
python3 chadsecure.py
```

---

## 🚀 Utilisation

### Mode interactif

```bash
python3 chadsecure.py
```

Puis naviguez dans les menus avec les chiffres.

### Mode ligne de commande (CLI)

```bash
# Exemple : lancer un scan TCP SYN simulé sur 127.0.0.1
python3 chadsecure.py --module 2 --option 1 --target 127.0.0.1
```

| Argument | Description |
|----------|-------------|
| `--module` | Numéro du module (1-17) |
| `--option` | Numéro de l'option dans le module |
| `--target` | Cible : IP, domaine, URL ou `localhost` |

---

## 📂 Modules & Menus (1000+)

CHADSECURE propose **17 modules principaux** avec **15 options chacun**, soit **255 options de base**.  
Chaque option déclenche une **simulation avancée** avec sous-étapes, barres de progression et résultats fictifs.

> 💡 Pour atteindre **1000+ menus documentés**, CHADSECURE intègre des sous-menus contextuels, des rapports dynamiques, des générateurs de règles, des scénarios de sensibilisation et des options d'export.

### Tableau des modules

| # | Module | Options | Description |
|---|--------|---------|-------------|
| 01 | Reconnaissance Éthique | 15 | WHOIS, DNS, sous-domaines, OSINT légal |
| 02 | Scan & Énumération | 15 | Scan de ports, énumération services, audit SSH/SSL |
| 03 | Tests Web | 15 | Détection XSS, SQLi, headers, JWT, API |
| 04 | Exploitation (Simulation) | 15 | Démonstrations éducatives de CVE célèbres |
| 05 | Post-Exploitation (Simulation) | 15 | Mouvement latéral, persistance, exfiltration (fictif) |
| 06 | Réseau & MITM (Simulation) | 15 | ARP, DNS, sniffing, rogue AP (démo) |
| 07 | Cryptographie | 15 | Encodages, hashes, chiffrements, JWT |
| 08 | OSINT Légal | 15 | Recherche d'informations publiques uniquement |
| 09 | Défense & Blue Team | 15 | SIEM, YARA, Sigma, threat hunting |
| 10 | Forensique (Simulation) | 15 | Analyse mémoire, fichiers, métadonnées |
| 11 | Réponse à Incident | 15 | Triage, containment, recovery, RCA |
| 12 | Outils Divers | 15 | Rapports, exports, session, configuration |
| 13 | Sensibilisation Ingénierie Sociale | 15 | Phishing, vishing, pretexting (formation) |
| 14 | Cloud Security | 15 | AWS, Azure, GCP, Kubernetes, containers |
| 15 | IA & Automatisation Sécurisée | 15 | Prompt injection, LLM security, RAG |
| 16 | Protection Données Personnelles | 15 | GDPR, privacy, consentement, anonymisation |
| 17 | Sécurité Mobile | 15 | APK, IPA, permissions, secrets, rooting |

**Total options de base : 255**  
**Avec sous-menus et générateurs dynamiques : 1000+ interactions**

### Détail des 1000+ menus (17 modules × 15 options × ~4 sous-actions)

Chaque option génère automatiquement jusqu'à **4 sous-menus contextuels** :
1. **Configuration** — choisir les paramètres de simulation
2. **Exécution** — lancer la simulation avec barres de progression
3. **Analyse** — interpréter les résultats fictifs
4. **Export** — sauvegarder le résultat dans le journal

Exemple pour **Module 01 — Reconnaissance Éthique** :

| Option | Sous-menus générés |
|--------|-------------------|
| WHOIS Lookup | Config → Exécuter → Analyser → Exporter |
| Reverse DNS | Config → Exécuter → Analyser → Exporter |
| DNS Enumeration | Config → Exécuter → Analyser → Exporter |
| Subdomain Discovery | Config → Exécuter → Analyser → Exporter |
| Certificate Transparency | Config → Exécuter → Analyser → Exporter |
| IP Geolocation | Config → Exécuter → Analyser → Exporter |
| ASN Lookup | Config → Exécuter → Analyser → Exporter |
| BGP Analysis | Config → Exécuter → Analyser → Exporter |
| Shodan-style Search | Config → Exécuter → Analyser → Exporter |
| Censys-style Search | Config → Exécuter → Analyser → Exporter |
| Google Dorking | Config → Exécuter → Analyser → Exporter |
| GitHub OSINT | Config → Exécuter → Analyser → Exporter |
| Social Media Footprint | Config → Exécuter → Analyser → Exporter |
| Metadata Analyzer | Config → Exécuter → Analyser → Exporter |
| Email Format Finder | Config → Exécuter → Analyser → Exporter |

> **15 options × 4 sous-menus = 60 interactions par module.**  
> **17 modules × 60 = 1020 menus dynamiques.**  

Les modules **12 (Outils Divers)**, **09 (Blue Team)** et **11 (Réponse à Incident)** incluent des générateurs de rapports qui produisent chacun **10+ variantes** supplémentaires.


---

## 🎨 Génération d'Images Gratuites avec l'IA

Voici une sélection d'outils d'IA gratuits pour générer des visuels promotionnels pour CHADSECURE :

| Outil | Lien | Type |
|-------|------|------|
| Leonardo.AI | https://leonardo.ai | Images / illustrations |
| Bing Image Creator | https://www.bing.com/create | Images DALL·E 3 gratuites |
| Canva AI | https://www.canva.com/ai-image-generator | Design + IA |
| Playground AI | https://playgroundai.com | Images stylisées |
| Ideogram | https://ideogram.ai | Texte dans l'image |
| Clipdrop (Stability AI) | https://clipdrop.co | Suite IA image |
| Craiyon | https://www.craiyon.com | Gratuit, illimité |
| Adobe Firefly | https://firefly.adobe.com | Génération éthique |
| NightCafe | https://nightcafe.studio | Communautaire |
| StarryAI | https://starryai.com | Mobile + desktop |

### Prompts suggérés pour CHADSECURE

```
"Futuristic cybersecurity command center with Chad flag colors,
 holographic interface, ethical hacker, neon blue and green, cinematic"
```

```
"African cyber defense agency logo, shield with digital circuits,
 Chad flag, professional, minimalist, dark background"
```

```
"Hacker tchadien éthique, terminal screen, Africa tech, cyberpunk,
 blue cyan glow, high tech operations room"
```

---

## ✨ Fonctionnalités Avancées

- 🖥️ **Interface terminal stylisée** avec bannière ASCII
- 🌈 **Couleurs dynamiques** via `colorama`
- 📊 **Barres de progression** via `tqdm`
- ✅ **Validation éthique** : confirmation de propriété de la cible
- 📝 **Journal de session** complet
- 📤 **Export JSON / CSV** des rapports
- ⚡ **Mode CLI** pour automatisation
- 🧠 **Simulations intelligentes** avec résultats aléatoires réalistes
- 🔒 **Aucune donnée privée** n'est collectée ou traitée
- 🌍 **Multilingue prêt** (actuellement en français)

---

## 🛠️ Stack Technique

| Technologie | Usage |
|-------------|-------|
| Python 3.8+ | Langage principal |
| colorama | Couleurs terminal |
| tqdm | Barres de progression |
| pyfiglet | Bannières ASCII |
| requests | Requêtes HTTP optionnelles |
| argparse | Mode ligne de commande |

---

## 📚 Ressources & Crédits

### Auteur

- **Hacker Tchadien 🇹🇩** — Créateur, architecte et développeur principal de CHADSECURE.

### Inspirations & Crédits

- Frameworks de pentesting éthique : Metasploit, Nmap, Burp Suite, OWASP
- Communauté cybersécurité africaine
- Labs éducatifs : Hack The Box, TryHackMe, PortSwigger Academy
- Standards : NIST, ISO 27001, GDPR, OWASP Top 10, MITRE ATT&CK

### IA Générative & Création de Contenu

| Outil | Lien | Usage |
|-------|------|-------|
| ChatGPT | https://chat.openai.com | Assistant IA, génération de docs |
| Claude | https://claude.ai | Assistant IA avancé |
| Gemini | https://gemini.google.com | IA multimodale Google |
| Perplexity | https://www.perplexity.ai | Recherche IA |
| Hugging Face | https://huggingface.co | Modèles open-source IA |
| Replicate | https://replicate.com | Exécution de modèles IA |
| Runway ML | https://runwayml.com | Vidéo IA |
| Pika Labs | https://pika.art | Vidéo IA |
| Midjourney | https://www.midjourney.com | Images artistiques IA |
| Stable Diffusion | https://stability.ai | Images IA open-source |

### Outils recommandés pour aller plus loin

| Catégorie | Outil | Lien |
|-----------|-------|------|
| Pentest | Kali Linux | https://www.kali.org |
| Labs | Hack The Box | https://www.hackthebox.com |
| Labs | TryHackMe | https://tryhackme.com |
| Web | PortSwigger Academy | https://portswigger.net/web-security |
| OSINT | OSINT Framework | https://osintframework.com |
| Blue Team | Splunk Boss of the SOC | https://bots.splunk.com |
| Threat Intel | MITRE ATT&CK | https://attack.mitre.org |
| Cloud | Prowler | https://prowler.cloud |
| Mobile | MobSF | https://mobsf.github.io |
| IA | OWASP LLM Top 10 | https://llmtop10.com |

---

## 🖼️ Badges & Visuels

Générez des badges pour votre fork :

```markdown
![CHADSECURE](https://img.shields.io/badge/CHADSECURE-v2.0.0-00F7FF)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Menus](https://img.shields.io/badge/Menus-1000%2B-success)
![Éthique](https://img.shields.io/badge/Éthique-100%25-red)
```

---

## 🤝 Contribution

Les contributions éducatives sont les bienvenues :

1. Forkez le projet.
2. Créez une branche `feature/...`.
3. Soumettez une Pull Request.

**Aucun code malveillant ou destiné à attaquer des tiers ne sera accepté.**

---

## 📜 Licence

```
MIT License

Copyright (c) 2024 Hacker Tchadien

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 📞 Contact & Communauté

- 🐦 Twitter/X : `@HackerTchadien` *(exemple)*
- 💬 Telegram : `CHADSECURE_Community` *(exemple)*
- 📧 Email : `contact@chadsecure.td` *(exemple)*
- 🌐 Site web : `https://chadsecure.td` *(exemple)*

> 🇹🇩 *Fièrement conçu au Tchad pour la cybersécurité africaine.*

---

## 🎯 Feuille de Route (Roadmap)

- [x] 17 modules principaux
- [x] 255 options de base
- [x] 1000+ menus dynamiques documentés
- [x] Mode CLI avancé
- [x] Export JSON/CSV
- [ ] Mode graphique web (Flask/Streamlit)
- [ ] Intégration de labs Docker
- [ ] Multilingue complet (FR/EN/AR)
- [ ] Certification éducative CHADSECURE

---

## 🏆 Remerciements

Un grand merci à :
- La communauté cybersécurité africaine
- Les mentors et formateurs en cybersécurité
- Les contributeurs open-source
- Les organisations promouvant la cybersécurité éthique

**CHADSECURE est un projet communautaire. Merci de l'utiliser de manière responsable.**

---

<p align="center">
  <strong>CHADSECURE — Apprendre. Tester. Sécuriser.</strong>
</p>
