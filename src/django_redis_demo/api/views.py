# Create your views here.
# import json

import redis
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.views import View
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# from media_conveyor.authentication import PlexAuthentication
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
from .models import MediaThumbnail

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# plex_auth = PlexAuthentication()


def home(request):
    return render(request, "home.html")


class ItemsView(View):
    def get(self, request, *args, **kwargs):
        items = {}
        for key in redis_instance.keys("*"):
            print(f"key: {key}")
            key_str = key.decode("utf-8")
            type_of_key = redis_instance.type(key).decode("utf-8")
            if type_of_key == "string":
                movie_thumb_url = f"https://{settings.PLEX_SERVER_IP}:{settings.PLEX_SERVER_PORT}{redis_instance.get(key).decode('utf-8')}"

                response = requests.get(movie_thumb_url, verify=False)
                image_file = ContentFile(response.content, name=f"{key_str}.jpg")

                thumbnail, _ = MediaThumbnail.objects.update_or_create(
                    defaults={"movie_thumb_url": movie_thumb_url, "image": image_file},
                    movie_thumb_url=movie_thumb_url,
                )

                items[key_str] = (items[key_str], thumbnail)
            elif type_of_key == "hash":
                items[key_str] = {
                    k.decode("utf-8"): v.decode("utf-8")
                    for k, v in redis_instance.hgetall(key).items()
                }
                # Add the movie_thumb_url to the hash
                movie_thumb_url = f"https://{settings.PLEX_SERVER_IP}:{settings.PLEX_SERVER_PORT}{items[key_str]['thumb_path']}"
                # redis_instance.hset(key, "movie_thumb_url", movie_thumb_url)
                # items[key_str]["movie_thumb_url"] = movie_thumb_url

                # Fetch the movie title and year from Redis
                movie_title = redis_instance.hget(key, "title").decode("utf-8")
                movie_year = redis_instance.hget(key, "year").decode("utf-8")
                media_type = key.decode().split(":")[0]
                items[key_str]["title"] = movie_title
                items[key_str]["year"] = movie_year
                items[key_str]["media_type"] = media_type

                response = requests.get(movie_thumb_url, verify=False)
                image_file = ContentFile(response.content, name=f"{key_str}.jpg")

                thumbnail, _ = MediaThumbnail.objects.update_or_create(
                    defaults={"movie_thumb_url": movie_thumb_url, "image": image_file},
                    image=key_str,
                )

                items[key_str] = (items[key_str], thumbnail)
        sorted_items = sorted(items.items(), key=lambda x: x[0].split(":")[0])
        # print(f"Sorted items: {sorted_items}")
        parsed_items = [
            (key.split(":")[1], key.split(":")[0], value[0], value[1])
            for key, value in sorted_items
        ]

        return render(request, "api/items.html", {"items": parsed_items})
