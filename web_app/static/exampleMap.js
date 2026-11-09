const form = document.querySelector("#locinfo");

async function sendLocation() {
  const formData = new FormData(form);
  console.log(formData.get("loc"))
  
  try {
    const response = fetch(`${SCRIPT_ROOT}/mapApi/loc`, {
      method: "POST",
      body: formData,
    }).then(resp => resp.json()).then(d => {console.log(d); charitiesToShow = d; addCharitiesToMap(d); })
    const searchLoc = fetch(`${SCRIPT_ROOT}/convert/${formData.get("loc")}`).then(resp => resp.json()).then(d => {
      console.log(d); 
      currentMarkerGroup.addLayer(L.marker([d[1], d[2]]));
      const boundary = new L.Circle([d[1], d[2]], {radius: formData.get("dist")*1000, color:"#0000FF", fillOpacity:0.01 });
      currentMarkerGroup.addLayer(boundary)
      boundary.bringToBack()
      map.setView([d[1], d[2]])
    });
  } catch (e) {
    console.error(e);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendLocation();
});

var map = L.map('map').setView([51.505, -0.09], 13);
var currentMarkerGroup = L.layerGroup()
currentMarkerGroup.addTo(map)
var charitiesToShow = []

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

fetch(allCharitiesURL).then(resp => resp.json()).then(d => {charitiesToShow = d; addCharitiesToMap(d)})

/*var marker = L.marker([51.5, -0.09]).addTo(map);
var marker2 = L.marker([51.508, -0.11]).addTo(map);

var circle = L.circle([51.5, -0.09], {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5,
    radius: 500
}).addTo(map);

marker.bindPopup("<b>Hello world!</b><br>I am a popup.").openPopup();
*/

function addCharitiesToMap(data){
    console.log("updated")
    currentMarkerGroup.clearLayers()
    let charityMarkers = L.markerClusterGroup();
    for (let d of data) {
        // need to sort data for new filter - not in JSON format
        if (d.latitude && d.longitude) {
            let m = new L.CircleMarker([d.latitude, d.longitude], {radius:25, color:"#FF0000", fillColor:"#FF0000"})
            charityMarkers.addLayer(m)
            m.bindPopup(`<div onclick="location.href='${SCRIPT_ROOT}/charity/${d.charity_id}';" style="cursor: pointer;">
                <h3>${d.charity_name}</h3>
                <a href='${d.url}' class="popup-link"> ${d.url} </a>
                <br>
                <br>
                ${d.location_name}
                <br>
                <br>
                ${d.summary}
                <br>

                </div>`)

        }
    } 
    currentMarkerGroup.addLayer(charityMarkers)
    map.addLayer(currentMarkerGroup)  
}
