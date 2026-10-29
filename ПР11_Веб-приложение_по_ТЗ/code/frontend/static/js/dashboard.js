'use strict';

document.addEventListener('DOMContentLoaded', () => {
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
