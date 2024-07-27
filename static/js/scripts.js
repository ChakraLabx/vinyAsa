let scale = 1;
let minScale = 1;
let maxScale = 3;
const documentView = document.getElementById('document-view');
const zoomIn = document.getElementById('zoom-in');
const zoomOut = document.getElementById('zoom-out');
const resetZoom = document.getElementById('reset-zoom');
const documentName = document.getElementById('document-name');

function updateZoom() {
    documentView.style.transformOrigin = 'center center';
    documentView.style.transform = `scale(${scale})`;
    zoomOut.disabled = scale <= minScale;
    resetZoom.disabled = scale === minScale;
    zoomIn.enabled = scale >= maxScale;
}

zoomIn.addEventListener('click', () => {
    if (scale < maxScale) {
        scale = Math.min(scale * 1.2, maxScale);
        updateZoom();
    }
});

zoomOut.addEventListener('click', () => {
    if (scale > minScale) {
        scale = Math.max(scale / 1.2, minScale);
        updateZoom();
    }
});

resetZoom.addEventListener('click', () => {
    scale = 1;
    updateZoom();
    const container = document.getElementById('document-container');
    container.scrollTop = 0;
    container.scrollLeft = 0;
});

document.addEventListener("DOMContentLoaded", function() {
    const sampleSelector = document.getElementById("sample-selector");
    sampleSelector.value = "Security and Exchange Comission Filing";
});

document.getElementById('file-upload').addEventListener('change', function(e) {
    const fileName = e.target.files[0].name;
    document.getElementById('file-name').textContent = fileName;
});

document.getElementById('bulk-file-upload').addEventListener('change', function(e) {
    const files = e.target.files;
    const fileNames = Array.from(files).map(file => file.name).join(', ');
    document.getElementById('bulk-file-names').textContent = fileNames;

    if (files.length > 0) {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('bulk-files', files[i]);
        }

        // Implement bulk upload functionality here, e.g., using fetch or XMLHttpRequest
        fetch('/upload-bulk', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Bulk upload successful:', data);
            // Handle success, e.g., show a success message or download CSV
        })
        .catch(error => {
            console.error('Bulk upload error:', error);
            // Handle error, e.g., show an error message
        });
    }
});

function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    var formData = new FormData(this);
    fetch('/', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            updateResults(data);
        })
        .catch(error => console.error('Error:', error));
});

document.addEventListener('DOMContentLoaded', function() {
    var triggerTabList = [].slice.call(document.querySelectorAll('#right-panel .nav-link'))
    triggerTabList.forEach(function (triggerEl) {
      var tabTrigger = new bootstrap.Tab(triggerEl)
  
      triggerEl.addEventListener('click', function (event) {
        event.preventDefault()
        tabTrigger.show()
      })
    })
  })

function updateResults(data) {
    document.getElementById('RawText').innerHTML = `<pre>${JSON.stringify(data.raw_text, null, 2)}</pre>`;
    document.getElementById('Layout').innerHTML = `<pre>${JSON.stringify(data.layout, null, 2)}</pre>`;
    // Update other tabs similarly
}

window.onload = function() {
    fetch('/sample_document')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            document.getElementById('document-view').innerHTML = `<img src="/static/images/sd.png" alt="Sample Document" style="width:100%;">`;
            documentName.textContent = "Security and Exchange Comission Filing";
            
            // Wait for the image to load before setting the full view scale
            const img = documentView.querySelector('img');
            img.onload = setFullViewScale;
        })
        .catch(error => console.error('Error:', error));

    // Update document name when a new document is selected
    document.getElementById('sample-selector').addEventListener('change', function(e) {
        documentName.textContent = e.target.options[e.target.selectedIndex].text;
    });


    // Add functionality for download results button
    document.getElementById('download-results').addEventListener('click', function() {
        // Implement download functionality here
        console.log('Download results clicked');
    });

    // Add functionality for reset demo button
    document.getElementById('reset-demo').addEventListener('click', function() {
        // Implement reset functionality here
        console.log('Reset demo clicked');
    });

    // Add functionality for tab navigation buttons
    const tabContainer = document.querySelector('.tab');
    const prevTab = document.getElementById('prev-tab');
    const nextTab = document.getElementById('next-tab');

    prevTab.addEventListener('click', () => {
        tabContainer.scrollLeft -= 100;
    });

    nextTab.addEventListener('click', () => {
        tabContainer.scrollLeft += 100;
    });
}