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
async function initMap() {
    const { Map } = (await google.maps.importLibrary('maps'));
    const { AdvancedMarkerElement, PinElement  } = (await google.maps.importLibrary('marker'));
    map = new Map(document.getElementById('map'), {
        center: { lat: 43.6584, lng: -79.3883 },
        zoom: 10,
        mapId: 'YajuSenpaiGabaDaddy',
    });
    const myPin = new PinElement({
        scale: 1.5,
    });
    const marker = new AdvancedMarkerElement({
        position: { lat: 43.6584, lng: -79.3883 },
    });
    marker.append(myPin);
    marker.map = map;
    map.append(marker);

}
initMap();


