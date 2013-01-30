def get(rt, torrent):
    remote_path = rt.d.get_base_path(torrent.info_hash)
    print 'going to download ' + remote_path
