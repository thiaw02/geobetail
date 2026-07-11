# views.py
import json
import time
import traceback
from collections import deque
from datetime import datetime, timedelta

from django.core.files.base import ContentFile
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.gzip import gzip_page

from .models import Alerte, Animal, CameraImage, Device, Position, Zone

# ============================================================================
# VARIABLES GLOBALES POUR LE STREAMING VIDÉO
# ============================================================================

video_frames_buffer = deque(maxlen=50)  # Garde les 50 dernières frames
stream_active = False
last_frame_time = 0

# ============================================================================
# VUES POUR PAGES HTML
# ============================================================================

def accueil(request):
    """Page d'accueil du système"""
    return render(request, 'animaux/accueil.html')

def dashboard(request):
    """Tableau de bord principal"""
    context = {
        'page_title': 'Dashboard GeoBétail',
        'active_animals': 0,
        'connected_devices': 1,
        'total_positions': 0,
        'last_update': '14:43'
    }
    return render(request, 'animaux/dashboard.html', context)

def animaux_list(request):
    """Liste des animaux"""
    return render(request, 'animaux/animaux_list.html')

def map_view(request):
    """Carte de suivi"""
    return render(request, 'animaux/map.html')

def connexion(request):
    return render(request, 'animaux/connexion.html')

def inscription(request):
    return render(request, 'animaux/inscription.html')

def surveillance_visuelle(request):
    """Page de surveillance visuelle en temps réel"""
    context = {
        'page_title': 'Surveillance Visuelle - GeoBétail',
        'stream_url': '/api/live_stream/',
        'status_url': '/api/stream_status/'
    }
    return render(request, 'animaux/surveillance.html', context)

# AJOUTER CETTE FONCTION MANQUANTE
def surveillance(request):
    """Alias pour la surveillance visuelle - même fonction que surveillance_visuelle"""
    return surveillance_visuelle(request)

def camera_view(request):
    """Vue pour l'affichage du flux caméra"""
    images = CameraImage.objects.order_by('-created_at')[:1] if CameraImage.objects.exists() else []
    return render(request, 'animaux/camera_stream.html', {'images': images})

# ============================================================================
# API POUR LE STREAMING VIDÉO
# ============================================================================

@csrf_exempt
def upload_image(request):
    """Réception des images individuelles de l'ESP32-CAM"""
    if request.method == 'POST':
        try:
            image_data = request.body
            if not image_data:
                return JsonResponse({'status': 'error', 'message': 'Aucune image reçue'}, status=400)
            
            # Sauvegarde dans la base de données
            filename = f"esp32_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            img = CameraImage()
            img.image.save(filename, ContentFile(image_data))
            img.save()
            
            # Traitement supplémentaire pour le streaming
            device_id = request.META.get('HTTP_DEVICE_ID', 'unknown')
            frame_data = {
                'timestamp': time.time(),
                'data': image_data,
                'device_id': device_id
            }
            
            # Ajouter au buffer pour le streaming
            video_frames_buffer.append(frame_data)
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Image reçue et enregistrée'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Erreur traitement image: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error', 
        'message': 'Méthode non autorisée'
    }, status=405)

@csrf_exempt
def video_stream(request):
    """Réception du flux vidéo de l'ESP32-CAM"""
    global video_frames_buffer, stream_active, last_frame_time
    
    if request.method == 'POST':
        try:
            # Mettre à jour le statut du stream
            stream_active = True
            last_frame_time = time.time()
            
            # Ajouter la frame au buffer
            frame_data = {
                'timestamp': time.time(),
                'data': request.body,
                'device_id': request.META.get('HTTP_DEVICE_ID', 'ESP32-CAM')
            }
            
            video_frames_buffer.append(frame_data)
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Frame reçue'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error', 
        'message': 'Méthode non autorisée'
    }, status=405)

