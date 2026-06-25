(function () {
    'use strict';

    const container = document.getElementById('spa-container');
    const pageBody = document.getElementById('body');
    if (!container || !window.fetch || !window.DOMParser || !window.history) return;

    let isNavigating = false;
    document.documentElement.dataset.spaReady = 'true';

    function isWeddingPage(url) {
        if (url.origin !== window.location.origin) return false;
        if (url.hash && url.pathname === window.location.pathname) return false;
        if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/static/') || url.pathname.startsWith('/media/')) return false;
        return /^\/(\d+\/|kitchen\/\d+\/|singers\/\d+\/)$/.test(url.pathname);
    }

    function executePageScripts(doc) {
        const scriptsRoot = doc.getElementById('spa-extra-scripts');
        if (!scriptsRoot) return;

        scriptsRoot.querySelectorAll('script').forEach(function (oldScript) {
            const script = document.createElement('script');

            Array.prototype.forEach.call(oldScript.attributes, function (attribute) {
                script.setAttribute(attribute.name, attribute.value);
            });

            if (oldScript.src) {
                script.src = oldScript.src;
            } else {
                script.textContent = oldScript.textContent;
            }

            document.body.appendChild(script);
            script.remove();
        });
    }

    function updateActiveLinks() {
        const currentPath = window.location.pathname;
        container.querySelectorAll('#header li.active').forEach(function (item) {
            item.classList.remove('active');
        });
        container.querySelectorAll('#header a[href]').forEach(function (link) {
            const url = new URL(link.getAttribute('href'), window.location.href);
            if (url.pathname === currentPath) {
                const item = link.closest('li');
                if (item) item.classList.add('active');
                link.setAttribute('aria-current', 'page');
            } else {
                link.removeAttribute('aria-current');
            }
        });
    }

    function getLinkFromEvent(event) {
        if (event.currentTarget && event.currentTarget.matches && event.currentTarget.matches('a[href]')) {
            return event.currentTarget;
        }

        const target = event.target && event.target.nodeType === 1
            ? event.target
            : event.target && event.target.parentElement;
        if (!target || !target.closest) return null;

        return target.closest('a[href]');
    }

    function handleSpaClick(event) {
        const link = getLinkFromEvent(event);
        if (!link) return;
        if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        if (link.target && link.target !== '_self') return;

        const url = new URL(link.getAttribute('href'), window.location.href);
        if (!isWeddingPage(url)) return;

        event.preventDefault();
        event.stopPropagation();
        document.documentElement.dataset.spaClick = String(
            Number(document.documentElement.dataset.spaClick || 0) + 1
        );

        if (url.pathname === window.location.pathname) {
            window.scrollTo({top: 0, behavior: 'smooth'});
            return;
        }

        loadPage(url);
    }

    function bindSpaLinks(root) {
        root.querySelectorAll('a[href]').forEach(function (link) {
            const url = new URL(link.getAttribute('href'), window.location.href);
            if (!isWeddingPage(url) || link.dataset.spaBound === 'true') return;
            link.dataset.spaBound = 'true';
            link.addEventListener('click', handleSpaClick, true);
        });
    }

    async function loadPage(url, options) {
        if (isNavigating) return;
        isNavigating = true;
        const shouldPush = !options || options.push !== false;

        pageBody.classList.add('spa-is-loading');

        try {
            const response = await fetch(url.href, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-SPA-Navigation': '1'
                },
                credentials: 'same-origin'
            });

            if (!response.ok) throw new Error('Page load failed');

            const html = await response.text();
            const doc = new DOMParser().parseFromString(html, 'text/html');
            const nextContainer = doc.getElementById('spa-container');
            if (!nextContainer) throw new Error('SPA container not found');

            container.innerHTML = nextContainer.innerHTML;
            document.title = doc.title || document.title;

            if (shouldPush) {
                window.history.pushState({spa: true}, '', url.href);
            }

            updateActiveLinks();
            bindSpaLinks(container);
            document.documentElement.dataset.spaNavigated = String(
                Number(document.documentElement.dataset.spaNavigated || 0) + 1
            );

            try {
                executePageScripts(doc);
            } catch (scriptError) {
                window.console && window.console.error && window.console.error('SPA page script error', scriptError);
            }

            window.scrollTo({top: 0, behavior: 'smooth'});
        } catch (error) {
            document.documentElement.dataset.spaError = error && error.message ? error.message : String(error);
            try {
                window.sessionStorage.setItem('weddingSpaLastError', error && error.message ? error.message : String(error));
            } catch (storageError) {}
            window.console && window.console.error && window.console.error('SPA navigation fallback', error);
            window.location.href = url.href;
        } finally {
            window.setTimeout(function () {
                pageBody.classList.remove('spa-is-loading');
                isNavigating = false;
            }, 180);
        }
    }

    document.addEventListener('click', handleSpaClick, true);

    window.addEventListener('popstate', function () {
        const url = new URL(window.location.href);
        if (isWeddingPage(url)) {
            loadPage(url, {push: false});
        }
    });

    updateActiveLinks();
    bindSpaLinks(container);
}());
