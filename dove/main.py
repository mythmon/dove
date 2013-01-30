from xmlrpclib import MultiCall

from dove import rtorrent, db, downloader


def main():
    with rtorrent.ConnectionManager() as rt:
        hashes = rt.download_list()
        mc = MultiCall(rt)
        session = db.get_session()

        for h in hashes:
            mc.d.get_complete(h)

        for h, done in zip(hashes, mc()):
            torrent, _ = db.get_or_create(session, db.Torrent, info_hash=h)
            if done:
                torrent.state = 'ready'
            else:
                torrent.state = 'incomplete'

            print h, done, torrent.state
            downloader.get(rt, torrent)

            session.add(torrent)

        session.commit()


if __name__ == '__main__':
    main()
