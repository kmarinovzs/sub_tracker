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

document.querySelectorAll('.edit-btn').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();

        const subId = this.getAttribute('data-id');

        const edit = document.getElementById(`editContainer${subId}`);

        if (edit) {
            edit.classList.toggle('d-none');
        } else {
            console.error(`Could not find element: editContainer${subId}`);
        }

    });
});