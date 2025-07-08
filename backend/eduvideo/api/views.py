# backend/eduvideo/views.py
from django.shortcuts import render
from django.http import JsonResponse
from ..models.models import EduVideo
from django.conf import settings
from django.core.cache import cache
from ..serializers import EduVideoSerializer
from django.http import JsonResponse
import requests
import redis
import datetime


# Redis client setup
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    charset="utf-8",
    decode_responses=True
)

def fetch_and_cache_videos():
    cached_videos = cache.get('youtube_videos')
    if cached_videos:
        return cached_videos

    # YouTube API URL'i ve istek parametreleri
    url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    params = {
        'part': 'snippet',
        'maxResults': 1000, 
        'playlistId': settings.YOUTUBE_PLAYLIST_ID,
        'key': settings.YOUTUBE_DATA_API_KEY,
    }

    # YouTube API'sinden veri çekme
    response = requests.get(url, params=params)
    response_json = response.json()

    # API'den başarılı bir yanıt geldiyse
    if response.status_code == 200:
        videos_info = []
        for item in response_json.get('items', []):
            snippet = item['snippet']
            video_id = snippet['resourceId']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Thumbnail URL kontrolü
        thumbnail_url = snippet['thumbnails'].get('high', {}).get('url', 'Varsayılan thumbnail URL adresi')

        video_info = {
            'title': snippet['title'],
            'video_id': video_id,
            'description': snippet.get('description', ''),
            'video_url': video_url,
            'thumbnail_url': thumbnail_url,
        }
        videos_info.append(video_info)

        # Cachelenen verileri güncelle
        cache.set('youtube_videos', videos_info, timeout=settings.CACHE_TTL)
    
    return videos_info


def load_videos_from_cache(cached_videos):
    # Redis'ten çekilen verileri işle
    if not cached_videos:
        return
    
    # Verileri Django modeline kaydet
    for video in cached_videos:
        EduVideo.objects.update_or_create(
            video_url=video['video_url'],
            defaults={
                'title': video['title'],
                'description': video['description'],
                'thumbnail_url': video['thumbnail_url'],  
                'published_at': datetime.datetime.now()  
            }
        )


def edu_videos_view(request):
    if request.method == 'GET':
        last_update = cache.get('last_youtube_update', datetime.datetime.min)

        if datetime.datetime.now() - last_update > datetime.timedelta(minutes=15):
            videos_info = fetch_and_cache_videos()
            load_videos_from_cache(videos_info)  
            cache.set('last_youtube_update', datetime.datetime.now())

        videos = EduVideo.objects.all()
        serializer = EduVideoSerializer(videos, many=True)  
        return JsonResponse(serializer.data, safe=False)