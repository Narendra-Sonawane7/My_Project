# 📰 AI News Classifier — Powered by Machine Learning

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?style=for-the-badge&logo=scikit-learn)
![NLP](https://img.shields.io/badge/NLP-TF--IDF-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> A Machine Learning powered **News Classification API** built with **Flask** and **Naive Bayes**. It classifies any news text into categories like Sports, Technology, Politics, Science and more — instantly!

---

## 📌 Features

- ✅ Classifies news text into **20 categories**
- ✅ Trained on **20 Newsgroups dataset** (scikit-learn)
- ✅ **TF-IDF Vectorization** for text processing
- ✅ **Naive Bayes** classification model
- ✅ REST API built with Flask
- ✅ Supports both **JSON API** and **Web Form** input
- ✅ Pre-trained model saved with `pickle`

---

## 🗂️ Project Structure

```
news-classifier/
│
├── app.py               # Flask API — main application
├── model.py             # Model loading & prediction logic
├── train.py             # Model training script
├── test.py              # API testing script
├── requirements.txt     # Python dependencies
├── model.pkl            # Trained ML model (generated after training)
├── vectorizer.pkl       # TF-IDF vectorizer (generated after training)
├── labels.pkl           # Category labels (generated after training)
└── README.md            # Project documentation
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Narendra-Sonawane/My_Projects.git
cd My_Projects/news-classifier
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the Model
```bash
python train.py
```
Output:
```
Model trained and saved!
```
> This generates `model.pkl`, `vectorizer.pkl`, and `labels.pkl`

### 5. Run the App
```bash
python app.py
```
Server starts at → `http://127.0.0.1:5000`

---

## 🚀 API Usage

### 🔹 Option 1 — Web Form (Browser)
Open browser → go to:
```
http://127.0.0.1:5000/predict
```
Type any news text → Click **Classify** ✅

---

### 🔹 Option 2 — JSON API (POST Request)

**Endpoint:**
```
POST /predict
```

**Request Body:**
```json
{
  "text": "NASA launches a new rocket to explore Mars"
}
```

**Response:**
```json
{
  "input": "NASA launches a new rocket to explore Mars",
  "category": "sci.space"
}
```

---

## 🧪 Testing

Run the test script:
```bash
python test.py
```

Expected output:
```json
{"input": "NASA launches a new rocket to explore Mars", "category": "sci.space"}
```

---

## 🧠 How It Works

```
User Input (News Text)
        ↓
TF-IDF Vectorizer  →  Converts text to numbers
        ↓
Naive Bayes Model  →  Predicts category
        ↓
Category Label     →  Returns result
```

---

## 📊 News Categories (20 Classes)

| # | Category | # | Category |
|---|---|---|---|
| 1 | alt.atheism | 11 | rec.sport.hockey |
| 2 | comp.graphics | 12 | sci.crypt |
| 3 | comp.os.ms-windows | 13 | sci.electronics |
| 4 | comp.sys.ibm.pc | 14 | sci.med |
| 5 | comp.sys.mac | 15 | sci.space |
| 6 | comp.windows.x | 16 | soc.religion.christian |
| 7 | misc.forsale | 17 | talk.politics.guns |
| 8 | rec.autos | 18 | talk.politics.mideast |
| 9 | rec.motorcycles | 19 | talk.politics.misc |
| 10 | rec.sport.baseball | 20 | talk.religion.misc |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core language |
| Flask | Web framework / REST API |
| Scikit-learn | ML model + dataset |
| TF-IDF Vectorizer | Text to numeric conversion |
| Naive Bayes | Classification algorithm |
| Pickle | Model serialization |
| Pandas / NumPy | Data handling |

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use and modify.

---

## 👨‍💻 Author

**Narendra Sonawane**  
[![GitHub](https://img.shields.io/badge/GitHub-Narendra--Sonawane-black?style=flat&logo=github)](https://github.com/Narendra-Sonawane)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://linkedin.com/in/your-profile)

---

⭐ **If you found this helpful, give it a star!**
