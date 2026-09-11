from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import requests
import logging
from dotenv import load_dotenv
import torch
import torchvision.models as models
import torchvision.transforms as transforms

load_dotenv()

# Establecer directorio de caché con permisos (compatible con Windows y Linux)
import tempfile
torch_cache_dir = os.path.join(tempfile.gettempdir(), 'torch_models')
os.environ['TORCH_HOME'] = torch_cache_dir
os.makedirs(torch_cache_dir, exist_ok=True)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load ImageNet classes
IMAGENET_CLASSES = []
try:
    with open('imagenet_classes.txt', 'r') as f:
        IMAGENET_CLASSES = [line.strip() for line in f.readlines()]
except:
    logger.warning("No se pudo cargar imagenet_classes.txt")
    IMAGENET_CLASSES = ['dog'] * 1000

logger.info("Cargando modelo MobileNetV2...")
try:
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
except:
    model = models.mobilenet_v2(pretrained=True)
model.eval()

# Pre-cargar modelo para evitar cold start
logger.info("Pre-cargando modelo en memoria...")
with torch.no_grad():
    dummy_input = torch.randn(1, 3, 224, 224)
    model(dummy_input)
logger.info("✓ MobileNetV2 cargado y listo")

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

DOG_BREEDS_KEYWORDS = [
    'retriever', 'german shepherd', 'labrador', 'bulldog', 'poodle',
    'beagle', 'husky', 'chihuahua', 'corgi', 'boxer', 'dalmatian',
    'golden', 'french bulldog', 'dachshund', 'terrier', 'spaniel',
    'shepherd', 'setter', 'hound', 'mastiff', 'shiba', 'maltese',
    'pug', 'schnauzer', 'collie', 'greyhound', 'pomeranian'
]

# Mapping exacto de razas a formato Dog CEO API
BREED_ALIASES = {
    'labrador retriever': 'labrador',
    'labrador': 'labrador',
    'golden retriever': 'retriever/golden',
    'retriever golden': 'retriever/golden',
    'golden': 'retriever/golden',
    'german shepherd': 'german/shepherd',
    'germanshepherd': 'german/shepherd',
    'shepherd german': 'german/shepherd',
    'german': 'german/shepherd',
    'shepherd': 'german/shepherd',
    'french bulldog': 'bulldog/french',
    'bulldog french': 'bulldog/french',
    'french': 'bulldog/french',
    'bulldog': 'bulldog',
    'poodle': 'poodle',
    'beagle': 'beagle',
    'husky': 'husky',
    'siberian husky': 'husky',
    'siberian': 'husky',
    'german shorthaired pointer': 'pointer/german',
    'pointer german': 'pointer/german',
    'pointer': 'pointer/german',
    'german pointer': 'pointer/german',
    'chihuahua': 'chihuahua',
    'pug': 'pug',
    'boxer': 'boxer',
    'dachshund': 'dachshund',
    'corgi': 'corgi',
    'pembroke corgi': 'corgi',
    'pembroke': 'corgi',
    'cardigan corgi': 'corgi',
    'cardigan': 'corgi',
    'shiba inu': 'shiba',
    'shiba': 'shiba',
    'yorkshire terrier': 'terrier/yorkshire',
    'yorkshire': 'terrier/yorkshire',
    'great dane': 'dane/great',
    'dane': 'dane/great',
    'greatdane': 'dane/great',
    'bernese mountain dog': 'mountain/bernese',
    'bernese mountain': 'mountain/bernese',
    'mountain bernese': 'mountain/bernese',
    'dalmatian': 'dalmatian',
    'rottweiler': 'rottweiler',
    'samoyed': 'samoyed',
    'cocker spaniel': 'spaniel/cocker',
    'cocker': 'spaniel/cocker',
    'english setter': 'setter/english',
    'english': 'setter/english',
    'setter': 'setter/english',
    'greyhound': 'greyhound',
    'italian greyhound': 'greyhound/italian',
    'australian shepherd': 'australian/shepherd',
    'australian': 'australian/shepherd',
    'border collie': 'collie/border',
    'bordercollie': 'collie/border',
    'border': 'collie/border',
    'collie': 'collie',
    'rough collie': 'collie',
    'maltese': 'maltese',
    'pomeranian': 'pomeranian',
    'papillon': 'papillon',
    'ibizan hound': 'hound/ibizan',
    'ibizan': 'hound/ibizan',
    'cavalier king charles': 'cavalier/kingcharles',
    'king charles': 'cavalier/kingcharles',
    'basset hound': 'hound/basset',
    'basset': 'hound/basset',
    'bloodhound': 'hound/blood',
    'saint bernard': 'stbernard',
    'st bernard': 'stbernard',
    'bernese': 'bernese',
    'weimaraner': 'weimaraner',
    'vizsla': 'vizsla',
    'english springer': 'springer/english',
    'springer': 'springer/english',
    'springer spaniel': 'springer/english',
    'miniature schnauzer': 'schnauzer/miniature',
    'schnauzer': 'schnauzer/miniature',
    'boston terrier': 'terrier/boston',
    'boston': 'terrier/boston',
    'jack russell terrier': 'terrier/russell',
    'shih tzu': 'shihtzu',
    'shih': 'shihtzu',
    'maltese dog': 'maltese',
    'bichon': 'frise/bichon',
    'bichon frise': 'frise/bichon',
    'american staffordshire terrier': 'staffordshire/american',
    'american staffordshire': 'staffordshire/american',
    'amstaff': 'staffordshire/american'
}

