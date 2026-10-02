// ==========================================
// EMERGENCY LOCATION
// ==========================================

function getCurrentLocation() {

    const locationInput =
        document.getElementById("location");

    const latitudeInput =
        document.getElementById("latitude");

    const longitudeInput =
        document.getElementById("longitude");

    const locationStatus =
        document.getElementById("location-status");


    // ==========================================
    // CHECK GEOLOCATION SUPPORT
    // ==========================================

    if (!navigator.geolocation) {

        locationStatus.textContent =
            "⚠️ GPS detection is not supported. Please enter your location manually.";

        locationStatus.style.color =
            "#dc2626";

        return;
    }


    // ==========================================
    // SHOW LOADING MESSAGE
    // ==========================================

    locationStatus.textContent =
        "📍 Trying to detect your current location...";

    locationStatus.style.color =
        "#2563eb";


    locationInput.value =
        "Detecting location...";


    // ==========================================
    // REQUEST LOCATION
    // ==========================================

    navigator.geolocation.getCurrentPosition(

        function(position) {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;


            // ==========================================
            // SAVE GPS COORDINATES
            // ==========================================

            latitudeInput.value =
                latitude;

            longitudeInput.value =
                longitude;


            // ==========================================
            // SHOW LOCATION
            // ==========================================

            locationInput.value =
                "GPS: " +
                latitude.toFixed(6) +
                ", " +
                longitude.toFixed(6);


            locationStatus.textContent =
                "✅ GPS location detected successfully.";

            locationStatus.style.color =
                "#16a34a";

        },


        function(error) {

            console.log(
                "GPS Error Code:",
                error.code
            );

            console.log(
                "GPS Error Message:",
                error.message
            );


            // Clear failed GPS values

            latitudeInput.value = "";

            longitudeInput.value = "";


            // ==========================================
            // HANDLE ERRORS
            // ==========================================

            if (error.code === 1) {

                locationStatus.textContent =
                    "⚠️ Location permission was denied. Please enter your location manually.";

            }

            else if (error.code === 2) {

                locationStatus.textContent =
                    "⚠️ Your device could not determine your location. Please enter your location manually.";

            }

            else if (error.code === 3) {

                locationStatus.textContent =
                    "⚠️ Location detection timed out. Please enter your location manually.";

            }

            else {

                locationStatus.textContent =
                    "⚠️ GPS detection failed. Please enter your location manually.";

            }


            locationStatus.style.color =
                "#dc2626";


            // ==========================================
            // RESTORE MANUAL INPUT
            // ==========================================

            locationInput.value = "";

            locationInput.placeholder =
                "Enter city, area or landmark";

        },

        {

            enableHighAccuracy: false,

            timeout: 20000,

            maximumAge: 60000

        }

    );

}