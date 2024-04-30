document.addEventListener('DOMContentLoaded', function () {
    var socket = io();

    // Listen for updates from the server
    socket.on('update_progress', function (data) {
        var progressBar = document.getElementById('progress-bar');
        progressBar.value = data.progress;
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const selectedImagesContainer = document.getElementById('selected-images');
    const numPhotosPerListingInput = document.querySelector('input[name="num_photos"]');
    let numPhotosPerListing = parseInt(numPhotosPerListingInput.value);
    const fileInput = document.getElementById('file-input');
    let openDropdown = null;

    numPhotosPerListingInput.addEventListener('change', function () {
        numPhotosPerListing = parseInt(this.value);
        displaySelectedImages(fileInput.files);
    });

    fileInput.addEventListener('change', function () {
        displaySelectedImages(this.files);
    });

    // Initialize Sortable.js for the main list
    const sortableMain = new Sortable(selectedImagesContainer, {
        animation: 150,
        handle: '.selected-image',
    });

    function displaySelectedImages(files) {
        selectedImagesContainer.innerHTML = '';
        const numGroups = Math.ceil(files.length / numPhotosPerListing);

        for (let i = 0; i < numGroups; i++) {
            const groupContainer = document.createElement('div');
            groupContainer.className = 'image-group';

            const toggleButton = document.createElement('button');
            toggleButton.className = 'dropdown-toggle';
            toggleButton.innerText = `Product ${i + 1}`;

            const dropdownContent = document.createElement('div');
            dropdownContent.className = 'dropdown-content';

            for (let j = i * numPhotosPerListing; j < (i + 1) * numPhotosPerListing && j < files.length; j++) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(files[j]);
                img.classList.add('selected-image');

                // Append image to dropdown content
                dropdownContent.appendChild(img);
            }

            // Append toggle button and dropdown content to group container
            groupContainer.appendChild(toggleButton);
            groupContainer.appendChild(dropdownContent);

            // Append group container to the main list
            selectedImagesContainer.appendChild(groupContainer);

            // Event listener for toggling the drop-down
            toggleButton.addEventListener('click', function (event) {
                event.preventDefault(); // Prevent button click from triggering form submission

                if (openDropdown && openDropdown !== dropdownContent) {
                    // Close the currently open dropdown
                    openDropdown.classList.remove('show');
                    openDropdown.previousElementSibling.innerText = `Product ${i + 1}`;
                }

                // Toggle the current dropdown
                dropdownContent.classList.toggle('show');
                const isExpanded = dropdownContent.classList.contains('show');
                toggleButton.innerText = isExpanded ? 'Collapse' : `Product ${i + 1}`;

                // Update the currently open dropdown
                openDropdown = isExpanded ? dropdownContent : null;
            });

            // Initialize Sortable.js for the dropdown content
            const sortableDropdown = new Sortable(dropdownContent, {
                animation: 150,
                handle: '.selected-image',
            });
        }
    }
});






