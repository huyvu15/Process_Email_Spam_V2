import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
from pymongo import MongoClient
import random
import pandas as pd 
import os
from NaiveBayes import NaiveBayes 

class GmailApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gmail App")
        self.root.geometry("1200x1000")

        self.ham_messages = []
        self.spam_messages = []

        self.message_index = 1
        self.spam_classifier = NaiveBayes()  # Sửa đổi: Khởi tạo NaiveBayes
        
        self.info_listbox = None

        self.create_gui()

        self.load_messages_from_database()
        self.train_spam_classifier()

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

        # Nhãn Hiển thị Email
        email_display_label = ttk.Label(email_frame, text="Inbox", font=("Arial", 10, "bold"))
        email_display_label.grid(row=0, column=0, sticky="w")

        self.email_display_frame = ttk.Frame(email_frame)
        self.email_display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Listbox mới cho thông tin sender, subject, date (Listbox 1)
        self.info_listbox_frame = ttk.Frame(email_frame)
        self.info_listbox_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
     
        self.info_listbox = tk.Listbox(self.email_display_frame, selectmode=tk.SINGLE, width=100, height=3, font=("Helvetica", 12))
        self.info_listbox.grid(row=0, column=0, padx=(0, 0), pady=0, sticky="w")
        
        # Listbox mới cho body_text (Listbox 2)
        self.email_display_text = scrolledtext.ScrolledText(self.email_display_frame, wrap=tk.WORD, width=100, height=15, font=("Helvetica", 12))
        self.email_display_text.grid(row=1, column=0, sticky="nw")

        # In text "user"
        user_label = ttk.Label(self.email_display_frame, text="Người gửi: ", font=("Helvetica", 30, "bold"), foreground="red")
        user_label.grid(row=0, column=1, sticky="NSEW")
        
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

        self.spam_classifier = NaiveBayes(alpha=1)  # Sử dụng self.spam_classifier để lưu trữ mô hình
        self.spam_classifier.train(training_set)

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
            avatar_label = tk.Label(self.email_display_frame, image=avatar_image, borderwidth=2, relief="solid", width=200, height=270)
            avatar_label.grid(row=1, column=1, sticky="w")

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


    def load_messages_from_database(self):
        # Kết nối đến MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['email']  
        email_collection = db['email']

        # Tải tin nhắn từ cơ sở dữ liệu
        messages = email_collection.find()
        for message in messages:
            sender = message.get('sender', 'Unknown Sender')
            subject = message.get('subject', 'No Subject')
            date = message.get('date', 'Unknown Date')
            body_text = message.get('body_text', 'No Body Text')
            
            # cập nhập lại mô hình trước khi dự đoạn
            self.train_spam_classifier()
            is_spam = self.spam_classifier.classify(body_text)
            # print(body_text)
            print(is_spam)

            
            avatar_path = self.get_random_avatar_path()
            avatar_image = self.load_avatar_image(avatar_path)

            if not is_spam:
                self.ham_messages.append((sender, subject, date, body_text, avatar_image))
                # break
                self.ham_listbox.insert(tk.END, f"{self.message_index}. {sender} - {subject}")
            else:
                self.spam_messages.append((sender, subject, date, body_text, avatar_image))
                # print(self.spam_messages)
                
                self.spam_listbox.insert(tk.END, f"{self.message_index}. {sender} - {subject}")

            self.message_index += 1
    
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
            img = img.resize((300, 300), resample=Image.Resampling.LANCZOS)
            img_photo = ImageTk.PhotoImage(img)
            return img_photo
        return None
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gmail_app = GmailApp()
    gmail_app.run()