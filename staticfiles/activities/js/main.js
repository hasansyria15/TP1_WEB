// Script pour les effets dynamiques de AirLibre

// Animation de la navbar au scroll
document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', function () {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Animation des particules
    createParticles();

    // Activer les tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Activer les filtres d'activités
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });
});

// Fonction pour créer des particules dynamiquement
function createParticles() {
    const particlesContainer = document.querySelector('.particles');
    if (!particlesContainer) return;

    // Supprimer les particules statiques définies en HTML
    particlesContainer.innerHTML = '';

    // Créer des particules dynamiques
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';

        // Position aléatoire
        const left = Math.random() * 100;

        // Délai d'animation aléatoire
        const delay = Math.random() * 6;

        // Taille aléatoire
        const size = Math.random() * 5 + 2;

        particle.style.left = `${left}%`;
        particle.style.animationDelay = `${delay}s`;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;

        particlesContainer.appendChild(particle);
    }
}