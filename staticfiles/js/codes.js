function deleteProject(event, deleteUrl) {
    event.preventDefault();

    Swal.fire({
        title: 'Czy na pewno chcesz usunąć ten projekt?',
        text: "Nie będziesz mógł tego cofnąć!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: getComputedStyle(document.documentElement).getPropertyValue('--color-success'),
        cancelButtonColor: getComputedStyle(document.documentElement).getPropertyValue('--color-error'),
        confirmButtonText: 'Tak, usuń to!',
        cancelButtonText: 'Nie, żartowałem!'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = deleteUrl;
        }
    });
}

function deleteCode(event, deleteUrl) {
    event.preventDefault();

    Swal.fire({
        title: 'Czy na pewno chcesz usunąć ten kod ?',
        text: "Nie będziesz mógł tego cofnąć!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: getComputedStyle(document.documentElement).getPropertyValue('--color-success'),
        cancelButtonColor: getComputedStyle(document.documentElement).getPropertyValue('--color-error'),
        confirmButtonText: 'Tak, usuń to!',
        cancelButtonText: 'Nie, żartowałem!'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = deleteUrl;
        }
    });
}