const API_URL = window.location.origin;

let currentLanguage = 'en';
let currentResults = null;
let breedChart = null;

const translations = {
    en: {
        title: 'Dog Breed Detector',
        subtitle: 'Detect dog breeds using AI',
        uploadText: 'Click or drag your image here',
        uploadSubtext: 'JPG, PNG, WebP supported',
        analyze: 'Analyze Image',
        analyzing: 'Analyzing...',
        chartTitle: 'Breed Distribution',
        download: 'Download Results',
        size: 'Size',
        temperament: 'Temperament',
        lifespan: 'Lifespan',
        origin: 'Origin',
        confidence: 'Confidence',
        error: 'Error analyzing image',
        noImage: 'Please select an image first',
        mixedBreed: 'Mixed Breed',
        tip1: 'Full body view',
        tip2: 'Well-lit photo',
        tip3: 'Neutral background',
        tip4: 'Distinctive features',
        forBetterResults: 'For better results'
    },
    es: {
        title: 'Detector de Razas de Perros',
        subtitle: 'Detecta razas de perros usando IA',
        uploadText: 'Haz clic o arrastra tu imagen aquí',
        uploadSubtext: 'JPG, PNG, WebP soportados',
        analyze: 'Analizar Imagen',
        analyzing: 'Analizando...',
        chartTitle: 'Distribución de Razas',
        download: 'Descargar Resultados',
        size: 'Tamaño',
        temperament: 'Temperamento',
        lifespan: 'Expectativa de vida',
        origin: 'Origen',
        confidence: 'Confianza',
        error: 'Error al analizar la imagen',
        noImage: 'Por favor selecciona una imagen primero',
        mixedBreed: 'Raza Mixta',
        tip1: 'Cuerpo completo',
        tip2: 'Bien iluminada',
        tip3: 'Fondo neutro',
        tip4: 'Características claras',
        forBetterResults: 'Para mejores resultados'
    }
};

// Traducción de razas
const breedTranslations = {
    'labrador retriever': 'Labrador Retriever',
    'golden retriever': 'Retriever Dorado',
    'german shepherd': 'Pastor Alemán',
    'french bulldog': 'Bulldog Francés',
    'bulldog': 'Bulldog',
    'poodle': 'Caniche',
    'beagle': 'Beagle',
    'husky': 'Husky Siberiano',
    'siberian husky': 'Husky Siberiano',
    'german shorthaired pointer': 'Pointer Alemán de Pelo Corto',
    'chihuahua': 'Chihuahua',
    'pug': 'Pug',
    'boxer': 'Boxer',
    'dachshund': 'Perro Salchicha',
    'corgi': 'Corgi',
    'pembroke': 'Corgi Pembroke',
    'shiba inu': 'Shiba Inu',
    'shiba': 'Shiba',
    'yorkshire terrier': 'Terrier de Yorkshire',
    'yorkshire': 'Terrier de Yorkshire',
    'great dane': 'Gran Danés',
    'bernese mountain dog': 'Perro de Montaña Bernés',
    'bernese mountain': 'Perro de Montaña Bernés',
    'dalmatian': 'Dálmata',
    'rottweiler': 'Rottweiler',
    'samoyed': 'Samoyedo',
    'cocker spaniel': 'Spaniel Cocker',
    'english setter': 'Setter Inglés',
    'greyhound': 'Galgo',
    'italian greyhound': 'Galgo Italiano',
    'australian shepherd': 'Pastor Australiano',
    'border collie': 'Border Collie',
    'collie': 'Collie',
    'maltese': 'Maltés',
    'pomeranian': 'Pomerania',
    'papillon': 'Papillon',
    'cavalier': 'Cavalier King Charles',
    'basset hound': 'Basset Hound',
    'bloodhound': 'Sabueso',
    'saint bernard': 'San Bernardo',
    'weimaraner': 'Weimaraner',
    'vizsla': 'Vizsla',
    'miniature schnauzer': 'Schnauzer Miniatura',
    'schnauzer': 'Schnauzer',
    'boston terrier': 'Boston Terrier',
    'jack russell terrier': 'Jack Russell Terrier',
    'shih tzu': 'Shih Tzu',
    'bichon frise': 'Bichon Frisé',
    'breed not detected': 'Raza No Detectada'
};

function translateBreedName(breedName, lang) {
    if (lang === 'es') {
        return breedTranslations[breedName.toLowerCase()] || breedName;
    }
    return breedName;
}

function t(key) {
    return translations[currentLanguage][key] || key;
}

function updateLanguage(lang) {
    currentLanguage = lang;
    document.documentElement.lang = lang;
    const title = document.getElementById('title');
    if (title) title.textContent = t('title');
    const subtitle = document.getElementById('subtitle');
    if (subtitle) subtitle.textContent = t('subtitle');
    const uploadText = document.getElementById('uploadText');
    if (uploadText) uploadText.textContent = t('uploadText');
    const uploadSubtext = document.getElementById('uploadSubtext');
    if (uploadSubtext) uploadSubtext.textContent = t('uploadSubtext');
    const analyzeBtnText = document.getElementById('analyzeBtnText');
    if (analyzeBtnText) analyzeBtnText.textContent = t('analyze');
    const analyzingText = document.getElementById('analyzingText');
    if (analyzingText) analyzingText.textContent = t('analyzing');
    const chartTitle = document.getElementById('chartTitle');
    if (chartTitle) chartTitle.textContent = t('chartTitle');
    const downloadBtnText = document.getElementById('downloadBtnText');
    if (downloadBtnText) downloadBtnText.textContent = t('download');

    // Tips
    const tip1 = document.getElementById('tip1');
    if (tip1) {
        tip1.textContent = t('tip1');
        document.getElementById('tip2').textContent = t('tip2');
        document.getElementById('tip3').textContent = t('tip3');
        document.getElementById('tip4').textContent = t('tip4');
    }

    // For better results
    const forBetterResults = document.getElementById('forBetterResults');
    if (forBetterResults) {
        forBetterResults.textContent = t('forBetterResults');
    }

    const detailLabels = {
        'sizeLabel': 'size',
        'temperamentLabel': 'temperament',
        'lifespanLabel': 'lifespan',
        'originLabel': 'origin'
    };

    Object.entries(detailLabels).forEach(([id, key]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = t(key);
    });
}

