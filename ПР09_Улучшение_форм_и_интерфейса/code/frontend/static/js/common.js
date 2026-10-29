'use strict';

const App = (() => {
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';

    async function api(url, { method = 'GET', body } = {}) {
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf },
            body: body ? JSON.stringify(body) : undefined,
            credentials: 'same-origin',
        });
        let data = {};
        try { data = await res.json(); } catch (e) {  }
        return { ok: res.ok, status: res.status, data };
    }

    function showErrors(form, errors = {}) {
        clearErrors(form);
        Object.entries(errors).forEach(([name, text]) => {
            if (name === 'form') return;
            const box = form.querySelector(`[data-error-for="${name}"]`);
            if (box) {
                box.textContent = text;
                box.closest('.field')?.classList.add('has-error');
            }
        });
        const alert = form.querySelector('[data-form-alert]');
        if (alert && errors.form) {
            alert.textContent = errors.form;
            alert.hidden = false;
        }
        const first = form.querySelector('.has-error input, .has-error select, .has-error textarea');
        if (first) first.focus();
    }

    function clearErrors(form) {
        form.querySelectorAll('[data-error-for]').forEach((el) => { el.textContent = ''; });
        form.querySelectorAll('.has-error').forEach((el) => el.classList.remove('has-error'));
        const alert = form.querySelector('[data-form-alert]');
        if (alert) { alert.hidden = true; alert.textContent = ''; }
    }

    function setFieldState(input, error) {
        const field = input.closest('.field');
        const box = field?.querySelector('[data-error-for]');
        if (!field || !box) return;
        box.textContent = error || '';
        field.classList.toggle('has-error', Boolean(error));
        field.classList.toggle('is-valid', !error && input.value !== '');
    }

    function toast(text, type = 'info') {
        const box = document.querySelector('[data-toasts]');
        if (!box) return;
        const el = document.createElement('div');
        el.className = `toast${type === 'error' ? ' toast--error' : ''}`;
        el.textContent = text;
        box.appendChild(el);
        setTimeout(() => { el.classList.add('hide'); el.addEventListener('animationend', () => el.remove()); }, 3200);
    }

    function loading(btn, on) {
        btn.disabled = on;
        btn.classList.toggle('is-loading', on);
    }

    function go(url) {
        const page = document.querySelector('[data-page]');
        if (!page || matchMedia('(prefers-reduced-motion: reduce)').matches) { location.href = url; return; }
        page.classList.add('page-leave');
        setTimeout(() => { location.href = url; }, 170);
    }

    function formData(form) {
        return Object.fromEntries(new FormData(form).entries());
    }

    document.addEventListener('DOMContentLoaded', () => {
        const burger = document.querySelector('[data-burger]');
        burger?.addEventListener('click', () => {
            const open = document.body.classList.toggle('nav-open');
            burger.setAttribute('aria-expanded', String(open));
        });

        document.querySelectorAll('a[href^="/"]').forEach((a) => {
            a.addEventListener('click', (e) => {
                if (e.ctrlKey || e.metaKey || e.shiftKey || a.target) return;
                e.preventDefault();
                go(a.getAttribute('href'));
            });
        });

        document.querySelectorAll('[data-toggle-pwd]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const input = document.getElementById(btn.dataset.togglePwd);
                input.type = input.type === 'password' ? 'text' : 'password';
            });
        });
    });

    return { api, showErrors, clearErrors, setFieldState, toast, loading, go, formData };
})();