@gzip_page
def live_stream(request):
    """Flux MJPEG pour l'affichage en temps réel"""
    def generate_frames():
        last_sent_index = -1
        while True:
            # Vérifier si de nouvelles frames sont disponibles
            if video_frames_buffer and last_sent_index != len(video_frames_buffer) - 1:
                current_frame = video_frames_buffer[-1]  # Prendre la dernière frame
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + current_frame['data'] + b'\r\n')
                
                last_sent_index = len(video_frames_buffer) - 1
            
            # Vérifier si le stream est toujours actif (timeout de 10 secondes)
            if time.time() - last_frame_time > 10:
                # Envoyer une frame de timeout/attente
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + get_waiting_frame() + b'\r\n')
            
            time.sleep(0.05)  # ~20 FPS max

    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

def get_waiting_frame():
    """Génère une image d'attente quand le stream est coupé"""
    # En production, vous pouvez retourner une image JPEG statique
    # Pour l'exemple, on retourne une image vide
    return b''

def stream_status(request):
    """API pour vérifier le statut du stream"""
    global stream_active, last_frame_time
    
    is_active = stream_active and (time.time() - last_frame_time < 10)
    
    return JsonResponse({
        'active': is_active,
        'last_update': last_frame_time,
        'buffer_size': len(video_frames_buffer),
        'devices_connected': 1 if is_active else 0
    })

# ============================================================================
# API ENDPOINTS POUR T-BEAM
# ============================================================================

@csrf_exempt
def receive_tbeam_data(request):
    """
    Endpoint professionnel pour réception des données T-Beam
    """
    if request.method == 'GET':
        return handle_sse_stream(request)
    elif request.method == 'POST':
        return handle_tbeam_post(request)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Méthode non autorisée'
        }, status=405)

def handle_sse_stream(request):
    """Gestion du streaming Server-Sent Events"""
    print("🔗 Nouvelle connexion SSE établie")
    
    def event_stream():
        try:
            # Message de connexion
            yield f"data: {json.dumps({'type': 'connection', 'message': 'Connecté au flux T-Beam', 'timestamp': timezone.now().isoformat()})}\n\n"
            
            # Garder la connexion active avec des heartbeats
            while True:
                time.sleep(30)  # Heartbeat toutes les 30 secondes
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': timezone.now().isoformat()})}\n\n"
                    
        except GeneratorExit:
            print("🔌 Client déconnecté du flux SSE")
        except Exception as e:
            print(f"❌ Erreur flux SSE: {e}")
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response