BREED_CHARACTERISTICS = {
    'labrador retriever': {
        'size': 'Large',
        'temperament': 'Friendly, Outgoing, Loyal',
        'lifespan': '10-12 years',
        'origin': 'Canada'
    },
    'labrador': {
        'size': 'Large',
        'temperament': 'Friendly, Outgoing, Loyal',
        'lifespan': '10-12 years',
        'origin': 'Canada'
    },
    'golden retriever': {
        'size': 'Large',
        'temperament': 'Intelligent, Devoted, Kind',
        'lifespan': '10-12 years',
        'origin': 'Scotland'
    },
    'german shepherd': {
        'size': 'Large',
        'temperament': 'Confident, Courageous, Obedient',
        'lifespan': '9-13 years',
        'origin': 'Germany'
    },
    'french bulldog': {
        'size': 'Small',
        'temperament': 'Playful, Alert, Affectionate',
        'lifespan': '10-14 years',
        'origin': 'France'
    },
    'bulldog': {
        'size': 'Medium',
        'temperament': 'Dignified, Courageous, Gentle',
        'lifespan': '8-12 years',
        'origin': 'England'
    },
    'poodle': {
        'size': 'Medium to Large',
        'temperament': 'Intelligent, Active, Elegant',
        'lifespan': '12-15 years',
        'origin': 'Germany/France'
    },
    'beagle': {
        'size': 'Small to Medium',
        'temperament': 'Merry, Curious, Determined',
        'lifespan': '12-15 years',
        'origin': 'England'
    },
    'husky': {
        'size': 'Large',
        'temperament': 'Energetic, Intelligent, Mischievous',
        'lifespan': '12-15 years',
        'origin': 'Siberia'
    },
    'siberian husky': {
        'size': 'Large',
        'temperament': 'Energetic, Intelligent, Mischievous',
        'lifespan': '12-15 years',
        'origin': 'Siberia'
    },
    'chihuahua': {
        'size': 'Toy',
        'temperament': 'Alert, Courageous, Devoted',
        'lifespan': '14-18 years',
        'origin': 'Mexico'
    },
    'boxer': {
        'size': 'Large',
        'temperament': 'Playful, Loyal, Protective',
        'lifespan': '10-12 years',
        'origin': 'Germany'
    },
    'dachshund': {
        'size': 'Small',
        'temperament': 'Clever, Courageous, Devoted',
        'lifespan': '14-16 years',
        'origin': 'Germany'
    },
    'corgi': {
        'size': 'Small',
        'temperament': 'Affectionate, Intelligent, Loving',
        'lifespan': '12-14 years',
        'origin': 'Wales'
    },
    'shiba inu': {
        'size': 'Small to Medium',
        'temperament': 'Lively, Bold, Independent',
        'lifespan': '13-16 years',
        'origin': 'Japan'
    },
    'pug': {
        'size': 'Small',
        'temperament': 'Charming, Mischievous, Loving',
        'lifespan': '12-15 years',
        'origin': 'China'
    },
    'maltese': {
        'size': 'Toy',
        'temperament': 'Affectionate, Gentle, Playful',
        'lifespan': '12-15 years',
        'origin': 'Mediterranean'
    },
    'yorkshire terrier': {
        'size': 'Toy',
        'temperament': 'Confident, Courageous, Affectionate',
        'lifespan': '13-16 years',
        'origin': 'England'
    },
    'german shorthaired pointer': {
        'size': 'Large',
        'temperament': 'Intelligent, Versatile, Willing',
        'lifespan': '10-12 years',
        'origin': 'Germany'
    },
    'cocker spaniel': {
        'size': 'Medium',
        'temperament': 'Gentle, Happy, Willing',
        'lifespan': '12-15 years',
        'origin': 'Spain'
    },
    'english setter': {
        'size': 'Large',
        'temperament': 'Good-natured, Affectionate, Eager',
        'lifespan': '11-12 years',
        'origin': 'England'
    },
    'great dane': {
        'size': 'Giant',
        'temperament': 'Gentle, Loving, Alert',
        'lifespan': '7-10 years',
        'origin': 'Germany'
    },
    'bernese mountain dog': {
        'size': 'Large',
        'temperament': 'Loyal, Affectionate, Intelligent',
        'lifespan': '7-10 years',
        'origin': 'Switzerland'
    },
    'dalmatian': {
        'size': 'Large',
        'temperament': 'Energetic, Playful, Outgoing',
        'lifespan': '11-13 years',
        'origin': 'Croatia'
    },
    'rottweiler': {
        'size': 'Large',
        'temperament': 'Loyal, Courageous, Confident',
        'lifespan': '8-11 years',
        'origin': 'Germany'
    },
    'samoyed': {
        'size': 'Large',
        'temperament': 'Friendly, Gentle, Devoted',
        'lifespan': '12-14 years',
        'origin': 'Russia'
    },
    'australian shepherd': {
        'size': 'Medium to Large',
        'temperament': 'Smart, Work-Oriented, Excellent herder',
        'lifespan': '12-18 years',
        'origin': 'United States'
    },
    'border collie': {
        'size': 'Medium',
        'temperament': 'Intelligent, Energetic, Herding instinct',
        'lifespan': '12-15 years',
        'origin': 'Scotland'
    },
    'greyhound': {
        'size': 'Large',
        'temperament': 'Gentle, Quiet, Athletic',
        'lifespan': '10-13 years',
        'origin': 'England'
    },
    'ibizan hound': {
        'size': 'Large',
        'temperament': 'Athletic, Elegant, Energetic',
        'lifespan': '11-14 years',
        'origin': 'Spain'
    },
    'pomeranian': {
        'size': 'Toy',
        'temperament': 'Lively, Bold, Inquisitive',
        'lifespan': '12-16 years',
        'origin': 'Germany'
    },
    'papillon': {
        'size': 'Toy',
        'temperament': 'Alert, Intelligent, Friendly',
        'lifespan': '13-15 years',
        'origin': 'France/Belgium'
    },
    'cavalier king charles': {
        'size': 'Small',
        'temperament': 'Affectionate, Gentle, Graceful',
        'lifespan': '12-15 years',
        'origin': 'England'
    },
    'basset hound': {
        'size': 'Medium',
        'temperament': 'Scent-driven, Stubborn, Affectionate',
        'lifespan': '12-13 years',
        'origin': 'France'
    },
    'bloodhound': {
        'size': 'Large',
        'temperament': 'Determined, Single-minded, Friendly',
        'lifespan': '10-12 years',
        'origin': 'Belgium'
    },
    'saint bernard': {
        'size': 'Giant',
        'temperament': 'Gentle, Massive, Watchful',
        'lifespan': '8-10 years',
        'origin': 'Switzerland'
    },
    'weimaraner': {
        'size': 'Large',
        'temperament': 'Alert, Obedient, Energetic',
        'lifespan': '10-13 years',
        'origin': 'Germany'
    },
    'vizsla': {
        'size': 'Medium',
        'temperament': 'Affectionate, Energetic, Gentle',
        'lifespan': '12-15 years',
        'origin': 'Hungary'
    },
    'boston terrier': {
        'size': 'Small',
        'temperament': 'Affectionate, Lively, Intelligent',
        'lifespan': '11-15 years',
        'origin': 'United States'
    },
    'jack russell terrier': {
        'size': 'Small',
        'temperament': 'Energetic, Fearless, Bold',
        'lifespan': '13-16 years',
        'origin': 'England'
    },
    'shih tzu': {
        'size': 'Toy',
        'temperament': 'Affectionate, Friendly, Playful',
        'lifespan': '10-18 years',
        'origin': 'China'
    },
    'bichon frise': {
        'size': 'Toy',
        'temperament': 'Cheerful, Playful, Affectionate',
        'lifespan': '12-15 years',
        'origin': 'Mediterranean'
    },
    'miniature schnauzer': {
        'size': 'Small',
        'temperament': 'Alert, Spirited, Intelligent',
        'lifespan': '12-14 years',
        'origin': 'Germany'
    },
    'springer spaniel': {
        'size': 'Medium',
        'temperament': 'Obedient, Willing, Active',
        'lifespan': '12-14 years',
        'origin': 'England'
    },
    'mastiff': {
        'size': 'Giant',
        'temperament': 'Calm, Dignified, Generous',
        'lifespan': '6-10 years',
        'origin': 'England'
    },
    'italian greyhound': {
        'size': 'Toy',
        'temperament': 'Affectionate, Playful, Lively',
        'lifespan': '12-15 years',
        'origin': 'Italy'
    },
    'collie': {
        'size': 'Large',
        'temperament': 'Intelligent, Loyal, Dignified',
        'lifespan': '14-16 years',
        'origin': 'Scotland'
    },
    'terrier': {
        'size': 'Small to Medium',
        'temperament': 'Brave, Energetic, Tenacious',
        'lifespan': '12-15 years',
        'origin': 'Various'
    },
    'spaniel': {
        'size': 'Medium',
        'temperament': 'Friendly, Obedient, Willing',
        'lifespan': '12-14 years',
        'origin': 'Spain'
    },
    'hound': {
        'size': 'Medium to Large',
        'temperament': 'Independent, Scent-driven, Loyal',
        'lifespan': '10-13 years',
        'origin': 'Various'
    },
    'setter': {
        'size': 'Large',
        'temperament': 'Intelligent, Eager, Gentle',
        'lifespan': '11-14 years',
        'origin': 'Europe'
    },
    'retriever': {
        'size': 'Large',
        'temperament': 'Friendly, Intelligent, Active',
        'lifespan': '10-12 years',
        'origin': 'Canada/Scotland'
    },
    'pinscher': {
        'size': 'Small to Medium',
        'temperament': 'Alert, Spirited, Intelligent',
        'lifespan': '12-15 years',
        'origin': 'Germany'
    },
    'airedale terrier': {
        'size': 'Large',
        'temperament': 'Courageous, Confident, Intelligent',
        'lifespan': '11-14 years',
        'origin': 'England'
    },
    'pit bull': {
        'size': 'Medium to Large',
        'temperament': 'Courageous, Confident, Strong-willed',
        'lifespan': '12-14 years',
        'origin': 'United States'
    },
    'american staffordshire terrier': {
        'size': 'Medium to Large',
        'temperament': 'Confident, Courageous, Intelligent',
        'lifespan': '12-16 years',
        'origin': 'United States'
    },
    'american staffordshire': {
        'size': 'Medium to Large',
        'temperament': 'Confident, Courageous, Intelligent',
        'lifespan': '12-16 years',
        'origin': 'United States'
    },
}

