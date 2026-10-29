'use strict';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('register-form');
    const fields = ['login', 'password', 'fio', 'phone', 'email'];
    liveValidate(form, fields);

    const phone = form.elements.phone;
    phone.addEventListener('input', () => {
        let d = phone.value.replace(/\D/g, '');
        if (d && d[0] !== '8') d = `8${d}`;
        d = d.slice(0, 11);
        let out = d.slice(0, 1);
        if (d.length > 1) out += `(${d.slice(1, 4)}`;
        if (d.length >= 4) out += ')';
        if (d.length > 4) out += d.slice(4, 7);
        if (d.length > 7) out += `-${d.slice(7, 9)}`;
        if (d.length > 9) out += `-${d.slice(9, 11)}`;
        phone.value = out;
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errors = validateForm(form, fields);
        if (Object.keys(errors).length) { App.showErrors(form, errors); return; }

        const btn = form.querySelector('button[type="submit"]');
        App.loading(btn, true);
        const { ok, data } = await App.api('/api/register', { method: 'POST', body: App.formData(form) });
        App.loading(btn, false);

        if (!ok) { App.showErrors(form, data.errors || { form: data.error || 'Ошибка регистрации' }); return; }
        App.toast(data.message);
        setTimeout(() => App.go(data.redirect), 900);
    });
});
