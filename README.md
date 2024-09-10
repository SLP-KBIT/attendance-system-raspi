### 構築方法

**※現在64bit版だとうまく動作しないので32bit使って!**

#### いつもの

```
sudo apt update

sudo apt upgrade -y

sudo reboot
```

#### 必要なライブラリ

```
pip install --upgrade Pillow --break-system-packages

pip install nfcpy --break-system-packages
```

#### NFCリーダを``sudo``なしでできるように

```
sudo sh -c 'echo SUBSYSTEM==\"usb\", ACTION==\"add\", ATTRS{idVendor}==\"054c\", ATTRS{idProduct}==\"06c1\", GROUP=\"plugdev\" >> /etc/udev/rules.d/nfcdev.rules'

sudo udevadm control -R
```

### その他推奨設定

- スクリーンセーバーをオフ
- プログラムを自動起動

### カスタマイズ

- ``sounds``以下に自分の学籍番号のMP3ファイル入れると音が変わる(例：21T000.mp3)
- ``images``以下に自分の学籍番号のPNGファイル入れると画像が変わる(例：21T000.png) <-まだ

※テキスト機能は廃止しました