# Traducción de nombres de razas al español
BREED_TRANSLATIONS = {
    'labrador retriever': 'Labrador Retriever',
    'labrador': 'Labrador',
    'golden retriever': 'Retriever Dorado',
    'german shepherd': 'Pastor Alemán',
    'french bulldog': 'Bulldog Francés',
    'bulldog': 'Bulldog',
    'poodle': 'Caniche',
    'beagle': 'Beagle',
    'husky': 'Husky Siberiano',
    'siberian husky': 'Husky Siberiano',
    'german shorthaired pointer': 'Pointer Alemán de Pelo Corto',
    'pointer': 'Pointer',
    'chihuahua': 'Chihuahua',
    'pug': 'Pug',
    'boxer': 'Boxer',
    'dachshund': 'Perro Salchicha',
    'corgi': 'Corgi',
    'pembroke': 'Corgi Pembroke',
    'cardigan': 'Corgi Cardigan',
    'shiba inu': 'Shiba Inu',
    'shiba': 'Shiba',
    'yorkshire terrier': 'Terrier de Yorkshire',
    'yorkshire': 'Terrier de Yorkshire',
    'great dane': 'Gran Danés',
    'dane': 'Gran Danés',
    'bernese mountain dog': 'Perro de Montaña Bernés',
    'bernese mountain': 'Perro de Montaña Bernés',
    'bernese': 'Perro de Montaña Bernés',
    'dalmatian': 'Dálmata',
    'rottweiler': 'Rottweiler',
    'samoyed': 'Samoyedo',
    'cocker spaniel': 'Spaniel Cocker',
    'cocker': 'Spaniel Cocker',
    'english setter': 'Setter Inglés',
    'english': 'Inglés',
    'setter': 'Setter',
    'greyhound': 'Galgo',
    'italian greyhound': 'Galgo Italiano',
    'ibizan hound': 'Podenco Ibicenco',
    'australian shepherd': 'Pastor Australiano',
    'australian': 'Australiano',
    'border collie': 'Border Collie',
    'bordercollie': 'Border Collie',
    'border': 'Border Collie',
    'collie': 'Collie',
    'rough collie': 'Collie',
    'maltese': 'Maltés',
    'pomeranian': 'Pomerania',
    'papillon': 'Papillon',
    'cavalier': 'Cavalier King Charles',
    'cavalier king charles': 'Cavalier King Charles',
    'king charles': 'Cavalier King Charles',
    'basset hound': 'Basset Hound',
    'basset': 'Basset Hound',
    'bloodhound': 'Sabueso',
    'saint bernard': 'San Bernardo',
    'st bernard': 'San Bernardo',
    'weimaraner': 'Weimaraner',
    'vizsla': 'Vizsla',
    'english springer': 'Spaniel Springer Inglés',
    'springer': 'Spaniel Springer',
    'miniature schnauzer': 'Schnauzer Miniatura',
    'schnauzer': 'Schnauzer',
    'boston terrier': 'Boston Terrier',
    'boston': 'Boston Terrier',
    'jack russell': 'Jack Russell Terrier',
    'jack russell terrier': 'Jack Russell Terrier',
    'shih tzu': 'Shih Tzu',
    'shih': 'Shih Tzu',
    'bichon': 'Bichon Frisé',
    'bichon frise': 'Bichon Frisé',
    'breed not detected': 'Raza No Detectada',
    'retriever golden': 'Retriever Dorado',
    'shepherd german': 'Pastor Alemán',
    'bulldog french': 'Bulldog Francés',
    'mountain bernese': 'Perro de Montaña Bernés',
}

