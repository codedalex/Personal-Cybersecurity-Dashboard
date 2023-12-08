    // locationHistoryTimeline.js

    // Function to create a timeline chart for location history
    function createLocationHistoryTimeline(containerId, locationHistory) {
        // Parse timestamp strings to Date objects
        locationHistory.forEach(entry => {
            entry.timestamp = new Date(entry.timestamp);
        });

        // Create a DataSet with the data
        var timelineData = new vis.DataSet(
            locationHistory.map(entry => ({
                id: entry.timestamp,
                content: entry.location,
                start: entry.timestamp,
            }))
        );

        // Set up the timeline options
        var options = {
            height: '300px',
            showCurrentTime: false,
            zoomMax: 31536000000, // 1 year
            format: {
                minorLabels: {
                    minute: 'h:mma',
                    hour: 'ha',
                },
            },
        };

        // Create the timeline
        var timeline = new vis.Timeline(document.getElementById(containerId), timelineData, options);
    }