def handle_tbeam_post(request):
    """Gestion des données POST T-Beam"""
    try:
        print("🌍 RÉCEPTION DONNÉES T-BEAM")
        print("═" * 50)
        
        # Chargement et validation des données JSON
        try:
            if request.content_type == 'application/json':
                raw_data = request.body.decode('utf-8')
                data = json.loads(raw_data)
            else:
                # Support for form data
                data = request.POST.dict()
                if not data:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Aucune donnée reçue'
                    }, status=400)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Données JSON invalides: {str(e)}'
            }, status=400)
        except Exception as e:
            print(f"❌ Erreur décodage: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur décodage données: {str(e)}'
            }, status=400)
        
        # Log des données reçues
        print(f"📨 Données brutes reçues: {data}")
        
        # Extraction des champs avec support multiple
        device_id = data.get('device_id') or data.get('deviceId') or data.get('id')
        latitude = data.get('latitude') or data.get('lat')
        longitude = data.get('longitude') or data.get('lng') or data.get('lon')
        batterie = data.get('batterie') or data.get('battery') or data.get('bat')
        satellites = data.get('satellites') or data.get('sats')
        accuracy = data.get('accuracy') or data.get('hdop')
        
        # Validation des données requises
        if not device_id:
            print("❌ Device ID manquant")
            return JsonResponse({
                'status': 'error',
                'message': 'Device ID manquant'
            }, status=400)
            
        if not latitude or not longitude:
            print("❌ Coordonnées GPS manquantes")
            return JsonResponse({
                'status': 'error',
                'message': 'Coordonnées GPS manquantes'
            }, status=400)
        
        # Conversion des coordonnées
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            print(f"📍 Coordonnées converties: {latitude}, {longitude}")
        except (ValueError, TypeError) as e:
            print(f"❌ Erreur conversion coordonnées: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Coordonnées GPS invalides: {str(e)}'
            }, status=400)
        
        # Récupération ou création du device
        try:
            device, created = Device.objects.get_or_create(
                device_id=device_id,
                defaults={
                    'nom': f"T-Beam {device_id}",
                    'type_device': 'TBEAM',
                    'statut': 'ACTIF'
                }
            )
            
            if created:
                print(f"✅ NOUVEAU DEVICE CRÉÉ: {device_id}")
            else:
                print(f"📱 Device existant: {device_id}")
            
            # Mise à jour du device
            device.date_dernier_contact = timezone.now()
            if batterie is not None:
                try:
                    device.batterie = float(batterie)
                except (ValueError, TypeError):
                    device.batterie = 100
            device.save()
            
        except Exception as e:
            print(f"❌ Erreur device: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur gestion device: {str(e)}'
            }, status=500)
        
        # Recherche ou création de l'animal associé au device
        animal = None
        try:
            animal = Animal.objects.filter(device=device).first()
            
            if animal is None:
                # Créer un nouvel animal
                animal = Animal.objects.create(
                    nom=f"Animal {device_id}",
                    type_animal='VACHE',
                    statut='ACTIF',
                    device=device,
                    emoji='🐮',
                    couleur='#3498db'
                )
                print(f"✅ NOUVEL ANIMAL CRÉÉ: {animal.nom}")
            else:
                print(f"🐮 Animal existant: {animal.nom}")
                
        except Exception as e:
            print(f"⚠️ Erreur lors de l'association animal-device: {str(e)}")
            # Continuer même sans animal
            
        # Gestion du timestamp
        timestamp = timezone.now()
        timestamp_input = data.get('timestamp') or data.get('time')
        
        if timestamp_input:
            try:
                if isinstance(timestamp_input, (int, float)):
                    # Timestamp Unix
                    timestamp = datetime.fromtimestamp(timestamp_input, tz=timezone.utc)
                elif isinstance(timestamp_input, str):
                    # Chaîne de caractères ISO
                    if 'Z' in timestamp_input:
                        timestamp_input = timestamp_input.replace('Z', '+00:00')
                    timestamp = datetime.fromisoformat(timestamp_input)
                    if timestamp.tzinfo is None:
                        timestamp = timezone.make_aware(timestamp)
                print(f"🕒 Timestamp utilisé: {timestamp}")
            except (ValueError, TypeError) as e:
                print(f"⚠️ Erreur conversion timestamp: {e} - Utilisation timestamp actuel")
                timestamp = timezone.now()
        
        # Création de la position
        try:
            position = Position.objects.create(
                animal=animal,
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamp,
                batterie=batterie,
                satellites=satellites,
                accuracy=accuracy,
                altitude=data.get('altitude'),
                speed=data.get('speed'),
                raw_data=json.dumps(data)
            )
            print(f"📍 Position enregistrée: {latitude:.6f}, {longitude:.6f}")
            
        except Exception as e:
            print(f"❌ Erreur création position: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur création position: {str(e)}'
            }, status=500)
        
        # Mise à jour de la date de dernier contact de l'animal
        if animal:
            try:
                animal.date_dernier_contact = timezone.now()
                animal.save()
                print(f"🔄 Animal mis à jour: {animal.nom}")
            except Exception as e:
                print(f"⚠️ Erreur mise à jour animal: {str(e)}")
        
        # Vérification des alertes
        try:
            check_alertes(animal, position, device)
        except Exception as e:
            print(f"⚠️ Erreur lors de la vérification des alertes: {str(e)}")
        
        # Préparer les données pour la réponse
        response_data = {
            'status': 'success',
            'message': 'Données enregistrées avec succès',
            'device_id': device.device_id,
            'animal_nom': animal.nom if animal else f"Animal {device_id}",
            'animal_id': animal.id if animal else None,
            'latitude': latitude,
            'longitude': longitude,
            'batterie': batterie,
            'satellites': satellites,
            'accuracy': accuracy,
            'timestamp': timestamp.isoformat(),
            'server_time': timezone.now().isoformat()
        }
        
        print("✅ DONNÉES TRAITÉES AVEC SUCCÈS")
        print(f"📟 Device: {device.device_id}")
        print(f"🐮 Animal: {animal.nom if animal else 'Non assigné'}")
        print(f"📍 Position: {latitude:.6f}, {longitude:.6f}")
        print(f"🕒 Timestamp: {timestamp}")
        print(f"📊 Batterie: {batterie}%")
        print("═" * 50)
        
        return JsonResponse(response_data, status=201)
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {str(e)}")
        print(f"🔍 DÉTAILS ERREUR: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur serveur: {str(e)}'
        }, status=500)

