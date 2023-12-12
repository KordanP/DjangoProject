from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
import json

from .models import Playlist, Track
from .views import playlist_list, playlist_detail, create_playlist, get_public_playlists, create_track


class PlaylistListTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.playlist = Playlist.objects.create(title='Test Playlist', owner=self.user, public=True)

    def test_playlist_list_authenticated(self):
        request = self.factory.get('/api/playlists/')
        force_authenticate(request, user=self.user)

        response = playlist_list(request)
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('playlists', data)
        self.assertIn('user', data)
        self.assertEqual(data['user'], self.user.username)
        self.assertEqual(len(data['playlists']), 1)
        self.assertEqual(data['playlists'][0]['title'], self.playlist.title)
        self.assertEqual(data['playlists'][0]['owner'], self.playlist.owner.username)
        self.assertEqual(data['playlists'][0]['public'], self.playlist.public)
        self.assertEqual(data['playlists'][0]['id'], self.playlist.id)

    def test_playlist_list_unauthenticated(self):
        request = self.factory.get('/api/playlists/')

        response = playlist_list(request)
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 401)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Authentication required')

class PlaylistDetailTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.playlist = Playlist.objects.create(title='Test Playlist', owner=self.user, public=True)



    def test_playlist_detail_authenticated_owner(self):
        request = self.factory.get(f'/api/playlists/{self.playlist.id}/')
        force_authenticate(request, user=self.user)

        response = playlist_detail(request, playlist_id=self.playlist.id)
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], self.playlist.title)
        self.assertEqual(data['owner'], self.playlist.owner.username)
        self.assertEqual(data['public'], self.playlist.public)
        self.assertEqual(data['id'], self.playlist.id)

    def test_playlist_detail_authenticated_not_owner(self):
        other_user = User.objects.create_user(username='otheruser', password='testpassword')
        request = self.factory.get(f'/api/playlists/{self.playlist.id}/')
        force_authenticate(request, user=other_user)

        response = playlist_detail(request, playlist_id=self.playlist.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, "Playlist not available")

    def test_playlist_detail_unauthenticated(self):
        request = self.factory.get(f'/api/playlists/{self.playlist.id}/')

        response = playlist_detail(request, playlist_id=self.playlist.id)

        self.assertEqual(response.status_code, 401)

    def test_playlist_detail_nonexistent_playlist(self):
        request = self.factory.get('/api/playlists/999/')  # Assuming there's no playlist with ID 999
        force_authenticate(request, user=self.user)

        response = playlist_detail(request, playlist_id=999)

        self.assertEqual(response.status_code, 404)


class CreatePlaylistTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_playlist_authenticated_valid_data(self):
        request_data = {'title': 'New Playlist', 'public': True}
        request = self.factory.post('/api/playlists/', data=request_data, format='json')
        force_authenticate(request, user=self.user)

        response = create_playlist(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Playlist.objects.count(), 1)
        playlist = Playlist.objects.first()
        self.assertEqual(playlist.title, request_data['title'])
        self.assertEqual(playlist.public, request_data['public'])
        self.assertEqual(playlist.owner, self.user)

    def test_create_playlist_authenticated_invalid_data(self):
        invalid_request_data = {'title': ''}
        request = self.factory.post('/api/playlists/', data=invalid_request_data, format='json')
        force_authenticate(request, user=self.user)

        response = create_playlist(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Playlist.objects.count(), 0)

    def test_create_playlist_unauthenticated(self):
        request_data = {'title': 'New Playlist', 'public': True}
        request = self.factory.post('/api/playlists/', data=request_data, format='json')

        response = create_playlist(request)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Playlist.objects.count(), 0)


class GetPublicPlaylistsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.public_playlist = Playlist.objects.create(title='Public Playlist', owner=self.user, public=True)
        self.private_playlist = Playlist.objects.create(title='Private Playlist', owner=self.user, public=False)

    def test_get_public_playlists_authenticated(self):
        request = self.factory.get('/api/public-playlists/')
        force_authenticate(request, user=self.user)

        response = get_public_playlists(request)
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('playlists', data)
        self.assertEqual(len(data['playlists']), 1)
        self.assertEqual(data['playlists'][0]['title'], self.public_playlist.title)
        self.assertEqual(data['playlists'][0]['owner'], self.public_playlist.owner.username)
        self.assertEqual(data['playlists'][0]['public'], self.public_playlist.public)
        self.assertEqual(data['playlists'][0]['id'], self.public_playlist.id)

    def test_get_public_playlists_unauthenticated(self):
        request = self.factory.get('/api/public-playlists/')

        response = get_public_playlists(request)

        self.assertEqual(response.status_code, 401)


    def test_get_public_playlists_with_private_playlist(self):
        other_user = User.objects.create_user(username='otheruser', password='testpassword')
        request = self.factory.get('/api/public-playlists/')
        force_authenticate(request, user=other_user)

        response = get_public_playlists(request)
        data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('playlists', data)
        self.assertEqual(len(data['playlists']), 1)
        self.assertEqual(data['playlists'][0]['title'], self.public_playlist.title)
        self.assertEqual(data['playlists'][0]['owner'], self.public_playlist.owner.username)
        self.assertEqual(data['playlists'][0]['public'], self.public_playlist.public)
        self.assertEqual(data['playlists'][0]['id'], self.public_playlist.id)


class CreateTrackTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_track_authenticated_valid_data(self):
        request_data = {'title': 'New Track', 'artist': 'New Artist', 'duration': 180}
        request = self.factory.post('/api/tracks/', data=request_data, format='json')
        force_authenticate(request, user=self.user)

        response = create_track(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Track.objects.count(), 1)
        track = Track.objects.first()
        self.assertEqual(track.title, request_data['title'])
        self.assertEqual(track.artist, request_data['artist'])
        self.assertEqual(track.duration, request_data['duration'])

    def test_create_track_authenticated_invalid_data(self):
        invalid_request_data = {'title': '', 'artist': 'Invalid Artist', 'duration': -5}
        request = self.factory.post('/api/tracks/', data=invalid_request_data, format='json')
        force_authenticate(request, user=self.user)

        response = create_track(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Track.objects.count(), 0)

    def test_create_track_unauthenticated(self):
        request_data = {'title': 'New Track', 'artist': 'New Artist', 'duration': 180}
        request = self.factory.post('/api/tracks/', data=request_data, format='json')

        response = create_track(request)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Track.objects.count(), 0)