import csv
import urllib.parse, urllib.request
import json


def song_name_cutter(song_name):
    short_song_name = ""
    i = 0
    while i < len(song_name) and song_name[i] != '(':
        short_song_name += song_name[i]
        i += 1
    return short_song_name


def retrieve_itunes_data(title, artist):

    headers = {
        "X-Apple-Store-Front" : "143441-1,29",
        "X-Apple-Tz" : "3600"
    }
    
    url = "https://itunes.apple.com/WebObjects/MZStore.woa/wa/search?clientApplication=MusicPlayer&term=" + urllib.parse.quote(artist) + "%20" + urllib.parse.quote(title)
    
    request = urllib.request.Request(url, None, headers)

    try:
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode('utf-8'))
        songs = [result for result in data["storePlatformData"]["lockup"]["results"].values() if result["kind"] == "song"]

        for song in songs:
            if (
                    song["name"].lower() in title.lower() or
                    title.lower() in song["name"].lower()
            ) and (
                    song["artistName"].lower() in artist.lower() or
                    artist.lower() in song["artistName"].lower()
            ):
                return [song["id"], song["name"], song["artistName"]]
            else:
                short_song_name = song_name_cutter(song["name"])
                if (
                        short_song_name.lower() in title.lower() or
                        title.lower() in short_song_name.lower()
                ) and (
                        song["artistName"].lower() in artist.lower() or
                        artist.lower() in song["artistName"].lower()
                ):
                    return [song["id"], song["name"], song["artistName"]]

        for song in songs:
            if song["name"].lower() == title.lower():
                return [song["id"], song["name"], song["artistName"]]
            else:
                short_song_name = song_name_cutter(song["name"])
                if short_song_name.lower() == title.lower():
                    return [song["id"], song["name"], song["artistName"]]
                elif short_song_name.lower() in title.lower():
                    return [song["id"], song["name"], song["artistName"]]
                elif title.lower() in short_song_name.lower():
                    return [song["id"], song["name"], song["artistName"]]

    except:
        return None


itunes_identifiers = []
not_found = []


with open('spotify.csv', encoding='utf-8') as playlist_file:
    playlist_reader = csv.reader(playlist_file)
    next(playlist_reader)

    for row in playlist_reader:
        title, artist = row[1], row[3]
        itunes_data = retrieve_itunes_data(title, artist)
        if itunes_data:
            itunes_identifier = itunes_data[0]
            itunes_title = itunes_data[1]
            itunes_artist = itunes_data[2]

            if itunes_identifier:
                itunes_identifiers.append(itunes_identifier)
                print("{}: {} - {}".format(itunes_identifier, title, artist), "-> {} - {}".format(itunes_title, itunes_artist))
        else:
            not_found.append({title: artist})
            print('\033[1m', "Not Found:", '\033[0m', "{} - {}".format(title, artist))

with open('itunes.csv', 'w', encoding='utf-8') as output_file:
    for itunes_identifier in itunes_identifiers:
        output_file.write(str(itunes_identifier) + "\n")

with open('not_found.csv', 'w', encoding='utf-8') as not_found_file:
    for not_found in not_found:
        not_found_file.write(str(not_found) + "\n")
