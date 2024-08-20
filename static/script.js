async function fetchData() {
    const response = await fetch('/ecg-data');
    if (!response.ok) {
        console.error('No new data available');
        return;
    }
    const data = await response.json();
    plotData(data.data);
}

function plotData(data) {
    const container = document.getElementById('plot');
    container.innerHTML = '';  // Clear previous plots
    Object.keys(data).forEach(leadId => {
        const card = document.createElement('div');
        card.className = 'plot-card';

        const div = document.createElement('div');
        div.className = 'plot';
        div.id = `plot_${leadId}`;
        card.appendChild(div);

        container.appendChild(card);

        const trace = {
            x: Array.from(Array(data[leadId].length).keys()),
            y: data[leadId],
            type: 'scatter',
            name: `Lead ${leadId}`
        };

        const layout = {
            title: `Lead ${leadId}`,
            xaxis: { title: 'Time' },
            yaxis: { title: 'Amplitude' },
            margin: { l: 30, r: 30, t: 30, b: 30 },
            autosize: true,
            responsive: true
        };

        Plotly.newPlot(div.id, [trace], layout);
    });
}

setInterval(fetchData, 1000);
