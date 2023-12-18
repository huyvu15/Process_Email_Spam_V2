from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Dữ liệu mẫu
texts = ["This is a positive example.", "Negative example here.", "Another positive text.", "Not a positive one."]

# Nhãn tương ứng với mỗi văn bản (0: Negative, 1: Positive)
labels = [1, 0, 1, 0]

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.25, random_state=42)

# Chuyển đổi văn bản thành ma trận đếm (bag-of-words)
vectorizer = CountVectorizer()
X_train_counts = vectorizer.fit_transform(X_train)
X_test_counts = vectorizer.transform(X_test)

# Sử dụng mô hình Multinomial Naive Bayes
nb_classifier = MultinomialNB()
nb_classifier.fit(X_train_counts, y_train)

# Dự đoán trên tập kiểm tra
y_pred = nb_classifier.predict(X_test_counts)

# Đánh giá mô hình
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy}")
print("Classification Report:\n", report)
