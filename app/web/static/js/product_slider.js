let autoScrollInterval;

function slideFeatured(direction) {
    const slider = document.getElementById('featured-products-slider');
    const productCard = document.querySelector('#featured-products-slider .product-card');
    const scrollAmount = productCard ? productCard.offsetWidth + 15 : 200;
    const scrollWidth = slider.scrollWidth;
    const clientWidth = slider.clientWidth;
    const currentScroll = slider.scrollLeft;

    resetAutoScroll();

    if (direction === 'prev') {
        if (currentScroll <= 0) {
            slider.scrollTo({
                left: scrollWidth - clientWidth,
                behavior: 'smooth'
            });
        } else {
            slider.scrollBy({
                left: -scrollAmount,
                behavior: 'smooth'
            });
        }
    } else {
        if (currentScroll + clientWidth >= scrollWidth - 1) {
            slider.scrollTo({
                left: 0,
                behavior: 'smooth'
            });
        } else {
            slider.scrollBy({
                left: scrollAmount,
                behavior: 'smooth'
            });
        }
    }

    startAutoScroll();
}

function startAutoScroll() {
    resetAutoScroll();

    autoScrollInterval = setInterval(() => {
        slideFeatured('next');
    }, 2000);
}

function resetAutoScroll() {
    if (autoScrollInterval) {
        clearInterval(autoScrollInterval);
        autoScrollInterval = null;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('featured-products-slider');

    document.querySelector('.slider-prev').addEventListener('click', () => slideFeatured('prev'));
    document.querySelector('.slider-next').addEventListener('click', () => slideFeatured('next'));

    let isDown = false;
    let startX;
    let scrollLeft;

    slider.addEventListener('mousedown', (e) => {
        isDown = true;
        startX = e.pageX - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
        resetAutoScroll();
    });

    slider.addEventListener('mouseleave', () => {
        isDown = false;
    });

    slider.addEventListener('mouseup', () => {
        isDown = false;
        startAutoScroll();
    });

    slider.addEventListener('mousemove', (e) => {
        if(!isDown) return;
        e.preventDefault();
        const x = e.pageX - slider.offsetLeft;
        const walk = (x - startX) * 2;
        slider.scrollLeft = scrollLeft - walk;
    });

    startAutoScroll();

    slider.addEventListener('mouseenter', resetAutoScroll);
    slider.addEventListener('mouseleave', startAutoScroll);
});

document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('reviews-slider');
    let scrollInterval;
    let isPaused = false;

    function startAutoScroll() {
        scrollInterval = setInterval(() => {
            if (isPaused) return;

            const scrollWidth = slider.scrollWidth;
            const clientWidth = slider.clientWidth;
            const currentScroll = slider.scrollLeft;

            if (currentScroll + clientWidth >= scrollWidth - 1) {
                slider.scrollTo({ left: 0, behavior: 'smooth' });
            } else {
                slider.scrollBy({ left: 320, behavior: 'smooth' });
            }
        }, 3000);
    }

    function pauseAutoScroll() {
        isPaused = true;
        setTimeout(() => isPaused = false, 10000);
    }

    startAutoScroll();

    slider.addEventListener('mouseenter', () => isPaused = true);
    slider.addEventListener('mouseleave', () => isPaused = false);

    slider.addEventListener('touchstart', () => isPaused = true);
    slider.addEventListener('touchend', () => {
        setTimeout(() => isPaused = false, 3000);
    });
});