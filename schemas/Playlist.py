class Playlist(dict):
    def __init__(self, name, owner, id, images):
        dict.__init__(self, name=name, owner=owner, id=id, images=images)
            # self.name = name
            # self.owner = owner
            # self.id = id
            # self.images = images
