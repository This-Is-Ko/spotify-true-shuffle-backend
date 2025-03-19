class Playlist(dict):
    def __init__(self, name, owner, id, images, numOfTracks):
        dict.__init__(self, name=name, owner=owner, id=id, images=images, numOfTracks=numOfTracks)
        # self.name = name
        # self.owner = owner
        # self.id = id
        # self.images = images
