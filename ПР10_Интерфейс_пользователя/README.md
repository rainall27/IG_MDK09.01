# Практическая работа № 10. Разработка интерфейса пользователя

**Цель:** свёрстать интерфейс портала по техническому заданию.

## Соответствие ТЗ (задание 1 КИМ)
| Страница из ТЗ | Требование | Реализация |
|---|---|---|
| Регистрация | логин, пароль, ФИО, телефон, e-mail, все обязательные | `code/frontend/templates/register.html`, кнопка «Зарегистрироваться» |
| Авторизация | логин и пароль, сообщения об ошибках, ссылка **«Еще не зарегистрированы? Регистрация»** и обратно | `code/frontend/templates/login.html` («Уже зарегистрированы? Авторизация» на странице регистрации) |
| Просмотр заявок | свои заявки и отзыв о мероприятии | `code/frontend/templates/dashboard.html` |
| Формирование заявки | помещение, дата начала, способ оплаты (очно / СБП), кнопка «Отправить» | `code/frontend/templates/create_request.html` |
| Панель администратора | все заявки, смена статуса «Новая» → «Мероприятие назначено» / «Завершено» | `code/frontend/templates/admin.html` |

## Технологии вёрстки
- **HTML5:** семантика (`header`, `nav`, `main`, `section`, `article`, `footer`), `label for` у каждого поля, `alt` у картинок, `aria-*` у меню и рейтинга.
- **CSS3:** CSS-переменные с фирменной палитрой, Grid и Flexbox, медиа-запросы, анимации `@keyframes`. Один файл `code/frontend/static/css/style.css`.
- **JavaScript:** без библиотек, `fetch` + JSON, отдельный файл для каждой страницы.
- **Шаблонизатор Jinja2:** общий каркас `base.html`, страницы наследуют его через `{% extends %}`.

## Адаптивность (390×844)
Вёрстка mobile-first: на смартфоне 1 колонка и меню-бургер, на планшете (768 px) 2 колонки, на ПК (992 px+) 3 колонки и горизонтальное меню.

## Проверка в двух браузерах
Проверены Chromium 153.0.8010.0 и Firefox 153.0. В каждом открыты главная, регистрация, личный кабинет с заявками и форма новой заявки. При отправке пустой регистрации появились ошибки у всех пяти полей; вход участника открыл «Мои заявки». На странице заявки проверены выбор помещения, способ оплаты и ввод даты. Необработанных исключений JavaScript в этих сценариях нет.

| Браузер | Размер области страницы | Материалы |
|---|---|---|
| Chromium 153.0.8010.0 | 1366×900 и 390×844 | Снимки ПК и мобильных страниц |
| Firefox 153.0 | 1366×900 | Главная, ошибки регистрации, заявки и форма даты |

Численные результаты проверок записаны в [`code/browser_checks.json`](code/browser_checks.json). Проверка ограничена перечисленными сценариями.

## Мобильная версия 390×844
На главной, в регистрации и форме заявки нет горизонтального переполнения. На мобильной ширине навигация заменена кнопкой меню, блоки перестроены в одну колонку.

| Главная | Регистрация | Новая заявка |
|---|---|---|
| ![](img/01_mobile_home.png) | ![](img/02_mobile_registration.png) | ![](img/03_mobile_new_request.png) |

## Главная в Chromium на ПК
![](img/04_chromium_desktop_home.png)

## Валидация в Chromium
![](img/05_chromium_validation.png)

## Главная в Firefox
![](img/06_firefox_desktop_home.png)

## Валидация в Firefox
![](img/07_firefox_validation.png)

## Мои заявки в Firefox
![](img/08_firefox_my_requests.png)

## Форма новой заявки в Firefox
![](img/09_firefox_new_request.png)

## Код этой работы
Папка [`code/`](code). Файлы:

- `frontend/static/css/style.css`
- `frontend/static/js/common.js`
- `frontend/templates/base.html`
- `frontend/templates/index.html`
- `frontend/templates/register.html`
- `frontend/templates/login.html`
- `frontend/templates/dashboard.html`
- `frontend/templates/create_request.html`
- `frontend/templates/admin.html`
- `frontend/templates/profile.html`
- `frontend/templates/error.html`
- `browser_checks.json`
