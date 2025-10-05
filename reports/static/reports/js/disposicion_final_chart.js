document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.graficoMensualLabels !== 'undefined' && typeof window.graficoMensualData !== 'undefined') {
        const ctx = document.getElementById('graficoMensual').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: window.graficoMensualLabels,
                datasets: [{
                    label: 'Residuos (toneladas)',
                    data: window.graficoMensualData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
});