def check_alertes(animal, position, device):
    """Vérification et création d'alertes professionnelles"""
    try:
        # Alerte batterie faible
        if device.batterie and device.batterie < 20:
            alerte, created = Alerte.objects.get_or_create(
                animal=animal,
                type_alerte='BATTERIE_FAIBLE',
                resolue=False,
                defaults={
                    'message': f'Batterie faible: {device.batterie}% - Device {device.device_id}',
                    'priorite': 'MOYENNE',
                    'position': position
                }
            )
            if created:
                print(f"🚨 ALERTE: Batterie faible {device.batterie}%")
        
        # Alerte perte de signal (si peu de positions récentes)
        if animal:
            seuil_temps = timezone.now() - timedelta(hours=1)
            positions_recentes = Position.objects.filter(
                animal=animal,
                timestamp__gte=seuil_temps
            ).count()
            
            if positions_recentes <= 1:  # Très peu de positions récentes
                alerte, created = Alerte.objects.get_or_create(
                    animal=animal,
                    type_alerte='SIGNAL_FAIBLE',
                    resolue=False,
                    defaults={
                        'message': f'Signal faible - Peu de positions récentes',
                        'priorite': 'BASSE',
                        'position': position
                    }
                )
                if created:
                    print(f"📡 ALERTE: Signal faible pour {animal.nom}")
                
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification des alertes: {str(e)}")

# ============================================================================
# API POUR FRONTEND
# ============================================================================

@gzip_page
def get_active_animals(request):
    """Récupération des animaux actifs"""
    try:
        seuil_activite = timezone.now() - timedelta(hours=2)
        
        animaux_actifs = []
        animaux_avec_positions = Animal.objects.filter(
            position__timestamp__gte=seuil_activite
        ).distinct()
        
        for animal in animaux_avec_positions:
            derniere_position = Position.objects.filter(
                animal=animal,
                timestamp__gte=seuil_activite
            ).order_by('-timestamp').first()
            
            if derniere_position:
                animaux_actifs.append({
                    'id': animal.id,
                    'nom': animal.nom,
                    'type_animal': animal.type_animal,
                    'race': animal.race or '',
                    'device_id': animal.device.device_id if animal.device else None,
                    'statut': animal.statut,
                    'derniere_position': {
                        'latitude': float(derniere_position.latitude),
                        'longitude': float(derniere_position.longitude),
                        'timestamp': derniere_position.timestamp.isoformat(),
                        'batterie': derniere_position.batterie,
                        'satellites': derniere_position.satellites,
                        'accuracy': derniere_position.accuracy
                    },
                    'emoji': animal.emoji or '🐮',
                    'couleur': animal.couleur or '#4CAF50',
                    'nombre_positions': Position.objects.filter(animal=animal).count(),
                    'dernier_contact': animal.date_dernier_contact.isoformat() if animal.date_dernier_contact else None
                })
        
        return JsonResponse({
            'status': 'success',
            'count': len(animaux_actifs),
            'maj': timezone.now().strftime('%H:%M:%S'),
            'animaux': animaux_actifs
        })
        
    except Exception as e:
        print(f"❌ Erreur get_active_animals: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur récupération animaux: {str(e)}'
        }, status=500)

