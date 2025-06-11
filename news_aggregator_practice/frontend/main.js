let allArticles = [];

const filterSelect = document.getElementById("filter-select");
const tableBody = document.querySelector("#articles-table tbody");
const canvasCtx = document.getElementById("sentiment-chart").getContext("2d");

async function loadData() {
  try {
    const fetchRes = await fetch(`${API_BASE}/fetch/${STUDENT_ID}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (!fetchRes.ok) throw new Error(`Fetch error: ${fetchRes.status} ${fetchRes.statusText}`);

    const analyzeRes = await fetch(`${API_BASE}/analyze/${STUDENT_ID}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (!analyzeRes.ok) throw new Error(`Analyze error: ${analyzeRes.status} ${analyzeRes.statusText}`);

    const data = await analyzeRes.json();
    if (!data.articles || !Array.isArray(data.articles)) throw new Error("Invalid response format: missing articles array");

    allArticles = data.articles.map(a => ({
      ...a,
      date: a.published ? new Date(a.published) : new Date()
    }));

    render();
  } catch (err) {
    console.error("Error loading data:", err);
    alert("Помилка при завантаженні новин або аналізі тональності. Перевірте авторизацію або статус сервера.");
  }
}

function render() {
  const filter = filterSelect.value;
  const filtered = allArticles.filter(a => filter === "all" ? true : a.sentiment === filter);

  tableBody.innerHTML = filtered
    .sort((a, b) => b.date - a.date)
    .map(a => `
      <tr>
        <td>${a.date.toLocaleString()}</td>
        <td>${a.sentiment}</td>
        <td><a href="${a.link}" target="_blank">${a.title}</a></td>
      </tr>
    `).join("");

  const counts = { positive: 0, neutral: 0, negative: 0 };
  filtered.forEach(a => counts[a.sentiment]++);

  chart.data.datasets[0].data = [
    counts.positive,
    counts.neutral,
    counts.negative
  ];
  chart.update();
}

const chart = new Chart(canvasCtx, {
  type: 'pie',
  data: {
    labels: ['Позитивні', 'Нейтральні', 'Негативні'],
    datasets: [{
      data: [0, 0, 0],
      backgroundColor: ['#4caf50', '#ffca28', '#f44336']
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
      legend: { position: 'top' }
    }
  }
});

filterSelect.addEventListener("change", render);

window.addEventListener("load", loadData);