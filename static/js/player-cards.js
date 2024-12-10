document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.player-card');

    cards.forEach(card => {
        card.addEventListener('click', function() {
            // Primeiro, remova a classe 'selected' de todas as outras cartas
            cards.forEach(otherCard => {
                if (otherCard !== card) {
                    otherCard.classList.remove('selected');
                }
            });

            // Agora, alterne a classe 'selected' na carta clicada
            card.classList.toggle('selected');
        });
    });
});
