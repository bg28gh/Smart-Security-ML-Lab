# Smart Security: AI-Driven Cybersecurity Lab 🛡️🤖

This repository contains a suite of advanced security tools developed during the **Smart Security Lab** at **Technische Universität Berlin**. The projects focus on the application of Machine Learning and Deep Learning to detect, analyze, and mitigate cyber threats.

## 🚀 Projects Overview

### 📧 [Spam & Phishing Detection](./spam_detection.py)
* **Goal:** Identifying malicious emails using NLP.
* **Implementation:** Multinomial Naive Bayes with **TF-IDF vectorization**.
* **Key Features:** Automated feature engineering (uppercase ratio, URL detection) and hyperparameter tuning via **GridSearchCV**.

### 🔍 [Malicious Code Predictor](./malicious_code_predictor.py)
* **Goal:** Classifying PDF files as benign or malware based on metadata and content.
* **Implementation:** **Logistic Regression** trained on features extracted from PDF metadata (authors, producers) and semantic analysis.
* **Tech:** Uses `PyMuPDF (fitz)` for forensic PDF analysis.

### 🧬 [Malicious Code Clustering](./clustering_malicious_code.py)
* **Goal:** Unsupervised grouping of malware families without prior labeling.
* **Implementation:** **DBSCAN Clustering** algorithm.
* **Key Features:** Automated cluster discovery and evaluation using **Silhouette Scores** and Adjusted Rand Index (ARI).

### 🌐 [Tor Website Fingerprinting](./tor_website_fingerprinting.py)
* **Goal:** Identifying visited websites over the Tor network by analyzing encrypted traffic patterns.
* **Implementation:** **Random Forest Classifier** trained on network flow features.
* **Key Features:** Feature extraction from traffic captures, including packet timing, sizes, and multilayer encryption patterns.

### 🚨 [Detection of Unknown Attacks (NIDS)](./detection_unknown_attacks.py)
* **Goal:** Network Intrusion Detection System (NIDS) for "Zero-Day" attack discovery.
* **Implementation:** **Isolation Forest** (Anomaly Detection).
* **Key Features:** Real-time packet analysis using `Scapy` to identify statistical outliers in network sessions (duration, packet count, total size).

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **AI/ML:** `Scikit-learn`, `TensorFlow`, `NumPy`, `Pandas`.
* **Security & Network:** `Scapy`, `PyShark`, `PyMuPDF (fitz)`.

---

## ⚠️ Important Note on Implementation
**Due to Non-Disclosure Agreements (NDA) and the significant size of the original datasets, this repository contains only the core source code and model architectures.** The training data, PCAP files, and testing environments used in the lab are not included. The scripts provided demonstrate the feature engineering logic, statistical methodologies, and machine learning implementations used throughout the research.

---
*Developed at TU Berlin, 2024.*
