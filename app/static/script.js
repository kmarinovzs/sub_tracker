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

document.getElementById('addButton').addEventListener('click', function() {
    const form = document.getElementById('formContainer');

    form.classList.toggle('d-none');
    this.classList.toggle("btn-pushed");

    this.textContent = form.classList.contains('d-none') ? 'Add Subscription' : 'Cancel'
});