#!/bin/bash
# Exemple d'utilisation d'Instagram Auto Publisher

echo "📱 Publication Instagram - Exemples"

# Publication d'une image unique
echo "1️⃣ Publication image unique..."
python3 /app/instagram_auto_publisher.py \
    --file "/path/to/image.webp" \
    --caption "Belle photo de nos chiots Berger Blanc Suisse! 🐕" \
    --hashtags "#bergerblancsuisse #chiots #elevage #chiens"

# Publication d'une vidéo
echo "2️⃣ Publication vidéo..."
python3 /app/instagram_auto_publisher.py \
    --file "/path/to/video.mov" \
    --caption "Nos chiots en plein jeu! 🎥" \
    --hashtags "#video #chiots #jeu #bergerblancsuisse"

# Publication par lots
echo "3️⃣ Publication par lots..."
python3 /app/instagram_auto_publisher.py \
    --batch "/path/to/photos_directory" \
    --caption "Collection de photos de nos chiens" \
    --hashtags "#collection #bergerblancsuisse #photos"

# Test sans publication
echo "4️⃣ Mode test..."
python3 /app/instagram_auto_publisher.py \
    --file "/path/to/test.jpg" \
    --caption "Test" \
    --dry-run

echo "✅ Exemples terminés!"
