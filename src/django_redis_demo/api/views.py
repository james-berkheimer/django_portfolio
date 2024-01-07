# Create your views here.
import json

import redis
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


@api_view(["GET", "POST"])
def manage_items(request, *args, **kwargs):
    if request.method == "GET":
        items = {}
        count = 0
        for key in redis_instance.keys("*"):
            key_str = key.decode("utf-8")
            type_of_key = redis_instance.type(key).decode("utf-8")
            if type_of_key == "string":
                items[key_str] = redis_instance.get(key).decode("utf-8")
            elif type_of_key == "hash":
                items[key_str] = {
                    k.decode("utf-8"): v.decode("utf-8")
                    for k, v in redis_instance.hgetall(key).items()
                }
            # Add more elif clauses here for other types as needed
            count += 1
        response = {"count": count, "msg": f"Found {count} items.", "items": items}
        # return Response(response, status=200)
        return render(request, "api/items.html", response)


@api_view(["GET", "PUT", "DELETE"])
def manage_item(request, *args, **kwargs):
    if request.method == "GET":
        if kwargs["key"]:
            value = redis_instance.get(kwargs["key"])
            if value:
                response = {"key": kwargs["key"], "value": value, "msg": "success"}
                return Response(response, status=200)
            else:
                response = {"key": kwargs["key"], "value": None, "msg": "Not found"}
                return Response(response, status=404)
    elif request.method == "PUT":
        if kwargs["key"]:
            request_data = json.loads(request.body)
            new_value = request_data["new_value"]
            value = redis_instance.get(kwargs["key"])
            if value:
                redis_instance.set(kwargs["key"], new_value)
                response = {
                    "key": kwargs["key"],
                    "value": value,
                    "msg": f"Successfully updated {kwargs['key']}",
                }
                return Response(response, status=200)
            else:
                response = {"key": kwargs["key"], "value": None, "msg": "Not found"}
                return Response(response, status=404)

    elif request.method == "DELETE":
        if kwargs["key"]:
            result = redis_instance.delete(kwargs["key"])
            if result == 1:
                response = {"msg": f"{kwargs['key']} successfully deleted"}
                return Response(response, status=404)
            else:
                response = {"key": kwargs["key"], "value": None, "msg": "Not found"}
                return Response(response, status=404)


def home(request):
    return render(request, "home.html")
