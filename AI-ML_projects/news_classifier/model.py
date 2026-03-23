import pickle

def predict_news(text):
    model = pickle.load(open("model.pkl", "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
    labels = pickle.load(open("labels.pkl", "rb"))

    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    return labels[pred]