// static/js/map.js
document.addEventListener("DOMContentLoaded", function () {
  const mapContainer = document.getElementById("map");
  if (!mapContainer) return;

  const locations = JSON.parse(mapContainer.dataset.locations);

  const map = L.map("map").setView([20, 0], 2); // Centered globally
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a>',
  }).addTo(map);

  locations.forEach((loc) => {
    L.marker([loc.lat, loc.lng]).addTo(map).bindPopup(loc.name);
  });
});
