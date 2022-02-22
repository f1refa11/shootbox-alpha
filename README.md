﻿# ShootBox
Добро пожаловать на репозиторию игры ShootBox. Здесь вы можете скачать исходный код, сообщить о проблеме в игре и многое другое.

# Компиляция
Так как разработка игры ведётся на Linux, а возможности компилировать игру под другие палатформы пока нет, вы можете помочь проекту, компилируя игру под свою систему и отправляя её мне.

Для начала, вам понадобится следующее:

 1. Python версии 3.6 и выше,
 2. Установленные библиотеки Pygame и Pyinstaller последних версий.

А затем:

 1. Скачайте исходный код репозитория и распакуйте его в удобном для вас месте на компьютере.
 2. Запустите командную строку(или терминал) и переместитесь в папку с исходным кодом.
 3. Выполните команду `pyinstaller --onedir --windowed main.py`(ознакомиться с доп.флагами для компиляции можно [здесь](https://pyinstaller.readthedocs.io/en/stable/usage.html)
 4. После успешной компиляции скопируйте папу resources, перейдите в папку dist и затем main, и там вставьте ранее скопированную папку.
 5. Запустите файл main(.exe в Windows)
