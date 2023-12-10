# DjangoProject
## Інструкція по розгортанню проекту

1. Клонуйте репозиторій:
   ```bash
   git clone https://github.com/KordanP/DjangoProject/
2. Перейдіть у директорію проекту:
   ```bash
   cd назва_проекту
3. Створіть віртуальне оточення:
   ```bash
   python3 -m venv venv
4. Активуйте віртуальне оточення:
   ```bash
   .\.venv\Scripts\activate
5. Встановіть залежності:
   ```bash
   pip install -r labs/requirements.txt
6. Запустіть сервер:
   ```bash
   python labs/manage.py runserver 8000
14. Відкрийте браузер і перейдіть за адресою:
    ```bash
    http://127.0.0.1:8000/api/v1/hello-world-2