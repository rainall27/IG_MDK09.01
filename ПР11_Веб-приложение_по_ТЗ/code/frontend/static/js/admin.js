'use strict';

document.addEventListener('DOMContentLoaded', () => {
    const list = document.querySelector('[data-admin-list]');
    const empty = document.querySelector('[data-admin-empty]');
    const filters = document.getElementById('filters');
    const statuses = JSON.parse(list.dataset.statuses);

    function el(tag, cls, text) {
        const node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text !== undefined && text !== null) node.textContent = text;
        return node;
    }

    function card(r) {
        const art = el('article', 'card card--hover req');
        art.dataset.requestId = r.id;
        art.dataset.testid = 'admin-request';

        const head = el('div', 'req__head');
        head.append(el('p', 'req__title', `№ ${r.id} · ${r.room}`),
            el('span', `badge badge--${r.status_id}`, r.status));

        const dl = el('dl', 'req__list');
        [['Пользователь', `${r.fio} (${r.login})`], ['Телефон', r.phone], ['Email', r.email],
            ['Начало', r.start_at], ['Оплата', r.payment_method], ['Подана', r.created_at.slice(0, 16)]]
            .forEach(([k, v]) => dl.append(el('dt', null, k), el('dd', null, v)));
        art.append(head, dl);

        const next = statuses.filter((s) => s.id > r.status_id);
        if (next.length) {
            const box = el('div', 'status-change');
            const sel = el('select');
            sel.setAttribute('aria-label', 'Новый статус');
            next.forEach((s) => { const o = el('option', null, s.name); o.value = s.id; sel.append(o); });
            const btn = el('button', 'btn btn--primary btn--sm', 'Сменить');
            btn.type = 'button';
            btn.addEventListener('click', () => changeStatus(r.id, sel.value, btn));
            box.append(sel, btn);
            art.append(box);
        }

        if (r.review_id) {
            const rev = el('div', 'review');
            rev.append(el('span', 'rating-view', '★'.repeat(r.review_rating) + '☆'.repeat(5 - r.review_rating)),
                el('p', 'review__text', r.review_text));
            art.append(rev);
        }
        return art;
    }

    function updateStats(stats) {
        Object.entries(stats).forEach(([id, cnt]) => {
            const b = document.querySelector(`[data-stat="${id}"]`);
            if (b && b.textContent !== String(cnt)) {
                b.textContent = cnt;
                b.classList.remove('bump'); void b.offsetWidth; b.classList.add('bump');
            }
        });
    }

    async function load() {
        const params = new URLSearchParams();
        new FormData(filters).forEach((v, k) => { if (v) params.append(k, v); });
        const { ok, data } = await App.api(`/api/admin/requests?${params}`);
        if (!ok) { App.toast(data.error || 'Ошибка загрузки', 'error'); return; }
        list.replaceChildren(...data.requests.map(card));
        empty.hidden = data.requests.length > 0;
        updateStats(data.stats);
    }

    async function changeStatus(id, statusId, btn) {
        App.loading(btn, true);
        const { ok, data } = await App.api(`/api/admin/requests/${id}/status`, { method: 'PATCH', body: { status_id: Number(statusId) } });
        App.loading(btn, false);
        if (!ok) { App.toast(data.error || 'Ошибка', 'error'); return; }
        App.toast(data.message);
        await load();
        list.querySelector(`[data-request-id="${id}"]`)?.classList.add('req--updated');
    }

    let timer;
    filters.addEventListener('input', (e) => {
        clearTimeout(timer);
        timer = setTimeout(load, e.target.name === 'q' ? 300 : 0);
    });
    filters.addEventListener('reset', () => setTimeout(load, 0));
    filters.addEventListener('submit', (e) => { e.preventDefault(); load(); });

    load();
});
