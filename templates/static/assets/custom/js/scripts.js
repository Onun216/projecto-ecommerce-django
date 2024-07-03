(function () {
    select_variation = document.getElementById('select-variations');
    variation_price = document.getElementById('variation-price');
    variation_price_promotional = document.getElementById('variation-price-promotional');

    if (!select_variation) {
        return;
    }

    if (!variation_price) {
        return;
    }

    select_variation.addEventListener('change', function () {
        price = this.options[this.selectedIndex].getAttribute('data-price');
        price_promotional = this.options[this.selectedIndex].getAttribute('data-price-promotional');

        if (price && variation_price) {
            variation_price.innerHTML = price;
        }

        if (variation_price_promotional && price_promotional) {
            variation_price_promotional.innerHTML = price_promotional;
        } else {
            variation_price_promotional.innerHTML = price;
            variation_price.innerHTML = '';

        }             
    })
})();