@gzip_page
def get_dashboard_stats(request):
    """Statistiques pour le tableau de bord"""
    try:
        maintenant = timezone.now()
        aujourd_hui = maintenant.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calcul des statistiques avec gestion des erreurs
        seuil_activite = maintenant - timedelta(hours=2)
        
        try:
            animaux_actifs_count = Animal.objects.filter(
                position__timestamp__gte=seuil_activite
            ).distinct().count()
        except:
            animaux_actifs_count = 0
            
        try:
            animaux_totaux = Animal.objects.count()
        except:
            animaux_totaux = 0
            
        try:
            devices_actifs = Device.objects.filter(
                date_dernier_contact__gte=seuil_activite
            ).count()
        except:
            devices_actifs = 0
            
        try:
            total_positions = Position.objects.count()
        except:
            total_positions = 0
            
        try:
            donnees_aujourdhui = Position.objects.filter(
                timestamp__gte=aujourd_hui
            ).count()
        except:
            donnees_aujourdhui = 0
            
        try:
            donnees_7jours = Position.objects.filter(
                timestamp__gte=maintenant - timedelta(days=7)
            ).count()
        except:
            donnees_7jours = 0
            
        try:
            donnees_30jours = Position.objects.filter(
                timestamp__gte=maintenant - timedelta(days=30)
            ).count()
        except:
            donnees_30jours = 0
            
        try:
            alertes_actives = Alerte.objects.filter(resolue=False).count()
        except:
            alertes_actives = 0
        
        stats = {
            'animaux_actifs': animaux_actifs_count,
            'animaux_totaux': animaux_totaux,
            'devices_actifs': devices_actifs,
            'total_positions': total_positions,
            'donnees_aujourdhui': donnees_aujourdhui,
            'donnees_7jours': donnees_7jours,
            'donnees_30jours': donnees_30jours,
            'alertes_actives': alertes_actives,
            'maj': maintenant.strftime('%H:%M:%S')
        }
        
        return JsonResponse({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        print(f"❌ Erreur get_dashboard_stats: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur récupération stats: {str(e)}'
        }, status=500)

@gzip_page
def get_recent_positions(request):
    """Positions récentes"""
    try:
        limit = int(request.GET.get('limit', 50))
        
        positions = Position.objects.select_related('animal', 'animal__device').order_by('-timestamp')[:limit]
        
        positions_data = []
        for position in positions:
            positions_data.append({
                'id': position.id,
                'animal_nom': position.animal.nom if position.animal else 'Non assigné',
                'animal_id': position.animal.id if position.animal else None,
                'device_id': position.animal.device.device_id if position.animal and position.animal.device else None,
                'latitude': float(position.latitude),
                'longitude': float(position.longitude),
                'timestamp': position.timestamp.isoformat(),
                'batterie': position.batterie,
                'satellites': position.satellites,
                'accuracy': position.accuracy,
                'altitude': position.altitude
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(positions_data),
            'data': positions_data
        })
        
    except Exception as e:
        print(f"❌ Erreur get_recent_positions: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur récupération positions: {str(e)}'
        }, status=500)

@gzip_page
def get_animaux_list(request):
    """Liste complète des animaux"""
    try:
        animaux = Animal.objects.select_related('device').prefetch_related('position_set').all()
        
        animaux_data = []
        for animal in animaux:
            try:
                nombre_positions = animal.position_set.count()
            except:
                nombre_positions = 0
                
            try:
                derniere_position = animal.position_set.order_by('-timestamp').first()
            except:
                derniere_position = None
            
            animaux_data.append({
                'id': animal.id,
                'nom': animal.nom,
                'type_animal': animal.type_animal,
                'race': animal.race or '',
                'device_id': animal.device.device_id if animal.device else None,
                'statut': animal.statut,
                'nombre_positions': nombre_positions,
                'date_dernier_contact': animal.date_dernier_contact.isoformat() if animal.date_dernier_contact else None,
                'emoji': animal.emoji or '🐮',
                'couleur': animal.couleur or '#4CAF50',
                'derniere_position': {
                    'latitude': float(derniere_position.latitude) if derniere_position else None,
                    'longitude': float(derniere_position.longitude) if derniere_position else None,
                    'timestamp': derniere_position.timestamp.isoformat() if derniere_position else None
                } if derniere_position else None
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(animaux_data),
            'animaux': animaux_data
        })
        
    except Exception as e:
        print(f"❌ Erreur get_animaux_list: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur récupération animaux: {str(e)}'
        }, status=500)

