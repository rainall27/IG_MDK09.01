'use strict';

function normalizeDateTime(value) {
    const match = /^(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2})$/.exec(value.trim());
    if (!match) return '';
    const [, day, month, year, hour, minute] = match;
    const iso = `${year}-${month}-${day}T${hour}:${minute}`;
    const date = new Date(iso);
    if (Number.isNaN(date.getTime()) || date.getFullYear() !== Number(year)
        || date.getMonth() + 1 !== Number(month) || date.getDate() !== Number(day)
        || date.getHours() !== Number(hour) || date.getMinutes() !== Number(minute)) return '';
    return iso;
}

const Rules = {
    login: (v) => (!v ? 'Введите логин'
        : (/^[A-Za-z0-9]{6,50}$/.test(v) ? '' : 'Логин: только латиница и цифры, не менее 6 символов')),
    password: (v) => (!v ? 'Введите пароль' : (v.length >= 8 ? '' : 'Пароль должен быть не короче 8 символов')),
    fio: (v) => (!v.trim() ? 'Введите ФИО'
        : (/^[А-Яа-яЁё]+( [А-Яа-яЁё]+)*$/.test(v.trim()) ? '' : 'ФИО: только кириллица и пробелы')),
    phone: (v) => (!v ? 'Введите телефон'
        : (/^8\(\d{3}\)\d{3}-\d{2}-\d{2}$/.test(v) ? '' : 'Телефон в формате 8(XXX)XXX-XX-XX')),
    email: (v) => (!v ? 'Введите email'
        : (/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(v) ? '' : 'Некорректный адрес электронной почты')),
    room_id: (v) => (v ? '' : 'Выберите помещение'),
    payment_method_id: (v) => (v ? '' : 'Выберите способ оплаты'),
    start_at: (v) => {
        if (!v) return 'Укажите дату и время начала конференции';
        const iso = normalizeDateTime(v);
        if (!iso) return 'Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ';
        const d = new Date(iso);
        return d > new Date() ? '' : 'Дата начала должна быть в будущем';
    },
    rating: (v) => (v >= 1 && v <= 5 ? '' : 'Поставьте оценку от 1 до 5'),
    text: (v) => {
        const t = (v || '').trim();
        if (t.length < 10) return 'Отзыв должен быть не короче 10 символов';
        return t.length > 1000 ? 'Отзыв не длиннее 1000 символов' : '';
    },
};

function validateForm(form, names) {
    const errors = {};
    names.forEach((name) => {
        const el = form.elements[name];
        const value = el ? (el.value ?? '') : '';
        const err = Rules[name](value);
        if (err) errors[name] = err;
    });
    return errors;
}

function liveValidate(form, names) {
    names.forEach((name) => {
        const el = form.elements[name];
        if (!el || !el.addEventListener) return;
        el.addEventListener('blur', () => App.setFieldState(el, Rules[name](el.value)));
        el.addEventListener('input', () => {
            if (el.closest('.field')?.classList.contains('has-error')) App.setFieldState(el, Rules[name](el.value));
        });
    });
}
