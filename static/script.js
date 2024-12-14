document.getElementById("searchForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const query = document.getElementById("query").value;
    fetch(`http://127.0.0.1:5000/search?q=${query}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "";
            data.forEach(movie => {
                const movieDiv = document.createElement("div");
                movieDiv.innerHTML = `
                    <h2>${movie.title}</h2>
                    <p><strong>Year:</strong> ${movie.release_year}</p>
                    <p><strong>Director:</strong> ${movie.director}</p>
                    <p><strong>Plot:</strong> ${movie.plot}</p>
                    <p><strong>Genre:</strong> ${movie.genre}</p>
                    <p><a href="${movie.wiki_page}" target="_blank">Wiki Page</a></p>
                `;
                resultsDiv.appendChild(movieDiv);
            });
        });
});
