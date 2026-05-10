fetch("/chart-data")
    .then(res => res.json())
    .then(data => {

        const ctx = document.getElementById('myChart');

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values
                }]
            }
        });

    });