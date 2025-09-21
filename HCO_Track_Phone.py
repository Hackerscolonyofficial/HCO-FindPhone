<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HCO Track Phone</title>
    <style>
        body {
            background: #000;
            color: #0f0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: Arial, sans-serif;
            font-size: 18px;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .message {
            margin-bottom: 20px;
        }
        .coords {
            margin-top: 20px;
            font-size: 16px;
            color: #0ff;
        }
        button {
            background: #0f0;
            color: #000;
            border: none;
            padding: 12px 24px;
            font-size: 18px;
            border-radius: 6px;
            cursor: pointer;
            margin: 20px 0;
            font-weight: bold;
        }
        button:hover {
            background: #0c0;
        }
    </style>
</head>
<body>
    <div class="message">HCO Track Phone Location Access</div>
    <div id="status">Click the button below to enable location tracking</div>
    <button id="enableBtn">Enable Location Tracking</button>
    <div id="coords" class="coords"></div>

    <script>
        const enableBtn = document.getElementById('enableBtn');
        const statusDiv = document.getElementById('status');
        const coordsDiv = document.getElementById('coords');
        let watchId = null;

        function onSuccess(pos) {
            try {
                statusDiv.innerHTML = 'Location access granted! Tracking active...';
                coordsDiv.innerHTML = `Lat: ${pos.coords.latitude.toFixed(6)}<br>Lon: ${pos.coords.longitude.toFixed(6)}<br>Accuracy: ${pos.coords.accuracy}m`;
                
                fetch('/update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        lat: pos.coords.latitude,
                        lon: pos.coords.longitude,
                        accuracy: pos.coords.accuracy,
                        heading: pos.coords.heading || null,
                        speed: pos.coords.speed || null,
                        timestamp: pos.timestamp
                    })
                }).catch(err => console.error('Error:', err));
            } catch(e) {
                console.error('Error:', e);
            }
        }
        
        function onError(err) {
            statusDiv.innerHTML = `Error: ${err.message}`;
            if (watchId) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }
            console.error('Geolocation error:', err);
        }
        
        function enableLocation() {
            if (navigator.geolocation) {
                statusDiv.innerHTML = 'Requesting location access...';
                
                // First try to get current position
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        onSuccess(pos);
                        // Then watch for updates
                        watchId = navigator.geolocation.watchPosition(onSuccess, onError, {
                            enableHighAccuracy: true,
                            maximumAge: 3000,
                            timeout: 10000
                        });
                    }, 
                    onError, 
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            } else {
                statusDiv.innerHTML = 'Geolocation is not supported by this browser.';
            }
        }
        
        // Add click event to button
        enableBtn.addEventListener('click', enableLocation);
    </script>
</body>
</html>
