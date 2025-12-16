#!/usr/bin/env python3
"""Créer toutes les variantes d'icônes et logos pour le dépôt brands."""

from PIL import Image, ImageOps
import os

def remove_white_background(img):
    """Convertir le fond blanc en transparent (agressif)."""
    img = img.convert("RGBA")
    datas = img.getdata()
    
    newData = []
    for item in datas:
        r, g, b, a = item[0], item[1], item[2], item[3] if len(item) == 4 else 255
        
        # Calculer la luminosité
        luminosity = (r + g + b) / 3
        
        # Pixels très clairs (blanc, gris très clair) -> transparent
        if luminosity > 230:
            newData.append((255, 255, 255, 0))
        # Pixels moyennement clairs -> semi-transparent proportionnel
        elif luminosity > 200:
            # Réduire progressivement l'opacité
            alpha = int((230 - luminosity) / 30 * 255)
            newData.append((r, g, b, alpha))
        else:
            newData.append(item)
    
    img.putdata(newData)
    return img

def crop_transparent(img):
    """Rogner l'espace transparent autour de l'image."""
    # Trouver la boîte englobante du contenu non-transparent
    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox)
    return img

def create_dark_version(img):
    """Créer une version pour fond sombre (inverser si nécessaire)."""
    # Pour le moment, on garde la même image
    # Si besoin d'inverser : return ImageOps.invert(img.convert('RGB')).convert('RGBA')
    return img

def create_all_variants(source_file, output_dir):
    """Créer toutes les variantes nécessaires."""
    
    # Charger l'image source
    img = Image.open(source_file)
    
    # Enlever le fond blanc
    img_transparent = remove_white_background(img)
    
    # Rogner l'espace transparent
    img_transparent = crop_transparent(img_transparent)
    
    # Redimensionner aux tailles standards
    # Icon : 256x256 (normal) et 512x512 (hDPI)
    img_256 = img_transparent.resize((256, 256), Image.Resampling.LANCZOS)
    img_512 = img_transparent.resize((512, 512), Image.Resampling.LANCZOS)
    
    # Sauvegarder toutes les versions
    os.makedirs(output_dir, exist_ok=True)
    
    # Icon versions (256x256 et 512x512)
    img_256.save(os.path.join(output_dir, "icon.png"), "PNG")
    img_512.save(os.path.join(output_dir, "icon@2x.png"), "PNG")
    
    # Logo versions (même tailles)
    img_256.save(os.path.join(output_dir, "logo.png"), "PNG")
    img_512.save(os.path.join(output_dir, "logo@2x.png"), "PNG")
    
    print(f"✅ Créé 4 fichiers dans {output_dir}")
    print(f"   - Taille normale: 256x256")
    print(f"   - Taille @2x: 512x512")
    print(f"   (Pas de versions dark - identiques aux normales)")

if __name__ == "__main__":
    source = "logo.png"
    output = "brands_submission/custom_integrations/rn_collectes"
    
    create_all_variants(source, output)