def extract_breed_name(imagenet_label):
    """Extract dog breed from ImageNet label - filter generic terms"""
    label_lower = imagenet_label.lower().strip()

    # Filtrar términos genéricos
    generic_terms = ['dog,', 'canine', 'working dog', 'toy dog', 'sporting dog', 'terrier group']
    if any(term in label_lower for term in generic_terms):
        # Si es muy genérico, intentar extraer algo específico
        for keyword in DOG_BREEDS_KEYWORDS:
            if keyword in label_lower:
                breed = label_lower.replace(',', '').replace('dog', '').strip().title()
                if breed and breed not in ['', 'Dog']:
                    return breed
        return None  # Retornar None para filtrar después

    for keyword in DOG_BREEDS_KEYWORDS:
        if keyword in label_lower:
            return label_lower.replace(',', '').title()

    return None  # No es una raza específica

def get_dog_image_and_info(breed_name):
    """Fetch dog image from Dog CEO API with multiple fallback strategies"""
    if not breed_name or breed_name == 'Breed Not Detected':
        return None

    breed_lower = breed_name.lower().strip()

    # Estrategia 1: Usar alias exacto
    if breed_lower in BREED_ALIASES:
        breed_key = BREED_ALIASES[breed_lower]
        img_url = try_get_image(breed_key, breed_name)
        if img_url:
            return img_url

    # Estrategia 2: Buscar alias parcial (palabras clave)
    for alias_key, alias_value in BREED_ALIASES.items():
        if breed_lower in alias_key or alias_key in breed_lower:
            img_url = try_get_image(alias_value, breed_name)
            if img_url:
                return img_url

    # Estrategia 3: Primera palabra
    if ' ' in breed_lower:
        first_word = breed_lower.split()[0]
        if first_word in BREED_ALIASES:
            breed_key = BREED_ALIASES[first_word]
            img_url = try_get_image(breed_key, breed_name)
            if img_url:
                return img_url

    # Estrategia 4: Sin espacios
    breed_key = breed_lower.replace(' ', '').replace(',', '')
    img_url = try_get_image(breed_key, breed_name)
    if img_url:
        return img_url

    # Estrategia 5: Con slash (subrazas)
    if ' ' in breed_lower:
        words = breed_lower.split()
        if len(words) >= 2:
            breed_key = f"{words[0]}/{words[1]}"
            img_url = try_get_image(breed_key, breed_name)
            if img_url:
                return img_url

    logger.warning(f"No se encontró imagen para: {breed_name} después de 5 intentos")
    return None

