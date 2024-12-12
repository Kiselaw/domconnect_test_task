# domconnect_test_task

Ссылка на тестовое задание - https://docs.google.com/document/d/1ehZHLgk7630ty2jyN1odviAISIfQZ0OwB7zNIuMEcCc/edit?tab=t.0

# Стек

- Python 3.12.7
- Selenium 4.27.1

# Справка

Для работы скрипта Chromedriver, соответствующий версии вашего браузера, должен быть расположен:

Windows:
```
C:\Windows\
```

Linux\MacOS:

```
/usr/bin
```

В ином случае путь придется прописывать вручную:

```python
self._driver = webdriver.Chrome('ваш_путь')
```

# Запуск

Первоочередно, конечно, необходимо создать и активировать виртуальное окружение, а затем установить зависимости:

Виртуальное окружение:

Windows:

```bash
py -3 -m venv env
```

```bash
. venv/Scripts/activate 
```

macOS/Linux:

```bash
python3 -m venv .venv
```

```bash
source env/bin/activate
```

Зависимости:

```bash
pip install -r requirements.txt
```

Затем необходимо запустить скрипт:

Windows:

```bash
py main.py
```
Linux/MacOS

```bash
python3 main.py
```

P.S: В качестве линтера использовался ruff, он есть в списке зависимостей