 // locationHistoryMap.js
 $(window).on('load', function() {
    createLocationHistoryMap('location-history-map');
  });
  

 function createLocationHistoryMap(containerId, locationHistory) {
    // Initialize the map
    var map = L.map(containerId).setView([0, 0], 2);
  
    // Add the base map layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
    }).addTo(map);
  
    // Add markers for each location
    locationHistory.forEach(entry => {
      L.marker([entry.latitude, entry.longitude])
        .addTo(map)
        .bindPopup(entry.location);
    });
  
    // Add the map to the DOM once the element exists
    $('#location-history-map').once('DOMContentLoaded', function() {
      map.addTo(this);
    });

    // Create the #location-history-map element
    $('<div id="location-history-map" style="height: 300px;"></div>').appendTo('.col-md-6');

    // Call the createLocationHistoryMap() function
    createLocationHistoryMap('location-history-map', locationHistory);
    

  }
  



