'use strict';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('request-form');
    const fields = ['room_id', 'start_at', 'payment_method_id'];
    const select = form.elements.room_id;
    liveValidate(form, fields);

    const start = form.elements.start_at;

    form.querySelectorAll('input[name="room_pick"]').forEach((radio) => {
        radio.addEventListener('change', () => {
            select.value = radio.value;
            App.setFieldState(select, '');
        });
    });
    select.addEventListener('change', () => {
        const radio = form.querySelector(`input[name="room_pick"][value="${select.value}"]`);
        if (radio) radio.checked = true;
        else form.querySelectorAll('input[name="room_pick"]').forEach((r) => { r.checked = false; });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errors = validateForm(form, fields);
        if (Object.keys(errors).length) { App.showErrors(form, errors); return; }

        const body = {
            room_id: select.value,
            start_at: normalizeDateTime(start.value),
            payment_method_id: form.elements.payment_method_id.value,
        };
        const btn = form.querySelector('button[type="submit"]');
        App.loading(btn, true);
        const { ok, data } = await App.api('/api/requests', { method: 'POST', body });
        App.loading(btn, false);

        if (!ok) { App.showErrors(form, data.errors || { form: data.error || 'Не удалось отправить заявку' }); return; }
        App.toast(data.message);
        setTimeout(() => App.go(data.redirect), 800);
    });
});
