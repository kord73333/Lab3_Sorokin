/* AJAX-поиск, редактирование и удаление записей из базы данных. */

(function () {
    'use strict';

    const searchInput = document.getElementById('search-input');
    if (!searchInput || !window.MOVIE_SEARCH_URL) {
        return;
    }

    const tbody = document.getElementById('movies-tbody');
    const status = document.getElementById('search-status');
    const noResults = document.getElementById('no-results');
    const clearButton = document.getElementById('search-clear');
    const DEBOUNCE_MS = 300;

    let debounceTimer = null;

    function ratingClass(rating) {
        if (rating >= 7) return 'bg-success';
        if (rating >= 4) return 'bg-warning text-dark';
        return 'bg-danger';
    }

    function buildRow(movie, index) {
        const row = document.createElement('tr');
        row.dataset.id = movie.id;

        const cells = [
            { text: String(index + 1) },
            { text: movie.title, className: 'fw-semibold' },
            { text: movie.director },
            { text: String(movie.year) },
            { badge: movie.genre, badgeClass: 'bg-secondary' },
            { badge: String(movie.rating), badgeClass: ratingClass(movie.rating) },
            { text: movie.created_at, className: 'text-muted small' },
        ];

        cells.forEach(function (cell) {
            const td = document.createElement('td');
            if (cell.className) {
                td.className = cell.className;
            }
            if (cell.badge !== undefined) {
                const span = document.createElement('span');
                span.className = 'badge ' + cell.badgeClass;
                span.textContent = cell.badge;
                td.appendChild(span);
            } else {
                td.textContent = cell.text;
            }
            row.appendChild(td);
        });

        row.appendChild(buildActionsCell(movie));
        return row;
    }

    function buildActionsCell(movie) {
        const td = document.createElement('td');
        td.className = 'text-end text-nowrap';

        const editLink = document.createElement('a');
        editLink.href = movieUrl(window.MOVIE_EDIT_URL, movie.id);
        editLink.className = 'btn btn-sm btn-outline-primary';
        editLink.title = 'Редактировать';
        editLink.innerHTML = '<i class="bi bi-pencil"></i>';

        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'btn btn-sm btn-outline-danger ms-1';
        deleteButton.title = 'Удалить';
        deleteButton.innerHTML = '<i class="bi bi-trash"></i>';
        deleteButton.addEventListener('click', function () {
            deleteMovie(movie.id, movie.title);
        });

        td.appendChild(editLink);
        td.appendChild(deleteButton);
        return td;
    }

    function movieUrl(template, id) {
        return template.replace('/0/', '/' + id + '/');
    }

    function renderResults(movies) {
        tbody.innerHTML = '';
        if (!movies.length) {
            noResults.classList.remove('d-none');
            return;
        }
        noResults.classList.add('d-none');
        movies.forEach(function (movie, index) {
            tbody.appendChild(buildRow(movie, index));
        });
    }

    function runSearch() {
        const query = searchInput.value.trim();
        const url = window.MOVIE_SEARCH_URL + '?q=' + encodeURIComponent(query);

        fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin',
        })
            .then(function (response) {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(function (data) {
                renderResults(data.results);
                status.textContent = query
                    ? 'Найдено записей: ' + data.count
                    : 'Введите текст для поиска по записям в базе данных.';
            })
            .catch(function () {
                status.textContent = 'Ошибка при выполнении поиска.';
            });
    }

    function deleteMovie(id, title) {
        if (!window.confirm('Удалить фильм «' + title + '» из базы данных?')) {
            return;
        }
        fetch(movieUrl(window.MOVIE_DELETE_URL, id), {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.MOVIE_CSRF_TOKEN,
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        })
            .then(function (response) {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                window.location.reload();
            })
            .catch(function () {
                window.alert('Не удалось удалить запись.');
            });
    }

    searchInput.addEventListener('input', function () {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(runSearch, DEBOUNCE_MS);
    });

    if (clearButton) {
        clearButton.addEventListener('click', function () {
            searchInput.value = '';
            runSearch();
            searchInput.focus();
        });
    }

    document.querySelectorAll('.delete-form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            const title = form.dataset.title || '';
            if (!window.confirm('Удалить фильм «' + title + '» из базы данных?')) {
                event.preventDefault();
            }
        });
    });
})();
