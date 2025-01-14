
document.addEventListener('DOMContentLoaded', initializeOrderForm);

console.log('order form initialized');

function initializeOrderForm() {
    initializeItemManagement();
    initializeMapAndLocation();
}

function initializeItemManagement() {
    const state = {
        itemCount: 1,
        itemList: document.getElementById('item-list'),
        addItemButton: document.getElementById('add-item'),
        submitItemsButton: document.getElementById('submit-items'),
        outputDiv: document.getElementById("output")
    };

    state.addItemButton.addEventListener('click', () => addNewItem(state));
    state.itemList.addEventListener('click', (event) => {
        handleItemRemoval(event, state);
        handleAddItem(event, state);
    });
}

function addNewItem(state) {
    const newRow = createItemRow(state.itemCount, false);
    state.itemList.appendChild(newRow);
    state.itemCount++;
    updateButtonVisibility(state);
}

function handleAddItem(event, state) {
    const addButton = event.target.closest('.add-item');
    if (addButton) {
        addNewItem(state);
    }
}

function createItemRow(itemCount, isFirstRow = true) {
    const newRow = document.createElement('div');
    newRow.className = 'row mb-3';
    newRow.innerHTML = `
        <div class="col-md-5">
            <label for="item-name-${itemCount}" class="form-label">Item Name</label>
            <input type="text" class="form-control item-name" name="item-name-${itemCount}" placeholder="Enter item name" required>
        </div>
        <div class="col-6 col-md-3">
            <label for="item-qty-${itemCount}" class="form-label">Quantity</label>
            <input type="number" class="form-control item-qty" name="item-qty-${itemCount}" value="1" min="1" required>
        </div>
        <div class="col-6 col-md-4 d-flex align-items-end mt-1">
            ${isFirstRow ? `
            <button class="btn btn-primary me-2 add-item" type="button">
                <i class="fas fa-plus"></i>
            </button>` : ''}
            <button class="btn btn-danger remove-item" type="button">
                <i class="fas fa-minus"></i>
            </button>
        </div>
    `;
    return newRow;
}

function updateButtonVisibility(state) {
    const rows = state.itemList.querySelectorAll('.row');
    rows.forEach((row, index) => {
        const addButton = row.querySelector('.add-item');
        if (addButton) {
            if (index === 0) {
                addButton.style.display = 'block';
            } else {
                addButton.style.display = 'none';
            }
        }
    });
}
function handleItemRemoval(event, state) {
    const removeButton = event.target.closest('.remove-item');
    if (removeButton) {
        removeButton.closest('.row').remove();
        state.itemCount--;
        updateRemoveButtonState(state);
    }
}

function updateRemoveButtonState(state) {
    const firstRowRemoveButton = document.querySelector("#item-list .row:first-child .remove-item");
    if (firstRowRemoveButton) {
        firstRowRemoveButton.disabled = state.itemCount <= 1;
    }
}

function initializeMapAndLocation() {
    const mapConfig = {
        shopLocation: [22.767697, 88.541460], // Shop location
        defaultZoom: 16,
        tileLayerUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    };

    // Initialize map and shop marker
    const map = initializeMap(mapConfig);
    const shopMarker = L.marker(mapConfig.shopLocation, { draggable: false })
        .bindPopup('📍 Shop Location')
        .addTo(map);

    // Initialize user marker with default position
    const userMarker = addDraggableMarker(map);

    // Update inputs when user marker moves
    userMarker.on('moveend', (e) => {
        const { lat, lng } = e.target.getLatLng();
        document.getElementById('latitude').value = lat.toFixed(6);
        document.getElementById('longitude').value = lng.toFixed(6);
        updateRouting(map, mapConfig.shopLocation, [lat, lng]);
    });

    // Try to use geolocation for initial user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLocation = [position.coords.latitude, position.coords.longitude];
                userMarker.setLatLng(userLocation).update();
                map.setView(userLocation, mapConfig.defaultZoom);
                document.getElementById('latitude').value = userLocation[0].toFixed(6);
                document.getElementById('longitude').value = userLocation[1].toFixed(6);
                updateRouting(map, mapConfig.shopLocation, userLocation);
            },
            (error) => handleLocationError(error),
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    } else {
        handleLocationError({ message: 'Geolocation is not supported by your browser.' });
    }
}

function initializeMap(config) {
    const map = L.map('map').setView(config.shopLocation, config.defaultZoom);
    L.tileLayer(config.tileLayerUrl, {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    return map;
}

function addDraggableMarker(map) {
    const marker = L.marker([0, 0], { draggable: true }).addTo(map);
    marker.bindPopup('🚶 Drag to select your location').openPopup();
    return marker;
}

function handleLocationError(error) {
    console.error('Geolocation error:', error.message);
    alert('Unable to fetch location. Please enable location services.');
}


function updateRouting(map, shopLocation, userLocation) {
    if (map.routingControl) {
        map.removeControl(map.routingControl);
    }

    map.routingControl = L.Routing.control({
        waypoints: [L.latLng(shopLocation), L.latLng(userLocation)],
        routeWhileDragging: false,
        showAlternatives: true,
        createMarker: function (i, waypoint) {
            const icons = ['📍 Shop', '🚶 You'];
            return L.marker(waypoint.latLng).bindPopup(icons[i]);
        },
        lineOptions: {
            styles: [{ color: 'green', weight: 4 }] // Customize route line appearance
        },
        router: new L.Routing.OSRMv1({
            serviceUrl: 'https://router.project-osrm.org/route/v1', // Default OSRM server
            show: false // Disables the instruction box
        }),
        // addWaypoints: false, // Prevent adding additional waypoints
        // routeWhileDragging: false,
        itinerary: {
            containerClassName: 'hidden', // Hide instructions entirely
        },
    }).addTo(map);

    // Fetch and display travel times for different modes
    calculateTravelTimes(shopLocation, userLocation);
}

function calculateTravelTimes(shopLocation, userLocation) {
    const travelModes = ['walking', 'bicycling', 'driving'];

    travelModes.forEach((mode) => {
        console.log(`Calculating ${mode} travel time...`);
        // Simulate API call for travel time estimation
        const distance = calculateDistance(shopLocation, userLocation); // Approximation in km
        const speeds = { walking: 5, bicycling: 15, driving: 50 }; // Speeds in km/h
        const travelTime = (distance / speeds[mode]) * 60; // Time in minutes
        console.log(`${mode.charAt(0).toUpperCase() + mode.slice(1)}: ${travelTime.toFixed(2)} minutes`);
    });
}

function calculateDistance(coord1, coord2) {
    // Haversine formula for distance between two lat/lng points
    const toRad = (value) => (value * Math.PI) / 180;
    const R = 6371; // Earth's radius in km

    const dLat = toRad(coord2[0] - coord1[0]);
    const dLon = toRad(coord2[1] - coord1[1]);

    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRad(coord1[0])) * Math.cos(toRad(coord2[0])) * Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in km
}

// Initialize map and location functionality
// initializeMapAndLocation();


function updateTravelTimesDisplay(times) {
    document.getElementById('travel-times').innerHTML = `
        <p><strong>Walking:</strong> ${times.walking.toFixed(2)} minutes</p>
        <p><strong>Two-wheeler:</strong> ${times.twoWheeler.toFixed(2)} minutes</p>
    `;
}
