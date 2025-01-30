// Prevent main dropdown closure
$(document).on('click', '.dropdown-menu', function(e) {
    if ($(e.target).hasClass('dropdown-sublevel-button') || window.innerWidth <= 768) {
        e.stopPropagation();
    }
});

// Handle sublevel toggles
$(document).on('click', '.dropdown-sublevel-button', function(e) {
    e.preventDefault();
    e.stopPropagation();

    const $submenu = $(this).next('.dropdown-menu');
    const $currentDropdown = $(this).closest('.dropdown-menu');
    const $parentSublevel = $(this).closest('.dropdown-sublevel');

    // Cierra otros submenus en el mismo nivel
    $currentDropdown.find('.dropdown-sublevel > .dropdown-menu').not($submenu).removeClass('show')
        .prev('.dropdown-toggle').removeClass('active');
    $currentDropdown.find('.dropdown-sublevel').not($parentSublevel).removeClass('show');

    // Toggle clases para el submenu actual
    $(this).toggleClass('active');
    $submenu.toggleClass('show');
    $parentSublevel.toggleClass('show');
});

// Handle clicks on dropdown items with onclick
$(document).on('click', '.dropdown-sublevel .dropdown-menu .dropdown-item[onclick]', function(e) {
    if (window.innerWidth <= 768) {
        setTimeout(() => {
            $('.dropdown-sublevel').removeClass('show');
            $('.dropdown-sublevel .dropdown-menu').removeClass('show');
            $('.dropdown-sublevel-button').removeClass('active');
            $(this).closest('.dropdown-menu.show').removeClass('show');
        }, 100);
    }
});

// Close submenus when clicking outside
$(document).on('click', function(e) {
    if (!$(e.target).closest('.dropdown-sublevel').length) {
        $('.dropdown-sublevel').removeClass('show');
        $('.dropdown-sublevel .dropdown-menu').removeClass('show');
        $('.dropdown-sublevel-button').removeClass('active');
    }
});

// Cerrar submenus al cambiar el tamaño de la ventana
$(window).on('resize', function() {
    if (window.innerWidth <= 768) {
        $('.dropdown-sublevel').removeClass('show');
        $('.dropdown-sublevel .dropdown-menu').removeClass('show');
        $('.dropdown-sublevel-button').removeClass('active');
    }
});