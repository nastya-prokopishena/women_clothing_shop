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
    // Знімаємо вибір за замовчуванням
    document.querySelectorAll('input[name="color"]').forEach(input => input.checked = false);
    document.querySelectorAll('input[name="size"]').forEach(input => input.checked = false);

    // Обробка вибору кольору
    document.querySelectorAll('.color-box').forEach(label => {
        label.addEventListener('click', () => {
            // Видаляємо вибір у всіх
            document.querySelectorAll('.color-box').forEach(l => l.classList.remove('selected'));

            // Встановлюємо checked відповідному input
            const input = document.getElementById(label.getAttribute('for'));
            input.checked = true;
            label.classList.add('selected');

            // Вивід вибраного кольору в консоль або на сторінку
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
});
