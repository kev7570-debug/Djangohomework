# Импорт встроенных библиотек для работы веб-сервера
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import os

# Настройки запуска
hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    """Класс для обработки входящих запросов от клиентов"""

    def do_GET(self):
        """Метод для обработки входящих GET-запросов"""

        # Обработка статических файлов (CSS, JS)
        if self.path.startswith('/static/'):
            self.serve_static_file()
            return

        # Обработка страницы контактов
        if self.path == '/contacts' or self.path == '/':
            try:
                # Чтение HTML файла с помощью контекстного менеджера
                with open('contacts.html', 'r', encoding='utf-8') as file:
                    html_content = file.read()

                # Отправка ответа
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))

            except FileNotFoundError:
                self.send_404()
            except Exception as e:
                self.send_500()
        else:
            self.send_404()

    def serve_static_file(self):
        """Метод для обслуживания статических файлов (CSS, JS)"""
        try:
            # Преобразуем путь к файлу (убираем /static/ в начале)
            file_path = self.path[1:]  # убираем первый слеш

            # Определяем тип файла по расширению
            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'text/plain'

            # Читаем файл
            with open(file_path, 'rb') as file:
                content = file.read()

            # Отправляем ответ
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            self.send_404()
        except Exception as e:
            self.send_500()

    def send_404(self):
        """Страница 404"""
        self.send_response(404)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        error_page = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>404 - Страница не найдена</title>
            <link href="/static/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container text-center mt-5">
                <h1 class="display-1">404</h1>
                <h2 class="mb-4">Страница не найдена</h2>
                <p class="lead mb-4">К сожалению, запрашиваемая страница не существует.</p>
                <a href="/contacts" class="btn btn-primary">Вернуться на главную</a>
            </div>
        </body>
        </html>
        """
        self.wfile.write(error_page.encode('utf-8'))

    def send_500(self):
        """Страница 500"""
        self.send_response(500)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        error_page = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>500 - Ошибка сервера</title>
            <link href="/static/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container text-center mt-5">
                <h1 class="display-1">500</h1>
                <h2 class="mb-4">Внутренняя ошибка сервера</h2>
                <p class="lead mb-4">Извините, произошла техническая ошибка. Попробуйте позже.</p>
                <a href="/contacts" class="btn btn-primary">Вернуться на главную</a>
            </div>
        </body>
        </html>
        """
        self.wfile.write(error_page.encode('utf-8'))

    def do_POST(self):
        """Метод для обработки POST-запросов"""
        if self.path == '/contacts':
            # Получаем длину содержимого
            content_length = int(self.headers.get('Content-Length', 0))

            # Читаем данные из POST-запроса
            post_data = self.rfile.read(content_length).decode('utf-8')

            # Парсим данные формы
            form_data = parse_qs(post_data)

            # Выводим данные в консоль
            print("\n" + "=" * 50)
            print("НОВОЕ СООБЩЕНИЕ ИЗ ФОРМЫ КОНТАКТОВ")
            print("=" * 50)

            # Извлекаем и выводим каждое поле
            name = form_data.get('name', [''])[0]
            email = form_data.get('email', [''])[0]
            phone = form_data.get('phone', [''])[0]
            subject = form_data.get('subject', [''])[0]
            message = form_data.get('message', [''])[0]

            # Сопоставление темы с текстом
            subject_map = {
                'question': 'Вопрос о продукте',
                'support': 'Техническая поддержка',
                'partnership': 'Сотрудничество',
                'other': 'Другое'
            }
            subject_text = subject_map.get(subject, subject)

            print(f"Имя: {name}")
            print(f"Email: {email}")
            print(f"Телефон: {phone if phone else 'Не указан'}")
            print(f"Тема: {subject_text}")
            print(f"Сообщение: {message}")
            print("=" * 50 + "\n")

            # Отправляем ответ с подтверждением
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            # Показываем страницу с подтверждением
            with open('contacts.html', 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Добавляем уведомление об успешной отправке
            success_message = """
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <strong>Спасибо за сообщение!</strong> Мы свяжемся с вами в ближайшее время.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            """

            # Вставляем сообщение после заголовка формы
            html_content = html_content.replace('<form method="POST" action="/contacts">',
                                                f'<form method="POST" action="/contacts">{success_message}')

            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_404()

    def log_message(self, format, *args):
        """Переопределяем метод логирования для вывода в консоль"""
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    print("=" * 50)
    print("ЗАПУСК ВЕБ-СЕРВЕРА")
    print("=" * 50)
    print(f"Сервер запущен по адресу: http://{hostName}:{serverPort}")
    print("Страница контактов доступна по адресу: http://{}:{}/contacts".format(hostName, serverPort))
    print("Для остановки сервера нажмите Ctrl+C")
    print("=" * 50 + "\n")

    # Инициализация веб-сервера
    webServer = HTTPServer((hostName, serverPort), MyServer)

    try:
        # Запуск веб-сервера в бесконечном цикле
        webServer.serve_forever()
    except KeyboardInterrupt:
        # Корректная остановка при нажатии Ctrl+C
        print("\n" + "=" * 50)
        print("ОСТАНОВКА СЕРВЕРА")
        print("=" * 50)
        pass

    # Корректное завершение работы сервера
    webServer.server_close()
    print("Сервер успешно остановлен.")
