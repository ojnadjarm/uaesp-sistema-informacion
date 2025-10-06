document.addEventListener('DOMContentLoaded', function() {
    console.log('Chart script loaded');
    console.log('Labels:', window.graficoMensualLabels);
    console.log('Datasets:', window.graficoMensualDatasets);
    
    if (typeof window.graficoMensualLabels !== 'undefined' && typeof window.graficoMensualDatasets !== 'undefined') {
        const canvas = document.getElementById('graficoMensual');
        if (canvas) {
            console.log('Canvas found, creating chart');
            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: window.graficoMensualLabels,
                    datasets: window.graficoMensualDatasets
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { 
                            display: true,
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                padding: 20,
                                font: {
                                    size: 11
                                }
                            }
                        }
                    },
                    scales: {
                        y: { 
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Toneladas'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Mes'
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
        } else {
            console.error('Canvas element not found');
        }
    } else {
        console.error('Chart data not available');
        console.log('Labels type:', typeof window.graficoMensualLabels);
        console.log('Datasets type:', typeof window.graficoMensualDatasets);
    }
});