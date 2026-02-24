# 📡 TeleIQ – AI Powered Telecom Tutor Bot

TeleIQ is an AI-driven telecom training assistant that transforms static telecom documents into an interactive learning platform. It uses semantic search and vector embeddings to generate contextual quizzes and track staff learning progress.

---

## 🚀 Overview

Telecom staff must understand complex topics like data plans, roaming policies, FUP rules, and billing systems. Traditional document-based training is static and difficult to retain.

TeleIQ solves this by:

- Converting telecom documents into embeddings  
- Storing them in a vector database  
- Retrieving knowledge semantically  
- Generating quizzes  
- Providing explanations  
- Tracking learning progress  

---

## 🏗️ Architecture

- **Frontend:** Streamlit  
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)  
- **Vector DB:** FAISS  
- **Backend:** Python  
- **Progress Tracking:** Pandas  

The system follows a Retrieval-Augmented Learning approach.

---

## 👥 User Roles

### 🔐 Admin
- Upload telecom documents  
- Manage training content  

### 👩‍💻 Staff
- Dynamic login  
- Attempt quizzes  
- View progress dashboard  

---

## ✨ Features

- Role-based access (Admin / Staff)  
- Admin-only document upload  
- Semantic search using FAISS  
- Topic-based quiz generation  
- Contextual explanations  
- Learning progress dashboard  
- Clean minimal UI  

---
