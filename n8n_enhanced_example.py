#!/usr/bin/env python3
"""
Exemple pratique pour N8N - Simulation de votre transformation exacte
"""

import requests
import json
from PIL import Image
import io

def simulate_n8n_transformation(binary_data, filename):
    """
    Simule exactement votre transformation N8N :
    
    return items.map(item => {
      return {
        json: {
          store: "ma-boutique",
          title: item.binary.data.fileName,
          description: "Découvrez ce produit dans notre boutique !",
          product_url: "https://www.logicamp.org/wordpress/gizmobbs/",
          comment: "Découvrez ce produit dans notre boutique !"
        },
        binary: {
          image: item.binary.data // met le binaire sous le champ "image"
        }
      };
    });
    """
    
    # Simulation de la partie JSON de votre transformation
    json_part = {
        "store": "ma-boutique",
        "title": filename,  # item.binary.data.fileName
        "description": "Découvrez ce produit dans notre boutique !",
        "product_url": "https://www.logicamp.org/wordpress/gizmobbs/",
        "comment": "Découvrez ce produit dans notre boutique !"
    }
    
    # Simulation de la partie binary de votre transformation
    binary_part = {
        "image": binary_data  # item.binary.data
    }
    
    return json_part, binary_part

def create_sample_product_images():
    """Créer plusieurs images de produits d'exemple"""
    products = [
        {"name": "chaise_design_premium.jpg", "color": (139, 69, 19), "text": "Chaise Design"},
        {"name": "table_moderne_bois.jpg", "color": (160, 82, 45), "text": "Table Moderne"}, 
        {"name": "lampe_vintage_cuivre.jpg", "color": (184, 134, 11), "text": "Lampe Vintage"},
        {"name": "coussin_velours_bleu.jpg", "color": (25, 25, 112), "text": "Coussin Velours"},
        {"name": "vase_ceramique_blanc.jpg", "color": (248, 248, 255), "text": "Vase Céramique"}
    ]
    
    images = []
    
    for product in products:
        # Créer une image pour chaque produit
        img = Image.new('RGB', (500, 400), color=product["color"])
        
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            # Texte en blanc avec outline noir pour visibilité
            draw.text((50, 150), product["text"], fill=(255, 255, 255))
            draw.text((50, 180), "Boutique Premium", fill=(255, 255, 255))
            draw.text((50, 210), "Qualité Française", fill=(255, 255, 255))
        except:
            pass
        
        # Convertir en bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG', quality=95)
        img_bytes = img_buffer.getvalue()
        
        images.append({
            "filename": product["name"],
            "data": img_bytes,
            "size": len(img_bytes)
        })
    
    return images

def test_n8n_simulation():
    """Test complet avec simulation N8N"""
    print("🚀 Simulation N8N - Webhook Enhancé")
    print("=" * 60)
    
    # Créer des images de produits d'exemple
    sample_images = create_sample_product_images()
    
    results = []
    
    for i, image_info in enumerate(sample_images):
        print(f"\n📦 Produit {i+1}/{len(sample_images)}: {image_info['filename']}")
        print("-" * 40)
        
        try:
            # Simulation de votre transformation N8N
            json_data, binary_data = simulate_n8n_transformation(
                image_info['data'], 
                image_info['filename']
            )
            
            print(f"🔄 Transformation N8N simulée:")
            print(f"   📝 JSON: {json.dumps(json_data, indent=2)}")
            print(f"   📁 Binary size: {len(binary_data['image'])} bytes")
            
            # Préparer la requête multipart (comme N8N l'enverrait)
            files = {
                'json_data': (None, json.dumps(json_data), 'application/json'),
                'image': (image_info['filename'], binary_data['image'], 'image/jpeg')
            }
            
            print(f"📡 Envoi vers webhook enhancé...")
            response = requests.post(
                "http://localhost:8001/api/webhook/enhanced",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS - {result.get('message', 'No message')}")
                
                if 'data' in result:
                    data = result['data']
                    print(f"   📸 Facebook Post ID: {data.get('facebook_post_id', 'None')}")
                    print(f"   📱 Instagram: {'✅' if data.get('instagram_post_id') else '❌ Failed'}")
                    print(f"   📄 Page: {data.get('page_name', 'None')}")
                    print(f"   🔗 Image URL: {data.get('generated_image_url', 'None')}")
                
                results.append({
                    "product": image_info['filename'],
                    "success": True,
                    "facebook_post_id": result.get('data', {}).get('facebook_post_id'),
                    "message": result.get('message')
                })
            else:
                error_text = response.text
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"   💥 Error: {error_text}")
                
                results.append({
                    "product": image_info['filename'],
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}"
                })
        
        except Exception as e:
            print(f"💥 Exception: {e}")
            results.append({
                "product": image_info['filename'],
                "success": False,
                "error": str(e)
            })
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA SIMULATION N8N")
    print("=" * 60)
    
    successes = [r for r in results if r['success']]
    failures = [r for r in results if not r['success']]
    
    print(f"✅ Succès: {len(successes)}/{len(results)}")
    print(f"❌ Échecs: {len(failures)}/{len(results)}")
    
    if successes:
        print(f"\n🎉 Produits publiés avec succès:")
        for result in successes:
            print(f"   ✅ {result['product']} -> Post ID: {result.get('facebook_post_id', 'N/A')}")
    
    if failures:
        print(f"\n⚠️ Produits en échec:")
        for result in failures:
            print(f"   ❌ {result['product']}: {result.get('error', 'Unknown error')}")
    
    # Instructions pour N8N
    print(f"\n📋 INSTRUCTIONS POUR N8N:")
    print("-" * 30)
    print("1. Utilisez exactement cette transformation :")
    print("""
return items.map(item => {
  return {
    json: {
      store: "ma-boutique",
      title: item.binary.data.fileName,
      description: "Découvrez ce produit dans notre boutique !",
      product_url: "https://www.logicamp.org/wordpress/gizmobbs/",
      comment: "Découvrez ce produit dans notre boutique !"
    },
    binary: {
      image: item.binary.data
    }
  };
});""")
    
    print("\n2. Configurez le nœud HTTP Request :")
    print("   • URL: https://fb-webhook-local.preview.emergentagent.com/api/webhook/enhanced")
    print("   • Method: POST")
    print("   • Body Type: Multipart-Form Data")
    print("   • Fields:")
    print("     - json_data: {{ JSON.stringify($json) }}")
    print("     - image: {{ $binary.image }}")
    
    return len(successes) == len(results)

if __name__ == "__main__":
    success = test_n8n_simulation()
    
    if success:
        print("\n🎉 Simulation complètement réussie ! Votre webhook est prêt pour N8N.")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez la configuration.")