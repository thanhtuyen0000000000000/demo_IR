async function search() {
    const query = document.getElementById("search-box").value;
    const res = await fetch(`http://127.0.0.1:5000/search?q=${query}`);
    const data = await res.json();

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = data.map(item => `
        <div class="result">
            <h2>${item.title}</h2>
            <p><strong>Genre:</strong> ${item.genre}</p>
            <p>${item.content}</p>
        </div>
    `).join("");
}
