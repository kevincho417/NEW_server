function updatePlots() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            Object.keys(data).forEach((lead, index) => {
                Plotly.react(`leadPlot-${lead}`, [{
                    y: data[lead],
                    type: 'scatter',
                    mode: 'lines'
                }], {
                    title: `Lead ${lead}`
                });
            });
        })
        .catch(error => console.error('Error fetching ECG data:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    setInterval(updatePlots, 2000);  // Update the plots every 2 seconds
});
