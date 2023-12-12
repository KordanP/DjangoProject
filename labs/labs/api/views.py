# views.py
from django.core.serializers import serialize
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.core import serializers
from rest_framework import status
from django.db.models import Q
from .models import Playlist, Track
from .forms import PlaylistForm, TrackForm
from rest_framework.response import Response
import json

from .serializers import PlaylistSerializer, TrackSerializer


@swagger_auto_schema(
    method="GET",
    operation_summary="Get playlists for authenticated user",
    responses={
        200: "OK - List of playlists and user information",
        401: "Unauthorized - Authentication required",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def playlist_list(request):
    if request.user.is_authenticated:
        playlists = Playlist.objects.filter(owner=request.user)
        return JsonResponse({'playlists': [{'title': playlist.title, 'owner': playlist.owner.username,
                                            'public': playlist.public, 'id': playlist.id} for playlist in playlists],
                             'user': request.user.username})
    else:
        return JsonResponse({'error': 'Authentication required'}, status=401)


@swagger_auto_schema(
    method='GET',
    operation_summary="Get details of a specific playlist for an authenticated user",
    responses={
        200: "OK - Playlist details",
        401: "Bad Request - Authentication required",
        403: "Forbidden - Playlist not available",
    },
    tags=["Playlists"],
    manual_parameters=[
        openapi.Parameter(
            name='playlist_id',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            description='ID of the playlist',
            required=True,
        ),
    ]
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def playlist_detail(request, playlist_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.owner != request.user and playlist.public:
        return Response("Playlist not available", status=status.HTTP_403_FORBIDDEN)
    return JsonResponse({'title': playlist.title, 'owner': playlist.owner.username,
                         'public': playlist.public, 'id': playlist.id})


@swagger_auto_schema(
    method='POST',
    operation_summary="Create a new playlist",
    request_body=PlaylistSerializer,
    responses={
        200: "OK - Playlist created successfully",
        400: "Bad Request - Invalid data provided",
        401: "Unauthorized - Authentication required",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_playlist(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    serializer = PlaylistSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response("OK", status=status.HTTP_200_OK)
    return Response("Nah-ah", status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='GET',
    operation_summary="Get public playlists",
    responses={
        200: "OK - List of public playlists",
        401: "Unauthorized - Authentication required",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_public_playlists(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    playlists = Playlist.objects.filter(public=True)
    return JsonResponse({'playlists': [{'title': playlist.title, 'owner': playlist.owner.username,
                                        'public': playlist.public, 'id': playlist.id} for playlist in playlists]})


@swagger_auto_schema(
    method='GET',
    operation_summary="Get available playlists",
    responses={
        200: "OK - List of available playlists",
        401: "Unauthorized - Authentication required",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_available_playlists(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    playlists = Playlist.objects.filter(Q(public=True) | Q(owner=request.user))
    return JsonResponse({'playlists': [{'title': playlist.title, 'owner': playlist.owner.username,
                                        'public': playlist.public, 'id': playlist.id} for playlist in playlists]})


@swagger_auto_schema(
    method='POST',
    request_body=TrackSerializer,
    responses={
        200: "OK - Track created successfully",
        400: "Bad Request - Invalid data provided",
        401: "Unauthorized - Authentication required",
    },
    tags=["Tracks"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_track(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    serializer = TrackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("OK", status=status.HTTP_200_OK)
    return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    responses={
        200: "OK - Track added to playlist successfully",
        401: "Unauthorized - Authentication required",
        404: "Not Found - Track or playlist not found",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_track_to_playlist(request, track_id, playlist_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    track = get_object_or_404(Track, id=track_id)
    playlist = get_object_or_404(Playlist, id=playlist_id)
    playlist.tracks.add(track)

    return Response("OK", status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='GET',
    operation_summary="Get tracks of a playlist",
    responses={
        200: "OK - List of tracks for the playlist",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - Playlist not found",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def playlist_tracks(request, playlist_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    playlist = get_object_or_404(Playlist, id=playlist_id)

    if request.user == playlist.owner or playlist.public:
        tracks = playlist.tracks.all()
        return JsonResponse({'tracks': [{'title': track.title, 'artist': track.artist,
                                         'duration': track.duration, 'id': track.id} for track in tracks],
                             'id': playlist.id, 'owner': playlist.owner.username})

    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete a track from a playlist",
    responses={
        200: "OK - Track deleted successfully",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - Playlist or track not found",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_track_from_playlist(request, playlist_id, track_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.owner == request.user or playlist.public:
        track = get_object_or_404(Track, id=track_id)
        playlist.tracks.remove(track)
        return Response("OK", status=status.HTTP_200_OK)
    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(
    method='DELETE',
    operation_summary="Delete a playlist",
    responses={
        200: "OK - Playlist deleted successfully",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - Playlist not found",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_playlist(request, playlist_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.owner == request.user or playlist.public:
        playlist.delete()
        return Response("OK", status=status.HTTP_200_OK)
    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update a playlist",
    request_body=PlaylistSerializer,
    responses={
        200: "OK - Playlist updated successfully",
        400: "Bad Request - Invalid data provided",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - Playlist not found",
    },
    tags=["Playlists"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_playlist(request,playlist_id):
    if not request.user.is_authenticated:
        return Response("User not authenticated", status=status.HTTP_401_UNAUTHORIZED)

    playlist = get_object_or_404(Playlist, id=playlist_id)

    if request.user == playlist.owner or playlist.public:
        serializer = PlaylistSerializer(playlist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response("OK", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(
    method='PATCH',
    operation_summary="Update a track",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='int'),
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'artist': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'duration': openapi.Schema(type=openapi.TYPE_INTEGER, description='int'),
        },
        required=['id', 'track']),
    responses={
        200: "OK - Track updated successfully",
        400: "Bad Request - Invalid data provided",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - Track not found",
    },
    tags=["Tracks"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def update_track(request):
    if not request.user.is_authenticated:
        return Response("User not authenticated", status=status.HTTP_401_UNAUTHORIZED)

    track = get_object_or_404(Track, id=request.data.get('id'))

    serializer = TrackSerializer(track, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response("OK", status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='PUT',
    operation_summary="Change the playlist of a track",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='int'),
            'old_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='int'),
            'new_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='int'),
        },
        required=['id', 'old_id', "new_id"]),
    responses={
        200: "OK - Playlist changed successfully",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - Track or playlist not found",
    },
    tags=["Tracks"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def change_track_playlist(request):
    if not request.user.is_authenticated:
        return Response("User not authenticated", status=status.HTTP_401_UNAUTHORIZED)
    track = get_object_or_404(Track, id=request.data.get('id'))
    playlist_new = get_object_or_404(Playlist, id=request.data.get('new_id'))
    playlist_old = get_object_or_404(Playlist, id=request.data.get('old_id'))
    if (playlist_new.owner == request.user or playlist_new.public) and (
            playlist_old.owner == request.user or playlist_old.public):
        playlist_old.tracks.remove(track)
        playlist_new.tracks.add(track)
        return Response("Success", status=status.HTTP_200_OK)
    return Response("Wrong user", status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(
    method='GET',
    responses={
        200: "OK - Tracks retrieved successfully",
        401: "Unauthorized - Authentication required",
    },
    tags=["Tracks"],
)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_all_tracks(request):
    if not request.user.is_authenticated:
        return Response("User not authenticated", status=status.HTTP_401_UNAUTHORIZED)
    tracks = Track.objects.all()
    return JsonResponse({'tracks': [{'title': track.title, 'artist': track.artist,
                                     'duration': track.duration, 'id': track.id} for track in tracks]})
