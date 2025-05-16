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

