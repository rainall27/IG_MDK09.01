'use strict';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errors = {};
        if (!form.elements.login.value.trim()) errors.login = 'Введите логин';
        if (!form.elements.password.value) errors.password = 'Введите пароль';
        if (Object.keys(errors).length) { App.showErrors(form, errors); return; }

        const btn = form.querySelector('button[type="submit"]');
        App.loading(btn, true);
        const { ok, data } = await App.api('/api/login', { method: 'POST', body: App.formData(form) });
        App.loading(btn, false);

        if (!ok) {
            App.showErrors(form, data.errors || { form: data.error || 'Ошибка входа' });
            form.elements.password.value = '';
            return;
        }
        App.go(data.redirect);
    });
});
