import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
from pymongo import MongoClient
import random
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import os


class CustomListbox(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        self.list_items = []

    def insert_item(self, sender, subject, date, image):
        item_frame = tk.Frame(self)

        avatar_label = tk.Label(item_frame, image=image, borderwidth=2, relief="solid", width=30, height=30)
        avatar_label.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="w")

        info_text = f"Sender: {sender}\nSubject: {subject}\nDate: {date}"
        info_label = tk.Label(item_frame, text=info_text, font=("Helvetica", 12))
        info_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.list_items.append(item_frame)


class GmailApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gmail App")
        self.root.geometry("1200x1000")

        self.ham_messages = []
        self.spam_messages = []
        self.message_index = 1
        self.vectorizer = CountVectorizer()

        self.spam_classifier = MultinomialNB()
        self.info_listbox = None  # Thêm khai báo biến info_listbox

        self.create_gui()

        self.load_messages_from_database()

    def create_gui(self):
        inbox_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        inbox_frame.grid(row=0, column=0, sticky="nsew")

        # Ham Listbox
        ttk.Label(inbox_frame, text="Ham Inbox", font=("Helvetica", 16, "bold")).grid(row=0, column=0, sticky="w")
        self.ham_listbox = tk.Listbox(inbox_frame, selectmode=tk.SINGLE, width=60, height=10, font=("Helvetica", 12))
        self.ham_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.ham_listbox.bind('<<ListboxSelect>>', self.display_selected_message)

        # Spam Listbox
        ttk.Label(inbox_frame, text="Spam Inbox", font=("Helvetica", 16, "bold")).grid(row=0, column=1, sticky="w")
        self.spam_listbox = tk.Listbox(inbox_frame, selectmode=tk.SINGLE, width=60, height=10, font=("Helvetica", 12))
        self.spam_listbox.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.spam_listbox.bind('<<ListboxSelect>>', self.display_selected_message)

        delete_ham_button = ttk.Button(inbox_frame, text="Delete Ham", command=lambda: self.delete_selected_message('ham'))
        delete_ham_button.grid(row=2, column=0, pady=10, sticky="w")

        delete_spam_button = ttk.Button(inbox_frame, text="Delete Spam", command=lambda: self.delete_selected_message('spam'))
        delete_spam_button.grid(row=2, column=1, pady=10, sticky="w")

        # Email Frame
        email_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        email_frame.grid(row=1, column=0, sticky="nsew")

        # Email Display
        email_display_label = ttk.Label(email_frame, text="Email", font=("Helvetica", 16, "bold"))
        email_display_label.grid(row=0, column=0, sticky="w")

        self.email_display_frame = ttk.Frame(email_frame)
        self.email_display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


        # Listbox mới cho thông tin sender, subject, date (Listbox 1)
        self.info_listbox = tk.Listbox(self.email_display_frame, selectmode=tk.SINGLE, width=100, height=3, font=("Helvetica", 12))
        self.info_listbox.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="w")


        # Listbox mới cho body_text (Listbox 2)
        self.email_display_text = scrolledtext.ScrolledText(self.email_display_frame, wrap=tk.WORD, width=100, height=20, font=("Helvetica", 12))
        self.email_display_text.grid(row=1, column=0, sticky="nsew")

        # Grid configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        inbox_frame.columnconfigure(0, weight=1)
        inbox_frame.rowconfigure(1, weight=1)

        email_frame.columnconfigure(0, weight=1)
        email_frame.rowconfigure(1, weight=1)
        
    def train_spam_classifier(self):
        sms_spam = pd.read_csv('SMSSpamCollection', sep='\t', header=None, names=['Label', 'SMS'])
        data_randomized = sms_spam.sample(frac=1, random_state=1)
        training_test_index = round(len(data_randomized) * 0.8)
        training_set = data_randomized[:training_test_index].reset_index(drop=True)

        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(training_set['SMS'])
        y = training_set['Label']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.spam_classifier = MultinomialNB()
        self.spam_classifier.fit(X_train, y_train)

    def load_messages_from_database(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client['email']
        email_collection = db['email_messages']

        messages = email_collection.find()
        for message in messages:
            sender = message.get('sender', 'Unknown Sender')
            subject = message.get('subject', 'No Subject')
            date = message.get('date', 'Unknown Date')
            body_text = message.get('body_text', 'No Body Text')

            message_vector = self.vectorizer.transform([body_text])

            is_spam = self.spam_classifier.predict(message_vector)[0]

            avatar_path = self.get_random_avatar_path()
            avatar_image = self.load_avatar_image(avatar_path)

            if is_spam:
                self.spam_messages.append((sender, subject, date, body_text, avatar_image))
                self.spam_listbox.insert(tk.END, f"{self.message_index}. {sender} - {subject}")
            else:
                self.ham_messages.append((sender, subject, date, body_text, avatar_image))
                # Hiển thị thông tin trong listbox thứ nhất (ham_listbox)
                info_text = f"Sender: {sender}\nSubject: {subject}\nDate: {date}"

                # Thêm cell mới vào listbox
                self.ham_listbox.insert(tk.END, info_text)

            self.message_index += 1

    def display_email(self, message):
        self.email_display_text.config(state=tk.NORMAL)
        self.email_display_text.delete(1.0, tk.END)

        sender_text = f"Sender: {message[0]}\n"
        subject_text = f"Subject: {message[1]}\n"
        date_text = f"Date: {message[2]}\n"
        body_text = f"Body Text:\n{message[3]}\n"

        self.email_display_text.insert(tk.END, sender_text)
        self.email_display_text.insert(tk.END, subject_text)
        self.email_display_text.insert(tk.END, date_text)
        self.email_display_text.insert(tk.END, body_text)

        avatar_image = message[4]
        if avatar_image:
            # Tạo Label để chứa hình ảnh
            avatar_label = tk.Label(self.info_listbox, image=avatar_image, borderwidth=2, relief="solid", width=30,
                                    height=30)
            avatar_label.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="w")

        # Hiển thị thông tin "sender, subject, date" dưới hình ảnh random
        info_text = f"Sender: {message[0]}\nSubject: {message[1]}\nDate: {message[2]}"
        self.info_listbox.delete(0, tk.END)  # Xóa hết nội dung cũ
        self.info_listbox.insert(tk.END, info_text)

        # Hiển thị body_text trong listbox 2
        body_text = message[3]
        self.email_display_text.config(state=tk.NORMAL)
        self.email_display_text.delete(1.0, tk.END)
        self.email_display_text.insert(tk.END, body_text)
        self.email_display_text.config(state=tk.DISABLED)

        # Hiển thị thông tin trong listbox 1
        self.info_listbox.delete(0, tk.END)
        self.info_listbox.insert(tk.END, f"Sender: {message[0]}")
        self.info_listbox.insert(tk.END, f"Subject: {message[1]}")
        self.info_listbox.insert(tk.END, f"Date: {message[2]}")

    def display_selected_message(self, event):
        selected_ham_index = self.ham_listbox.curselection()
        selected_spam_index = self.spam_listbox.curselection()

        if selected_ham_index:
            selected_index = int(selected_ham_index[0])
            selected_message = self.ham_messages[selected_index]
        elif selected_spam_index:
            selected_index = int(selected_spam_index[0])
            selected_message = self.spam_messages[selected_index]
        else:
            return
        self.display_email(selected_message)

    def delete_selected_message(self, inbox_type):
        selected_ham_index = self.ham_listbox.curselection()
        selected_spam_index = self.spam_listbox.curselection()

        if inbox_type == 'ham' and selected_ham_index:
            selected_index = int(selected_ham_index[0])
            self.ham_listbox.delete(selected_index)
            del self.ham_messages[selected_index]
        elif inbox_type == 'spam' and selected_spam_index:
            selected_index = int(selected_spam_index[0])
            self.spam_listbox.delete(selected_index)
            del self.spam_messages[selected_index]

    def get_random_avatar_path(self):
        avatar_dir = "Image"
        avatar_files = [f for f in os.listdir(avatar_dir) if f.startswith("avatar-") and f.endswith(".png")]
        if avatar_files:
            return os.path.join(avatar_dir, random.choice(avatar_files))
        return ""

    def load_avatar_image(self, path):
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((100, 100), resample=Image.Resampling.LANCZOS)
            img_photo = ImageTk.PhotoImage(img)
            return img_photo
        return None

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gmail_app = GmailApp()
    gmail_app.run()