def try_get_image(breed_key, breed_name):
    """Try to get image from Dog CEO API - intenta múltiples variaciones"""
    # Generar variaciones del nombre
    variations = [
        breed_key,  # Original
        breed_key.lower(),  # Minúsculas
        breed_key.replace('/', '-'),  # Reemplazar / con -
        breed_key.replace('-', '/'),  # Reemplazar - con /
    ]

    # Si contiene /, también intentar sin él
    if '/' in breed_key:
        parts = breed_key.split('/')
        variations.append(parts[0])  # Primera parte
        variations.append(parts[1])  # Segunda parte
        variations.append(f"{parts[1]}/{parts[0]}")  # Invertido

    # Si es compuesto, intentar también con guion
    if ' ' in breed_name:
        simple = breed_name.replace(' ', '-').lower()
        variations.append(simple)
        variations.append(simple.replace('-', ''))

    # Eliminar duplicados manteniendo orden
    variations = list(dict.fromkeys(variations))

    for variant in variations:
        try:
            url = f"https://dog.ceo/api/breed/{variant}/images/random"
            logger.info(f"Intentando: {breed_name} → {variant}")

            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    logger.info(f"✓ Éxito: {breed_name} con variante: {variant}")
                    return data.get('message')

        except Exception as e:
            logger.debug(f"Variante falló ({variant}): {e}")
            continue

    logger.warning(f"✗ No se encontró imagen para {breed_name} en ninguna variante")
    return None

