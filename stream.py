from pafy import new
from requests import get
from subprocess import Popen, PIPE, check_output
from youtube_dl import YoutubeDL
from sys import stderr, argv
from os import name, remove, system, path, chdir
from psutil import Process


class Stream:
    def __init__(self, _search=None):
        self._search = _search
        self.ffplay = "bin\\ffplay.exe"
        self.ytdlexe = "bin\\youtube-dl.exe"
        self.ctime = 0
        self.stats = {
            "CS": 0,
            "TS": 0,
            "H": 0,
            "M": 0,
            "S": 0
        }
        # chdir("C:\\Users\\sami\\Desktop\\tmp\\Yt-Player")

    def _getDuration(self):
        try:
            with Popen([self.ytdlexe, "--get-duration", self.songNameOrUrl], stdout=PIPE) as d:
                du = d.stdout.readline().decode().strip().split(":")
                # print(du)
                if du.__len__() == 1:
                    self.stats["S"] = int(du[0])
                elif du.__len__() == 2:
                    self.stats["M"] = int(du[0])
                    self.stats["S"] = int(du[1])
                elif du.__len__() == 3:
                    self.stats["H"] = int(du[0])
                    self.stats["M"] = int(du[1])
                    self.stats["S"] = int(du[2])

                self.stats["TS"] = (self.stats["H"] * 3600) + (self.stats["M"] * 60) + self.stats["S"]

        except Exception as e:
            print(str(e), file=stderr)
            return False

    # @property
    # def getDuration(self):
    #     return 

    @property
    def songNameOrUrl(self):
        if bool(self._search):
            if self._search.startswith("https://"):
                return self._search
            else:
                return f"ytsearch:{self._search}"
    
    @songNameOrUrl.setter
    def songNameOrUrl(self, su):
        self._search = su
        self._getDuration()

    def play(self):
        # print(self.songNameOrUrl)
        # print(self._getDuration(self.songNameOrUrl))
        try:
            with Popen([self.ytdlexe, "-q", "-f", "bestaudio", self.songNameOrUrl, "-o", "-"], stdout=PIPE) as ytproc:

                with Popen([self.ffplay, "-nodisp", "-autoexit", "-loglevel", "8", "-volume", "100", "-stats", "-i", "-"], stdin=ytproc.stdout, stderr=PIPE) as ffplayproc:
                    line = ''
                    # self.stats.update({"ffplay": ffplayproc.pid})
                    # self.stats.update({"ytdl": ytproc.pid})
                    while ffplayproc.poll() is None:
                        c = ffplayproc.stderr.read(1).decode()
                        line = line + c
                        if c == '\r':
                            line = line.split()[0]
                            if not line == 'nan':
                                self.ctime = int(line.split('.')[0])
                                self.stats["CS"] = self.ctime
                                yield self.stats
                            line = ''

        except Exception as e:
            print(str(e), file=stderr)
            return False

    @staticmethod
    def getPidof(pname, argToLook):
        command = f"wmic process get commandline,processid"
        try:
            with Popen(command.split(), stdout=PIPE, stdin=PIPE, universal_newlines=True) as wmic:
                for line in wmic.stdout.readlines():
                    if pname in line and argToLook in line:
                        line = line.split()[-1]
                        return int(line)
        except Exception as e:
            print(str(e))


    @staticmethod
    def streamCtl(command):
        try:
            pid = Stream.getPidof("ffplay.exe", "-nodisp -autoexit -loglevel 8 -volume 100 -stats -i -")
            if pid:
                psProcess = Process(pid=pid)
                print(pid)
                if command == "pause":
                    psProcess.suspend()
                elif command == "stop":
                    pid = Stream.getPidof("youtube-dl.exe", "-q -f bestaudio")

                    Process(pid=pid).kill()
                    psProcess.kill()
                elif command == "resume":
                    psProcess.resume()

                return True

            else:
                return False
        except Exception as e:
            print(str(e))
            return False

if __name__ == "__main__":

    if not len(argv) == 1:
        obj = Stream()

        if argv[1] == 'p' and len(argv) == 2:
            obj.streamCtl("pause") 
        elif argv[1] == 's' and len(argv) == 2:
            obj.streamCtl("stop")
        elif argv[1] == 'r' and len(argv) == 2:
            obj.streamCtl("resume")
        elif len(argv) >= 2:
            obj.songNameOrUrl = " ".join(argv[1:])
            
            # print(obj.songNameOrUrl)
            # print(obj.duration)

            for i in obj.play():
                print(i)
# pyinstaller lib/stream.py ; rm -rf build ; cp -r dist/stream . ; rm -rf dist
# ./youtube-dl.exe -J -q -f bestaudio ytsearch:"tommar jonno by arnob" -o - 