@gzip_page
def get_zones(request):
    """Récupérer toutes les zones"""
    try:
        zones = Zone.objects.all()
        
        zones_data = []
        for zone in zones:
            zones_data.append({
                'id': zone.id,
                'nom': zone.nom,
                'description': zone.description or '',
                'type_zone': zone.type_zone,
                'polygone': zone.polygone,
                'couleur': zone.couleur or '#FF5722',
                'date_creation': zone.date_creation.isoformat() if zone.date_creation else None
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(zones_data),
            'zones': zones_data
        })
        
    except Exception as e:
        print(f"❌ Erreur get_zones: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur récupération zones: {str(e)}'
        }, status=500)

@gzip_page
def get_alertes(request):
    """Récupérer les alertes actives"""
    try:
        alertes = Alerte.objects.filter(resolue=False).select_related('animal', 'position')
        
        alertes_data = []
        for alerte in alertes:
            alertes_data.append({
                'id': alerte.id,
                'animal_nom': alerte.animal.nom,
                'animal_id': alerte.animal.id,
                'type_alerte': alerte.type_alerte,
                'priorite': alerte.priorite,
                'message': alerte.message,
                'position': {
                    'latitude': float(alerte.position.latitude) if alerte.position else None,
                    'longitude': float(alerte.position.longitude) if alerte.position else None
                } if alerte.position else None,
                'date_creation': alerte.date_creation.isoformat() if alerte.date_creation else None
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(alertes_data),
            'alertes': alertes_data
        })
        
    except Exception as e:
        print(f"❌ Erreur get_alertes: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur récupération alertes: {str(e)}'
        }, status=500)

@gzip_page
def get_devices(request):
    """Liste des devices"""
    try:
        devices = Device.objects.select_related('animal').all()
        
        devices_data = []
        for device in devices:
            devices_data.append({
                'id': device.id,
                'device_id': device.device_id,
                'nom': device.nom,
                'type_device': device.type_device,
                'statut': device.statut,
                'batterie': device.batterie,
                'date_activation': device.date_activation.isoformat() if device.date_activation else None,
                'date_dernier_contact': device.date_dernier_contact.isoformat() if device.date_dernier_contact else None,
                'animal_nom': device.animal.nom if device.animal else None,
                'animal_id': device.animal.id if device.animal else None
            })
        
        return JsonResponse({
            'status': 'success',
            'count': len(devices_data),
            'devices': devices_data
        })
        
    except Exception as e:
        print(f"❌ Erreur get_devices: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur récupération devices: {str(e)}'
        }, status=500)

@csrf_exempt
def firmware_update(request):
    """Mise à jour firmware"""
    return JsonResponse({
        'status': 'success',
        'firmware_version': '2.1.0',
        'update_available': False,
        'message': 'Firmware à jour - Système GeoBétail'
    })

@gzip_page
def test_endpoint(request):
    """Endpoint de test pour vérifier que l'API fonctionne"""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'message': 'API GeoBétail fonctionnelle',
            'timestamp': timezone.now().isoformat(),
            'endpoints': {
                'tbeam_data': '/api/tbeam/stream/ (POST)',
                'active_animals': '/api/animaux/actifs/',
                'dashboard_stats': '/api/dashboard/stats/',
                'recent_positions': '/api/positions/recentes/',
                'animaux_list': '/api/animaux/liste/',
                'zones': '/api/zones/',
                'alertes': '/api/alertes/',
                'devices': '/api/devices/',
                'video_stream': '/api/video_stream/ (POST)',
                'live_stream': '/api/live_stream/ (GET)',
                'stream_status': '/api/stream_status/ (GET)'
            }
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée'
    }, status=405)