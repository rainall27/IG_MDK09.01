'use strict';

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-delete-request]').forEach((btn) => {
        let timer = null;
        btn.addEventListener('click', async () => {
            if (!btn.classList.contains('is-confirm')) {
                btn.classList.add('is-confirm');
                btn.textContent = 'Точно удалить?';
                timer = setTimeout(() => {
                    btn.classList.remove('is-confirm');
                    btn.textContent = 'Удалить заявку';
                }, 4000);
                return;
            }
            clearTimeout(timer);
            App.loading(btn, true);
            const { ok, data } = await App.api(`/api/requests/${btn.dataset.deleteRequest}`, { method: 'DELETE' });
            if (!ok) {
                App.loading(btn, false);
                App.toast(data.errors?.form || 'Не удалось удалить заявку', 'error');
                return;
            }
            const card = btn.closest('[data-testid="request-card"]');
            const grid = card.parentElement;
            card.remove();
            App.toast(data.message);
            if (!grid.querySelector('[data-testid="request-card"]')) setTimeout(() => location.reload(), 600);
        });
    });

    document.querySelectorAll('[data-review-form]').forEach((form) => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const rating = form.querySelector('input[name="rating"]:checked')?.value || '';
            const text = form.elements.text.value;
            const errors = {};
            const rErr = Rules.rating(Number(rating));
            const tErr = Rules.text(text);
            if (rErr) errors.rating = rErr;
            if (tErr) errors.text = tErr;
            if (Object.keys(errors).length) { App.showErrors(form, errors); return; }

            const btn = form.querySelector('button[type="submit"]');
            App.loading(btn, true);
            const id = form.dataset.reviewForm;
            const { ok, data } = await App.api(`/api/requests/${id}/review`, { method: 'POST', body: { rating, text } });
            App.loading(btn, false);
            if (!ok) { App.showErrors(form, data.errors || { form: data.error }); return; }

            const box = document.createElement('div');
            box.className = 'review';
            const stars = document.createElement('span');
            stars.className = 'rating-view';
            stars.textContent = '★'.repeat(data.review.rating) + '☆'.repeat(5 - data.review.rating);
            const p = document.createElement('p');
            p.className = 'review__text';
            p.textContent = data.review.text;
            box.append(stars, p);
            form.replaceWith(box);
            App.toast(data.message);
        });
    });
});