document.getElementById('langToggle').addEventListener('click', () => {
    currentLanguage = currentLanguage === 'en' ? 'es' : 'en';
    updateLanguage(currentLanguage);
});

const uploadZone = document.getElementById('uploadZone');
const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('previewImage');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsContainer = document.getElementById('resultsContainer');
const breedCardsContainer = document.getElementById('breedCardsContainer');
const downloadBtn = document.getElementById('downloadBtnText');

uploadZone.addEventListener('click', () => imageInput.click());

imageInput.addEventListener('change', handleImageSelect);

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        preview.style.display = 'block';
        previewImage.src = event.target.result;
        analyzeBtn.disabled = false;
        resultsContainer.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

analyzeBtn.addEventListener('click', analyzeImage);

async function analyzeImage() {
    if (!imageInput.files[0]) {
        alert(t('noImage'));
        return;
    }

    const reader = new FileReader();
    reader.onload = async (event) => {
        const base64Image = event.target.result;
        loadingSpinner.style.display = 'block';
        analyzeBtn.disabled = true;

        try {
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: base64Image })
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            if (data.success) {
                currentResults = data.breeds;
                displayResults(data.breeds);
            } else {
                alert(t('error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert(t('error'));
        } finally {
            loadingSpinner.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    };
    reader.readAsDataURL(imageInput.files[0]);
}

function displayResults(breeds) {
    resultsContainer.style.display = 'block';
    displayChart(breeds);
    displayBreedCards(breeds);
    window.scrollTo({ top: resultsContainer.offsetTop - 100, behavior: 'smooth' });
}

function displayChart(breeds) {
    const ctx = document.getElementById('breedChart').getContext('2d');
    if (breedChart) breedChart.destroy();

    // Paleta de colores variada y hermosa
    const colors = [
        '#FF6B6B', // Rojo coral
        '#4ECDC4', // Turquesa
        '#45B7D1', // Azul cielo
        '#FFA07A', // Salmón
        '#98D8C8', // Menta
        '#F7DC6F', // Amarillo cálido
        '#BB8FCE', // Púrpura lavanda
        '#85C1E2', // Azul pastel
        '#F8B88B', // Naranja pastel
        '#A8D8EA'  // Azul claro
    ];

    breedChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: breeds.map(b => b.breed),
            datasets: [{
                data: breeds.map(b => b.confidence),
                backgroundColor: colors.slice(0, breeds.length),
                borderColor: '#fff',
                borderWidth: 3,
                hoverBorderColor: '#333',
                hoverBorderWidth: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 12, weight: '500' },
                        padding: 15,
                        color: '#333',
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

function displayBreedCards(breeds) {
    breedCardsContainer.innerHTML = '';

    breeds.forEach(breed => {
        const template = document.getElementById('breedCardTemplate');
        const card = template.content.cloneNode(true);

        const img = card.querySelector('.breed-image');
        img.src = breed.image_url || 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22300%22%3E%3Crect fill=%22%23e8eef5%22 width=%22300%22 height=%22300%22/%3E%3C/svg%3E';
        img.alt = breed.breed;

        // Traducir nombre de raza
        const translatedBreed = translateBreedName(breed.breed, currentLanguage);
        card.querySelector('.breed-name').textContent = translatedBreed;
        card.querySelector('.confidence-badge').textContent = `${breed.confidence.toFixed(1)}%`;

        const chars = breed.characteristics || {};

        // Actualizar etiquetas con traducción
        card.querySelector('#sizeLabel').textContent = t('size');
        card.querySelector('#temperamentLabel').textContent = t('temperament');
        card.querySelector('#lifespanLabel').textContent = t('lifespan');
        card.querySelector('#originLabel').textContent = t('origin');

        // Llenar valores
        card.querySelector('.size-value').textContent = chars.size || 'Unknown';
        card.querySelector('.temperament-value').textContent = chars.temperament || 'Unknown';
        card.querySelector('.lifespan-value').textContent = chars.lifespan || 'Unknown';
        card.querySelector('.origin-value').textContent = chars.origin || 'Unknown';

        breedCardsContainer.appendChild(card);
    });
}

downloadBtn.addEventListener('click', downloadResults);

function downloadResults() {
    if (!currentResults) return;
    const csv = generateCSV(currentResults);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dog-breed-results-${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function generateCSV(breeds) {
    let csv = 'Breed,Confidence,Size,Temperament,Lifespan,Origin\n';
    breeds.forEach(breed => {
        const chars = breed.characteristics || {};
        csv += `"${breed.breed}",${breed.confidence.toFixed(2)},"${chars.size || 'Unknown'}","${chars.temperament || 'Unknown'}","${chars.lifespan || 'Unknown'}","${chars.origin || 'Unknown'}"\n`;
    });
    return csv;
}

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files[0]?.type.startsWith('image/')) {
        imageInput.files = files;
        handleImageSelect({ target: { files } });
    }
});
