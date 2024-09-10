import tkinter as tk
from datetime import datetime
from time import sleep
import json
import threading
from PIL import Image, ImageTk
import nfc
import pygame.mixer
import unicodedata

font = 'Times New Roman'

class Display:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance-System")
        # self.root.geometry("1280x1024")
        self.root.attributes("-fullscreen", True) # フルスクリーン設定

        # Open the image file
        original_image = Image.open('./images/default.png')
        resized_image = original_image.resize((1280, 1024), Image.LANCZOS) # Resize the image
        self.bg_image = ImageTk.PhotoImage(resized_image)

        # Create a Canvas and set the background image
        self.canvas = tk.Canvas(root, width=1280, height=1024)
        self.canvas.pack(fill="both", expand=True)
        self.background_image_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.top_text = self.canvas.create_text(650, 70, text="SLP出席管理システム", font=(font, 50), fill="black", anchor="center")

        self.time_text = self.canvas.create_text(650, 230, text="", font=(font, 80), fill="black", anchor="center")
        self.update_time()

        self.card_status_text = self.canvas.create_text(650, 450, text="× エラーが発生しています\n", font=(font, 50), fill="black", anchor="center")

    def update_time(self):
        now = datetime.now()
        formatted_time = now.strftime('%Y年%m月%d日 %H:%M:%S')
        self.canvas.itemconfig(self.time_text, text=formatted_time)
        self.root.after(1000, self.update_time)

    def hide_background(self):
        # Restore the original background image
        self.canvas.itemconfig(self.background_image_id, image=self.bg_image)


class NFCHandler:
    def __init__(self):
        self.result = {"number": "?", "furigana": "?"}

    # タッチされた時の処理
    def on_connect(self, tag):
        self.result['number'] = "?"
        self.result['furigana'] = "?"

        idm, pmm = tag.polling(system_code=0xfe00)
        tag.idm, tag.pmm, tag.sys = idm, pmm, 0xfe00

        service_code = 0x1a8b
        sc = nfc.tag.tt3.ServiceCode(service_code >> 6, service_code & 0x3f)
        bc1 = nfc.tag.tt3.BlockCode(0, service=0) # 学籍番号のブロックコード
        bc2 = nfc.tag.tt3.BlockCode(1, service=0) # 氏名(フリガナ)のブロックコード
        data = tag.read_without_encryption([sc], [bc1, bc2])

        # print ('  ' + '\n  '.join(tag.dump())) # カードのすべての情報

        number = data[2:8].decode("utf-8") # 学籍番号
        furigana = data[16:32].decode("shift_jis") # 氏名(フリガナ)

        # JSONファイルの読み込み
        try:
            with open('/home/slp-admin/attendance-system-raspi/data.json', 'r') as json_file:
                data = json.load(json_file) # data配列に代入
        except FileNotFoundError: # JSONファイルが存在しない場合、新しいリストを作成
            data = []

        # 新しい辞書データを作成
        new_data = {
            "number": number,
            "furigana": furigana,
            "timestamp": str(datetime.now().replace(microsecond=0))  # 現在のタイムスタンプを文字列に変換
        }

        # dataリストに新しい辞書データを追加
        data.append(new_data)

        # JSONファイルにデータを書き込み
        with open('/home/slp-admin/attendance-system-raspi/data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        self.result['number'] = number
        self.result['furigana'] = unicodedata.normalize('NFKC', furigana)


def read_nfc(app):
    handler = NFCHandler()
    pygame.mixer.init(frequency=44100)
    while True:
        try:
            clf = nfc.ContactlessFrontend('usb') # USBからNFCリーダーを認識
        except:
            app.canvas.itemconfig(app.card_status_text, text="× NFCリーダーが接続されていません\n")
            sleep(5)
            continue

        app.canvas.itemconfig(app.card_status_text, text="\n学生証をタッチしてください\n")
        try:
            clf.connect(rdwr={'on-connect': handler.on_connect}) # カードがタッチされたら実行(on_connect関数)
            app.canvas.itemconfig(app.card_status_text, text=f"\n✓出席しました！\n{handler.result['number']} {handler.result['furigana']}")

            try:
                # Load and resize the new background image for when the button is pressed
                # new_bg_image = Image.open(f"./images/{handler.result['number']}.png")
                # resized_new_bg_image = new_bg_image.resize((1280, 1024), Image.LANCZOS)
                # app.new_bg_image = ImageTk.PhotoImage(resized_new_bg_image)
                app.canvas.itemconfig(app.background_image_id, image=app.new_bg_image)
            except:
                app.canvas.itemconfig(app.background_image_id, image=app.bg_image)

            try:
                pygame.mixer.music.load(f"./sounds/{handler.result['number']}.mp3")
            except:
                pygame.mixer.music.load('./sounds/default.mp3')

            pygame.mixer.music.play(1)
            sleep(2)
            app.root.after(0, app.hide_background)

        except:
            app.canvas.itemconfig(app.card_status_text, text=f"\n⚠️カードの読み取りに失敗しました\n")
            sleep(2)

        finally:
            clf.close()

def main():
    root = tk.Tk()
    app = Display(root)
    thread = threading.Thread(target=read_nfc, args=(app,), name='attendance_read_nfc', daemon = True)
    thread.start()
    root.mainloop()

if __name__ == "__main__":
    main()
