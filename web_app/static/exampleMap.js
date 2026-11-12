// set up map and marker group
var map = L.map('map').setView([51.505, -0.09], 13);
var currentMarkerGroup = L.featureGroup()
currentMarkerGroup.addTo(map)
var charitiesToShow = []

const form = document.querySelector("#locinfo");

//Receive form data, retrieve all charities within radius and siaplay as circle markers, convert postcode to coordinates and display as marker, and a circle indicating radius
async function sendLocation() {
  const formData = new FormData(form);
  console.log(formData.get("loc"))
  
  try {
    const response = fetch(`${SCRIPT_ROOT}/mapApi/loc`, {
      method: "POST",
      body: formData,
    }).then(resp => resp.json()).then(d => {console.log(d);
      // adding services in radius to map
       charitiesToShow = d; 
       addCharitiesToMap(d); 
       // convert postcode to lat-long coordinates
       fetch(`${SCRIPT_ROOT}/convert/${formData.get("loc")}`).then(resp => resp.json()).then(d => {
        // add pointer marker of searched location
        currentMarkerGroup.addLayer(L.marker([d[1], d[2]]));
        // add boundary of search radius
        const boundary = new L.Circle([d[1], d[2]], {radius: formData.get("dist")*1000, color:"#0000FF", fillOpacity:0.01 });
        currentMarkerGroup.addLayer(boundary)
        boundary.bringToBack()
        // Recenter map on search radius
        map.flyToBounds(currentMarkerGroup.getBounds())
        
    }); 
  })
    
    
  } catch (e) {
    console.error(e);
  }
}

// Add listener to form submit button
form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendLocation();
});

// Adds a charity marker to map for each service in list. Uses same card as list view
function addCharitiesToMap(data){
    // remove previous markers and regenerate
    currentMarkerGroup.clearLayers()
    let charityMarkers = L.markerClusterGroup();
    for (let d of data) {
        console.log(d)
        if (d.latitude && d.longitude) {
            // add circle marker for service - may be nice to change to zone marker is possible
            let m = new L.CircleMarker([d.latitude, d.longitude], {radius:25, color:"#FF0000", fillColor:"#FF0000"})
            charityMarkers.addLayer(m)
            // add card pop up with description. Only include distance is searched
            let dist = "distance" in d ? `<br> ${(d.distance/1000).toFixed(2)}km away`: ''
            m.bindPopup(`<div onclick="location.href='${SCRIPT_ROOT}/charity/${d.charity_id}';" style="cursor: pointer;">
                <h3>${d.charity_name}</h3>
                <a href='${d.url}' class="popup-link"> ${d.url} </a>
                <br>
                <br>
                ${d.location_name} ${dist}
                <br>
                <br>
                ${d.summary}
                <br>

                </div>`)

        }
    } 

    // ensure all added to map
    currentMarkerGroup.addLayer(charityMarkers)
    map.addLayer(currentMarkerGroup)  
}

// add map
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// add all charities onto map originally
fetch(allCharitiesURL).then(resp => resp.json()).then(d => {charitiesToShow = d; addCharitiesToMap(d)})