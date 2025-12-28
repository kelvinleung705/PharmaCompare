/*
let map;
async function initMap() {
    const { Map } = (await google.maps.importLibrary('maps'));
    map = new Map(document.getElementById('map'), {
        center: { lat: 43.6584, lng: -79.3883 },
        zoom: 8,
    });
}
initMap();
*/
let map;
let infoWindow;
let activeMarkers = [];
async function initMap() {
    const { Map } = (await google.maps.importLibrary('maps'));

    map = new Map(document.getElementById('map'), {
        center: { lat: 43.6584, lng: -79.3883 },
        zoom: 10,
        //gestureHandling: "cooperative",
        mapId: 'YajuSenpaiGabaDaddy',
    });
    infoWindow = new google.maps.InfoWindow();
    const { AdvancedMarkerElement, PinElement  } = (await google.maps.importLibrary('marker'));
    const myPin = new PinElement({
        scale: 1.5,
    });
    const marker = new AdvancedMarkerElement({
        position: { lat: 43.6584, lng: -79.3883 },
    });
    marker.append(myPin);
    marker.map = map;
    //map.append(marker); dont use when map is a js object
    map.addListener("idle", () => {
        var bounds = map.getBounds();
        var ne = bounds.getNorthEast(); // North-East corner (LatLng object)
        var sw = bounds.getSouthWest(); // South-West corner (LatLng object)
        var northLat = ne.lat();
        const paragraphElement1 = document.getElementById("p1");
        paragraphElement1.textContent = northLat;
        var eastLng = ne.lng();
        const paragraphElement3 = document.getElementById("p3");
        paragraphElement3.textContent = eastLng;
        var southLat = sw.lat();
        const paragraphElement2 = document.getElementById("p2");
        paragraphElement2.textContent = southLat;
        var westLng = sw.lng();
        const paragraphElement4 = document.getElementById("p4");
        paragraphElement4.textContent = westLng;
        fetch(`/api/pharmacies?neLat=${ne.lat()}&neLng=${ne.lng()}&swLat=${sw.lat()}&swLng=${sw.lng()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(pharmacies => {
            console.log(`Received ${pharmacies.length} pharmacies.`);
                // 1. Clear markers from the previous view
                clearMarkers();
                // 2. Loop through the new pharmacy data and create markers
                pharmacies.forEach(pharmacy => {
                    addMarker(pharmacy);
            });
        });

    });


}
initMap();


function clearMarkers() {
    for (let i = 0; i < activeMarkers.length; i++) {
        activeMarkers[i].map = null; // To remove an AdvancedMarkerElement, set its map property to null
    }
    activeMarkers = []; // Empty the array for the next batch of markers
}


/**
 * Creates a marker for a single pharmacy and adds it to the map.
 * @param {object} pharmacy - A single pharmacy object from your API response.
 */
async function addMarker(pharmacy) {
    // We need to import the library again here if it's not in the global scope
    // or pass it as an argument. Let's pass it for cleanliness.
    if (!pharmacy.location || !pharmacy.location.coordinates) {
        return;
    }
    const { AdvancedMarkerElement, PinElement  } = (await google.maps.importLibrary('marker'));
    const myPin = new PinElement({
        scale: 1.5,
    });
    // --- FIX #1: Use the correct GeoJSON coordinates ---
    // Latitude is the SECOND element (index 1)
    // Longitude is the FIRST element (index 0)
    const position = {
        lat: pharmacy.location.coordinates[1],
        lng: pharmacy.location.coordinates[0]
    };
    const pharmacyPin = new PinElement({
        scale: 1.2,
    });
    const marker = new AdvancedMarkerElement({
        map: map,
        position: position,
        title: pharmacy["pharmacy name"], // Tooltip on hover
        content: pharmacyPin.element,
    });
    //marker.append(myPin); inefficient and pt into marker above
    marker.map = map;
    // Add the new marker to our array for tracking
    activeMarkers.push(marker);
    const googleMapsUrl = `https://www.google.com/maps?q=${pharmacy["pharmacy address"]}`;
    // Add a click listener to show the InfoWindow
    marker.addListener('click', () => {
        // Build the HTML content for the pop-up window

        const contentString = `
            <div id="infowindow-content">
                <h3>${pharmacy["pharmacy name"]}</h3>
                <p><strong>Address:</strong> ${pharmacy["pharmacy address"]}</p>
                <h3><strong>Processing Fee:</strong> $${pharmacy.fee.toFixed(2)}</h3>
                <p><strong>ID:</strong> ${pharmacy["pharmacy ident"]}</p>
                <a href="${googleMapsUrl}" target="_blank" rel="noopener noreferrer">View on Google Maps</a>
            </div>
        `;

        // Set the content on our single, reusable infoWindow
        infoWindow.setContent(contentString);

        // Open the infoWindow, anchored to the clicked marker
        infoWindow.open(map, marker);
    });
}