def classify_breed(image_pil):
    """Classify dog breed using ResNet50 - returns top specific breeds"""
    try:
        input_tensor = preprocess(image_pil)
        input_batch = input_tensor.unsqueeze(0)

        with torch.no_grad():
            output = model(input_batch)

        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top_prob, top_catid = torch.topk(probabilities, 15)  # Top 15 para filtrar mejor

        results = []
        seen_breeds = set()

        for prob, catid in zip(top_prob, top_catid):
            confidence = round(prob.item() * 100, 2)
            label = IMAGENET_CLASSES[catid] if catid < len(IMAGENET_CLASSES) else 'Unknown'
            breed_name = extract_breed_name(label)

            # Filtrar None y razas genéricas, mantener solo específicas con confianza > 2%
            if breed_name and confidence > 2 and breed_name.lower() not in seen_breeds:
                seen_breeds.add(breed_name.lower())
                results.append({
                    'breed': breed_name,
                    'confidence': confidence
                })

                if len(results) >= 5:  # Máximo 5 razas
                    break

        # Si no encontró razas específicas
        if not results:
            return [{'breed': 'Breed Not Detected', 'confidence': 0.0}]

        return results

    except Exception as e:
        logger.error(f"Error in classification: {e}")
        return [{'breed': 'Breed Not Detected', 'confidence': 0.0}]

