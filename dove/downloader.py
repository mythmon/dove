import os
import shlex
import subprocess
import xmlrpclib
from time import sleep

from dove.config import config


class DownloadManager(object):

    def __init__(self, rt, session):
        self.session = session
        self.rt = rt

        self.torrent_queue = []
        self.current_downloads = []

        try:
            os.makedirs(config['download_dir'])
        except OSError as e:
            if 'File exists' not in str(e):
                raise

    def add_torrent(self, torrent):
        self.torrent_queue.append(torrent)

    def download_all(self):
        while self.torrent_queue or self.current_downloads:
            self._load_up_queue()
            self._wait_for_one_finish()

    def _load_up_queue(self):
        while (len(self.current_downloads) < config['parallel'] and 
               self.torrent_queue):
            print 'Adding job'
            try:
                torrent = self.torrent_queue.pop()
            except IndexError:
                return

            try:
                job = TorrentJob(self.rt, self.session, torrent)
            except xmlrpclib.Fault:
                # There was an error communicating with the server.
                torrent.state = 'error'
                self.session.add(torrent)
                self.session.commit()
                print 'Problem getting torrent from server.'
                continue

            self.current_downloads.append(job)

    def _wait_for_one_finish(self):
        while True:
            for download in self.current_downloads:
                done = False
                if download.is_done():
                    self.current_downloads.remove(download)
                    print 'Job done'
                    done = True
                if done:
                    return
            sleep(5)


class TorrentJob(object):

    def __init__(self, rt, session, torrent):
        self.torrent = torrent
        self.rt = rt
        self.session = session

        dir_path = self.rt.d.get_directory(torrent.info_hash)
        target_path = self.rt.d.get_name(torrent.info_hash)
        # Handle both files and directories
        if dir_path.endswith(target_path):
            remote_path = dir_path
        else:
            remote_path = os.path.join(dir_path, target_path)

        # It would be bad if this were zero length.
        assert remote_path

        rsync_command = [
            'rsync',
        ]
        rsync_command.extend(shlex.split(config['rsync_opts']))
        remote_path = remote_path.replace('"', '\\"')
        rsync_command.extend([
            '--rsh=ssh -p{rsync_port}'.format(**config),
            '{rsync_user}@{rsync_host}:"{remote_path}"'
                .format(remote_path=remote_path, **config),
            config['download_dir']
        ])

        torrent.state = 'downloading'
        self.session.add(torrent)
        self.session.commit()

        print rsync_command

        self.rsync = subprocess.Popen(rsync_command)

    def is_done(self):
        code = self.rsync.poll()
        if code is None:
            return False
        else:
            if code == 0:
                self.torrent.state = 'done'
            else:
                self.torrent.state = 'error'
            self.rsync.wait()
            self.session.add(self.torrent)
            self.session.commit()
            return True
