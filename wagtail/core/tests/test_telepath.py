import unittest
from django.test import TestCase

from wagtail.core.telepath import Adapter, JSContext, register


class Artist:
    def __init__(self, name):
        self.name = name


class Album:
    def __init__(self, title, artists):
        self.title = title
        self.artists = artists


class ArtistAdapter(Adapter):
    js_constructor = 'music.Artist'

    def js_args(self, obj):
        return [obj.name]


register(ArtistAdapter(), Artist)


class AlbumAdapter(Adapter):
    js_constructor = 'music.Album'

    def js_args(self, obj):
        return [obj.title, obj.artists]

    class Media:
        js = ['music_player.js']


register(AlbumAdapter(), Album)


class TestPacking(TestCase):
    def test_pack_object(self):
        beyonce = Artist("Beyoncé")
        ctx = JSContext()
        result = ctx.pack(beyonce)

        self.assertEqual(result, {'_type': 'music.Artist', '_args': ["Beyoncé"]})

    def test_pack_list(self):
        destinys_child = [
            Artist("Beyoncé"), Artist("Kelly Rowland"), Artist("Michelle Williams")
        ]
        ctx = JSContext()
        result = ctx.pack(destinys_child)

        self.assertEqual(result, [
            {'_type': 'music.Artist', '_args': ["Beyoncé"]},
            {'_type': 'music.Artist', '_args': ["Kelly Rowland"]},
            {'_type': 'music.Artist', '_args': ["Michelle Williams"]},
        ])

    def test_pack_dict(self):
        glastonbury = {
            'pyramid_stage': Artist("Beyoncé"),
            'acoustic_stage': Artist("Ed Sheeran"),
        }
        ctx = JSContext()
        result = ctx.pack(glastonbury)
        self.assertEqual(result, {
            'pyramid_stage': {'_type': 'music.Artist', '_args': ["Beyoncé"]},
            'acoustic_stage': {'_type': 'music.Artist', '_args': ["Ed Sheeran"]},
        })

    def test_dict_reserved_words(self):
        profile = {
            '_artist': Artist("Beyoncé"),
            '_type': 'R&B',
        }
        ctx = JSContext()
        result = ctx.pack(profile)

        self.assertEqual(result, {
            '_dict': {
                '_artist': {'_type': 'music.Artist', '_args': ["Beyoncé"]},
                '_type': 'R&B',
            }
        })

    def test_recursive_arg_packing(self):
        dangerously_in_love = Album("Dangerously in Love", [
            Artist("Beyoncé"),
        ])
        ctx = JSContext()
        result = ctx.pack(dangerously_in_love)

        self.assertEqual(result, {
            '_type': 'music.Album',
            '_args': [
                "Dangerously in Love",
                [
                    {'_type': 'music.Artist', '_args': ["Beyoncé"]},
                ]
            ]
        })

        self.assertIn('music_player.js', str(ctx.media))

    @unittest.expectedFailure
    def test_object_references(self):
        beyonce = Artist("Beyoncé")
        jay_z = Artist("Jay-Z")
        discography = [
            Album("Dangerously in Love", [beyonce]),
            Album("Everything Is Love", [beyonce, jay_z]),
        ]
        ctx = JSContext()
        result = ctx.pack(discography)

        self.assertEqual(result, [
            {
                '_type': 'music.Album',
                '_args': [
                    "Dangerously in Love",
                    [
                        {'_type': 'music.Artist', '_args': ["Beyoncé"], '_id': 0},
                    ]
                ]
            },
            {
                '_type': 'music.Album',
                '_args': [
                    "Everything Is Love",
                    [
                        {'_ref': 0},
                        {'_type': 'music.Artist', '_args': ["Jay-Z"]},
                    ]
                ]
            },
        ])

        self.assertIn('music_player.js', str(ctx.media))

    @unittest.expectedFailure
    def test_list_references(self):
        destinys_child = [
            Artist("Beyoncé"), Artist("Kelly Rowland"), Artist("Michelle Williams")
        ]
        discography = [
            Album("Destiny's Child", destinys_child),
            Album("Survivor", destinys_child),
        ]
        ctx = JSContext()
        result = ctx.pack(discography)

        self.assertEqual(result, [
            {
                '_type': 'music.Album',
                '_args': [
                    "Destiny's Child",
                    {
                        '_list': [
                            {'_type': 'music.Artist', '_args': ["Beyoncé"]},
                            {'_type': 'music.Artist', '_args': ["Kelly Rowland"]},
                            {'_type': 'music.Artist', '_args': ["Michelle Williams"]},
                        ],
                        '_id': 0,
                    }
                ]
            },
            {
                '_type': 'music.Album',
                '_args': [
                    "Survivor",
                    {'_ref': 0},
                ]
            },
        ])

    @unittest.expectedFailure
    def test_primitive_value_references(self):
        beyonce_name = "Beyoncé"
        beyonce = Artist(beyonce_name)
        discography = [
            Album("Dangerously in Love", [beyonce]),
            Album(beyonce_name, [beyonce]),
        ]
        ctx = JSContext()
        result = ctx.pack(discography)

        self.assertEqual(result, [
            {
                '_type': 'music.Album',
                '_args': [
                    "Dangerously in Love",
                    [
                        {
                            '_type': 'music.Artist',
                            '_args': [{'_val': "Beyoncé", '_id': 1}],
                            '_id': 0,
                        },
                    ]
                ]
            },
            {
                '_type': 'music.Album',
                '_args': [
                    {'_ref': 1},
                    [
                        {'_ref': 0},
                    ]
                ]
            },
        ])