def get_breed_characteristics(breed_name):
    """Get breed characteristics from dictionary, fallback to The Dog API"""
    breed_key = breed_name.lower().strip()

    # Buscar en diccionario exacto primero
    if breed_key in BREED_CHARACTERISTICS:
        return BREED_CHARACTERISTICS[breed_key]

    # Buscar por palabras clave
    for key, chars in BREED_CHARACTERISTICS.items():
        if breed_key in key or key in breed_key:
            return chars

    # Si no encuentra, consultar The Dog API
    logger.info(f"Buscando {breed_name} en The Dog API...")
    try:
        response = requests.get(
            f"https://api.thedogapi.com/v1/breeds/search?q={breed_key}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                breed_data = data[0]
                characteristics = {
                    'size': f"{breed_data.get('weight', {}).get('metric', 'Unknown')} kg",
                    'temperament': breed_data.get('temperament', 'Unknown'),
                    'lifespan': breed_data.get('life_span', 'Unknown'),
                    'origin': breed_data.get('origin', 'Unknown')
                }
                logger.info(f"✓ Encontrado en The Dog API: {breed_name}")
                return characteristics
    except Exception as e:
        logger.warning(f"Error consultando The Dog API para {breed_name}: {e}")

    # Default como último recurso
    return {
        'size': 'Unknown',
        'temperament': 'Unknown',
        'lifespan': 'Unknown',
        'origin': 'Unknown'
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        data = request.json
        image_base64 = data.get('image')

        if not image_base64:
            return jsonify({'error': 'No image provided'}), 400

        image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
        image_pil = Image.open(BytesIO(image_data)).convert('RGB')

        breed_predictions = classify_breed(image_pil)

        results = []
        for prediction in breed_predictions:
            breed_name = prediction['breed']
            confidence = prediction['confidence']
            dog_image_url = get_dog_image_and_info(breed_name)
            characteristics = get_breed_characteristics(breed_name)

            results.append({
                'breed': breed_name,
                'confidence': confidence,
                'image_url': dog_image_url,
                'characteristics': characteristics
            })

        return jsonify({
            'success': True,
            'breeds': results,
            'total_breeds': len(results)
        }), 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-all-breeds', methods=['GET'])
def test_all_breeds():
    """Test all breeds in BREED_ALIASES to see which work with Dog CEO API"""
    results = {
        'working': [],
        'failed': [],
        'total_tested': 0
    }

    tested_breeds = set()

    for breed_alias, breed_key in BREED_ALIASES.items():
        if breed_key in tested_breeds:
            continue
        tested_breeds.add(breed_key)

        results['total_tested'] += 1
        url = f"https://dog.ceo/api/breed/{breed_key}/images/random"

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    results['working'].append({
                        'breed': breed_alias,
                        'key': breed_key
                    })
                else:
                    results['failed'].append({
                        'breed': breed_alias,
                        'key': breed_key,
                        'reason': data.get('message')
                    })
            else:
                results['failed'].append({
                    'breed': breed_alias,
                    'key': breed_key,
                    'reason': f'HTTP {response.status_code}'
                })
        except Exception as e:
            results['failed'].append({
                'breed': breed_alias,
                'key': breed_key,
                'reason': str(e)
            })

    return jsonify(results), 200

@app.route('/debug-breeds', methods=['POST'])
def debug_breeds():
    """Debug endpoint to test specific breeds"""
    try:
        data = request.json
        breeds = data.get('breeds', [])

        results = []
        for breed in breeds:
            logger.info(f"Testing breed: {breed}")

            breed_lower = breed.lower().strip()

            # Check alias
            if breed_lower in BREED_ALIASES:
                breed_key = BREED_ALIASES[breed_lower]
                logger.info(f"  → Found alias: {breed_key}")
            else:
                breed_key = breed_lower.replace(' ', '').replace(',', '')
                logger.info(f"  → No alias, using: {breed_key}")

            # Test API
            url = f"https://dog.ceo/api/breed/{breed_key}/images/random"
            logger.info(f"  → Testing URL: {url}")

            try:
                response = requests.get(url, timeout=5)
                logger.info(f"  → Status: {response.status_code}")

                if response.status_code == 200:
                    data_resp = response.json()
                    logger.info(f"  → API Response status: {data_resp.get('status')}")

                    if data_resp.get('status') == 'success':
                        img_url = data_resp.get('message')
                        results.append({
                            'breed': breed,
                            'status': 'success',
                            'image_url': img_url
                        })
                    else:
                        results.append({
                            'breed': breed,
                            'status': 'api_error',
                            'message': data_resp.get('message')
                        })
                else:
                    results.append({
                        'breed': breed,
                        'status': 'http_error',
                        'code': response.status_code
                    })
            except Exception as e:
                logger.error(f"  → Exception: {str(e)}")
                results.append({
                    'breed': breed,
                    'status': 'exception',
                    'error': str(e)
                })

        return jsonify({'debug_results': results}), 200

    except Exception as e:
        logger.error(f"Debug error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
