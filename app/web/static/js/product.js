const thumbnails = document.querySelectorAll('.thumbnail');
const mainImage = document.getElementById('main-image');

thumbnails.forEach(thumbnail => {
    thumbnail.addEventListener('click', () => {
        mainImage.src = thumbnail.src;
    });
});

// Скрипт для акордіонів
document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
        const accordion = header.parentElement;
        const isActive = accordion.classList.contains('active');

        document.querySelectorAll('.accordion').forEach(a => {
            a.classList.remove('active');
            a.querySelector('.accordion-content').style.maxHeight = '0';
            a.querySelector('.accordion-icon').style.transform = 'rotate(0deg)';
        });

        if (!isActive) {
            accordion.classList.add('active');
            const content = accordion.querySelector('.accordion-content');
            content.style.maxHeight = content.scrollHeight + 'px';
            accordion.querySelector('.accordion-icon').style.transform = 'rotate(90deg)';
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Скидання вибору за замовчуванням
    document.querySelectorAll('input[name="color"]').forEach(input => input.checked = false);
    document.querySelectorAll('input[name="size"]').forEach(input => input.checked = false);

    // Обробка вибору кольору
    document.querySelectorAll('.color-box').forEach(label => {
        label.addEventListener('click', () => {
            document.querySelectorAll('.color-box').forEach(l => l.classList.remove('selected'));
            const input = document.getElementById(label.getAttribute('for'));
            input.checked = true;
            label.classList.add('selected');
            console.log('Обраний колір:', input.value);
        });
    });

    // Обробка вибору розміру
    document.querySelectorAll('.size-button').forEach(label => {
        label.addEventListener('click', () => {
            document.querySelectorAll('.size-button').forEach(l => l.classList.remove('selected'));
            const input = document.getElementById(label.getAttribute('for'));
            input.checked = true;
            label.classList.add('selected');
            console.log('Обраний розмір:', input.value);
        });
    });

    // ===== Нова валідація рейтингу при надсиланні коментаря =====
    const form = document.getElementById("comment-form");
    const warning = document.getElementById("rating-warning");

    if (form) {
        form.addEventListener("submit", function (e) {
            const ratingSelected = form.querySelector('input[name="rating"]:checked');
            if (!ratingSelected) {
                e.preventDefault();
                if (warning) {
                    warning.style.display = "block";
                    warning.textContent = "Будь ласка, поставте оцінку перед відправленням коментаря.";
                }
            } else {
                if (warning) {
                    warning.style.display = "none";
                }
            }
        });

        const ratingInputs = form.querySelectorAll('input[name="rating"]');
        ratingInputs.forEach((input) => {
            input.addEventListener("change", function () {
                if (warning && warning.style.display === "block") {
                    warning.style.display = "none";
                }
            });
        });
    }
});
