setInterval(() => {
  const alerts = document.querySelectorAll('.alert');

  alerts.forEach((alert) => {
    // Sprawdza, czy już jest ustawiony timer na zamykanie
    if (!alert.dataset.timerSet) {
      alert.dataset.timerSet = 'true';

      const closeBtn = alert.querySelector('.alert__close');

      // Obsługa zamknięcia przez użytkownika
      if (closeBtn) {
        closeBtn.addEventListener('click', () => {
          alert.style.display = 'none';
        });
      }

      // Automatyczne zamknięcie po 5 sekundach
      setTimeout(() => {
        alert.style.display = 'none';
      }, 5000);
    }
  });
}, 1000);