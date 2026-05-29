const fileInput = document.getElementById('fileInput');
const uploadBox = document.getElementById('uploadBox');
const processBtn = document.getElementById('processBtn');
const loader = document.getElementById('loader');
const results = document.getElementById('results');
const beforeImg = document.getElementById('beforeImg');
const afterImg = document.getElementById('afterImg');
const downloadBtn = document.getElementById('downloadBtn');

let selectedFile = null;

// Choisir une image
fileInput.addEventListener('change', (e) => {
    selectedFile = e.target.files[0];
    if (selectedFile) {
        const reader = new FileReader();
        reader.onload = (e) => {
            beforeImg.src = e.target.result;
            uploadBox.innerHTML = `
                <img src="${e.target.result}" class="preview-img" />
                <p style="margin-top:10px; color:#e2b96f">${selectedFile.name}</p>
            `;
            processBtn.disabled = false;
        };
        reader.readAsDataURL(selectedFile);
    }
});

// Drag & Drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = '#f5e642';
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.style.borderColor = '#e2b96f';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    selectedFile = e.dataTransfer.files[0];
    fileInput.files = e.dataTransfer.files;
    fileInput.dispatchEvent(new Event('change'));
});

// Traiter l'image
processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    // Afficher le loader
    loader.style.display = 'block';
    results.style.display = 'none';
    downloadBtn.style.display = 'none';
    processBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('image', selectedFile);

        const response = await fetch('http://127.0.0.1:8000/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.output) {
            afterImg.src = `data:${data.format};base64,${data.output}`;
            results.style.display = 'flex';
            downloadBtn.style.display = 'block';
        
            let analysisDiv = document.getElementById('analysis');
            if (!analysisDiv) {
                analysisDiv = document.createElement('div');
                analysisDiv.id = 'analysis';
                analysisDiv.style.cssText = `
                    background: rgba(226,185,111,0.1);
                    border: 1px solid #e2b96f;
                    border-radius: 12px;
                    padding: 15px 20px;
                    margin: 15px 0;
                    color: #e2b96f;
                    font-size: 1rem;
                    line-height: 1.6;
                `;
                downloadBtn.before(analysisDiv);
            }
            analysisDiv.innerHTML = `🤖 <strong>Analyse IA :</strong> ${data.analysis}`;
        } else {
            alert('Erreur lors du traitement. Réessaie.');
        }

    } catch (error) {
        alert('Erreur de connexion au serveur. Vérifie que le backend tourne.');
        console.error(error);
    } finally {
        loader.style.display = 'none';
        processBtn.disabled = false;
    }
});

// Télécharger l'image
downloadBtn.addEventListener('click', () => {
    const link = document.createElement('a');
    link.href = afterImg.src;
    link.download = 'image-restauree.png';
    link.click();
});