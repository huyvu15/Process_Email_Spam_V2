import pandas as pd
import re

class NaiveBayes:
    def __init__(self, alpha=1):
        self.alpha = alpha
        self.vocabulary = []
        self.parameters_spam = {}
        self.parameters_ham = {}
        self.p_spam = 0
        self.p_ham = 0

    def clean_text(self, text):
        text = re.sub('\W', ' ', text)
        text = text.lower().split()
        return text

    def train(self, training_set):
        # Tạo một từ điển để lưu số lần xuất hiện của mỗi từ trong spam và ham
        word_counts_per_sms = {'spam': {}, 'ham': {}}

        # Tổng số lượng tin nhắn spam và ham
        n_spam = 0
        n_ham = 0

        for index, row in training_set.iterrows():
            label = row['Label']
            message = self.clean_text(row['SMS'])
            if label == 'spam':
                n_spam += 1
            else:
                n_ham += 1

            for word in message:
                if word not in word_counts_per_sms[label]:
                    word_counts_per_sms[label][word] = 1
                else:
                    word_counts_per_sms[label][word] += 1

                if word not in self.vocabulary:
                    self.vocabulary.append(word)

        # Tính xác suất của từng từ cho spam và ham
        self.parameters_spam = {}
        self.parameters_ham = {}

        for word in self.vocabulary:
            if word not in word_counts_per_sms['spam']:
                word_counts_per_sms['spam'][word] = 0
            if word not in word_counts_per_sms['ham']:
                word_counts_per_sms['ham'][word] = 0

            p_word_given_spam = (word_counts_per_sms['spam'][word] + self.alpha) / (n_spam + self.alpha * len(self.vocabulary))
            p_word_given_ham = (word_counts_per_sms['ham'][word] + self.alpha) / (n_ham + self.alpha * len(self.vocabulary))

            self.parameters_spam[word] = p_word_given_spam
            self.parameters_ham[word] = p_word_given_ham

        # Xác suất trước
        self.p_spam = n_spam / len(training_set)
        self.p_ham = n_ham / len(training_set)
    def classify(self, message):
        message = self.clean_text(message)
        p_spam_given_message = self.p_spam
        p_ham_given_message = self.p_ham
        for word in message:
            if word in self.parameters_spam:
                p_spam_given_message *= self.parameters_spam[word]
            if word in self.parameters_ham:
                p_ham_given_message *= self.parameters_ham[word]
        return p_ham_given_message > p_spam_given_message
    
# Sử dụng mô hình
if __name__ == "__main__":
    # Đọc dữ liệu
    sms_spam = pd.read_csv('SMSSpamCollection', sep='\t', header=None, names=['Label', 'SMS'])

    # Randomize the dataset
    data_randomized = sms_spam.sample(frac=1, random_state=1)
    # Calculate index for split
    training_test_index = round(len(data_randomized) * 0.8)
    # Split into training and test sets
    training_set = data_randomized[:training_test_index].reset_index(drop=True)

    # Tạo và huấn luyện mô hình
    spam_classifier = NaiveBayes(alpha=1)
    spam_classifier.train(training_set)

    mess = """
---      | |  ![Google](  Số điện thoại đã được thêm cho tính năng Xác minh 2 bước  | ![]( DJikGRxIjThIz5y4UBgVtCI4Bg=s96-c)| anhhungbanphim57@gmail.com   ---|---      Từ nay trở đi, hệ thống sẽ gửi mã dùng để đăng nhập vào tài khoản của bạn đến số điện thoại mới. Nếu bạn không phải là người thêm số điện thoại này thì có thể ai đó đang sử dụng tài khoản của bạn. Hãy kiểm tra và bảo mật tài khoản của bạn ngay bây giờ.  [Kiểm tra hoạt động](  Bạn cũng có thể xem hoạt động bảo mật tại     Chúng tôi gửi email này để thông báo cho bạn biết về những thay đổi quan trọng đối với Tài khoản Google và dịch vụ của bạn.  (C) 2023 Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA  
 """
 
    mess1 = """
   Đây là tin nhắn thông thường
    """
    
    mess3 = """
    
     """
    
    # mess1 = 

    result = spam_classifier.classify(mess)
    if result:
        print("Ham")
    else:
        print("Spam")

