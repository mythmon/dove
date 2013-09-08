from sqlalchemy import or_
from xmlrpclib import MultiCall

from dove import rtorrent, db, downloader


def print_progress(state):
    print(state)


def main():
    print_progress('Starting connection')
    with rtorrent.ConnectionManager() as rt:
        print_progress('Getting torrent list')
        hashes = rt.download_list()
        mc = MultiCall(rt)
        session = db.get_session()

        for h in hashes:
            mc.d.get_complete(h)

        print_progress('Getting torrent statuses')

        for h, done in zip(hashes, mc()):
            torrent, created = db.get_or_create(session, db.Torrent, {'state': 'incomplete'}, info_hash=h)

            if torrent.state == 'incomplete' and done:
                torrent.state = 'ready'

            print h, done, torrent.state
            session.add(torrent)
        session.commit()

        print_progress('Starting downloads')
        ready_torrents = session.query(db.Torrent).filter(
            or_(db.Torrent.state == 'ready',
                db.Torrent.state == 'downloading',
                db.Torrent.state == 'error'))

        dlman = downloader.DownloadManager(rt, session)
        for torrent in ready_torrents:
            dlman.add_torrent(torrent)
        dlman.download_all()

        print_progress('Done')


if __name__ == '__main__':
    main()
