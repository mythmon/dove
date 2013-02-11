import os
import shlex
import subprocess

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
        while len(self.torrent_queue) > 0:
            self._load_up_queue()
            self._wait_for_one_finish()

    def _load_up_queue(self):
        while len(self.current_downloads) < config['parallel']:
            torrent = self.torrent_queue.pop()
            job = TorrentJob(self.rt, self.session, torrent)
            self.current_downloads.append(job)

    def _wait_for_one_finish(self):
        while True:
            for download in self.current_downloads:
                done = False
                if download.is_done():
                    done = True
            if done:
                return


class TorrentJob(object):

    def __init__(self, rt, session, torrent):
        self.torrent = torrent
        self.rt = rt
        self.session = session

        dir_path = self.rt.d.get_directory(torrent.info_hash)
        target_path = self.rt.d.get_name(torrent.info_hash)
        if dir_path.endswith(target_path):
            remote_path = dir_path
        else:
            remote_path = os.path.join(dir_path, target_path)

        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print 'dir_path', dir_path
        print 'target_path', target_path
        print 'remote_path', remote_path
        print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

        # It would be bad if this were zero length.
        assert remote_path

        rsync_command = [
            'rsync',
        ]
        rsync_command.extend(shlex.split(config['rsync_opts']))
        rsync_command.extend([
            '--rsh=ssh -p{ssh_port}'.format(**config),
            "{ssh_user}@{ssh_host}:'{remote_path}'"
                .format(remote_path=remote_path, **config),
            config['download_dir']
        ])

        print rsync_command
        print ' '.join(rsync_command)

        torrent.state = 'downloading'
        self.session.add(torrent)
        self.session.commit()

        self.rsync = subprocess.Popen(rsync_command)

    def is_done(self):
        code = self.rsync.poll()
        if code is not None:
            if code == 0:
                self.torrent.state = 'done'
            else:
                self.torrent.state = 'error'
            self.session.add(self.torrent)
            self.session.commit()
            return True

        return False
