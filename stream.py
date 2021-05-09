from pafy import new
from requests import get
from subprocess import Popen, PIPE, check_output
from youtube_dl import YoutubeDL
from sys import stderr, argv
from os import name, remove, system, path, chdir
from psutil import Process


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class Stream:
    def __init__(self, cookies = 'cookies.txt', _search = None):
        self._search = _search

        #self.ffplay = "bin\\ffplay.exe"
        #self.ytdlexe = "bin\\youtube-dl.exe"
        self.cookies = cookies

        #if name != "nt":
        #    self.ffplay = "ffplay"
        #    self.ytdlexe = "youtube-dl"

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

    @classproperty
    def ffplay(self):
        if name != "nt":
            return "ffplay"
        else:
            return "bin\\ffplay.exe"

    @classproperty
    def ytdlexe(self):
        if name != "nt":
            return "youtube-dl"
        else:
            return "bin\\youtube-dl.exe"

    @property
    def songNameOrUrl(self):
        if bool(self._search):
            if self._search.startswith("https://"):
                return self._search
            else:
                return f"ytsearch:{self._search}"

    @songNameOrUrl.setter
    def songNameOrUrl(self, su):
        print("change")
        self._search = su
        self._getDuration()

    def play(self):
        # print(self.songNameOrUrl)
        # print(self._getDuration(self.songNameOrUrl))
        try:
            with Popen([self.ytdlexe, "--force-ipv4", "--cookies", self.cookies,"-q", "-f", "bestaudio", self.songNameOrUrl, "-o", "-"], stdout=PIPE) as ytproc:

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
        if name != "nt":
            command = f"ps aux"
            try:
                with Popen(command.split(), stdout=PIPE, stdin=PIPE) as psall:
                    for line in psall.stdout.readlines():
                        line = line.decode()
                        if argToLook in line:
                            line = line.split()[1]
                            return line

            except Exception as e:
                print(str(e))
        else:
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
            pid = Stream.getPidof(Stream.ffplay, "-nodisp -autoexit -loglevel 8 -volume 100 -stats -i -")
            if pid:
                psProcess = Process(pid=pid)
                if command == "pause":
                    psProcess.suspend()
                elif command == "stop":
                    pid = Stream.getPidof(Stream.ytdlexe, "-q -f bestaudio")

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

        print(obj.getPidof(Stream.ffplay, "-nodisp -autoexit -loglevel 8 -volume 100 -stats -i -"))
        #obj.streamCtl("pause")

        if argv[1] == 'q': exit()


        if len(argv) == 2:
            if argv[1] == 'p':
                obj.streamCtl("pause")
            elif argv[1] == 's':
                obj.streamCtl("stop")
            elif argv[1] == 'r':
                obj.streamCtl("resume")

        elif len(argv) >= 2:
            obj.songNameOrUrl = " ".join(argv[1:])
            for i in obj.play():
                pass
        if argv[1].startswith("https://"):
            obj.songNameOrUrl = argv[1]
            for i in obj.play():
                print(i, end='\r')
# pyinstaller lib/stream.py ; rm -rf build ; cp -r dist/stream . ; rm -rf dist
# ./youtube-dl.exe -J -q -f bestaudio ytsearch:"tommar jonno by arnob" -o -
