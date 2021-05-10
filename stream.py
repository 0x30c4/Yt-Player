#!/usr/bin/python3
from subprocess import Popen, PIPE
from sys import stderr, argv
from os import name, remove, system, path, chdir
from psutil import Process, process_iter


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class Stream:
    def __init__(self, cookies = 'cookies.txt', _search = None):
        self._search = _search
        self.cookies = cookies
        
        # self.ytdlcmdline = [self.ytdlexe, "--force-ipv4", "--cookies", self.cookies, "-q", "-f", "bestaudio", self.songNameOrUrl, "-o", "-"]
        # self.ffplaycmdline = [self.ffplay, "-nodisp", "-autoexit", "-loglevel", "8", "-volume", "100", "-stats", "-i", "-"]

        self.ytdlcmdline = ['', "--force-ipv4", "--cookies", self.cookies, "-q", "-f", "bestaudio", '', "-o", "-"]
        self.ffplaycmdline = ['', "-nodisp", "-autoexit", "-loglevel", "8", "-volume", "100", "-stats", "-i", "-"]


        self.ctime = 0
        self.stats = {
            "CS": 0,
            "TS": 0,
            "H": 0,
            "M": 0,
            "S": 0
        }

    def _getDuration(self):
        try:
            with Popen([self.ytdlexe, "--get-duration", "--cookies", self.cookies, self.songNameOrUrl], stdout=PIPE) as d:
                du = d.stdout.readline().decode().strip().split(":")
                # print(du)
                if du.__len__() == 1:
                    self.stats["S"] = int(du[0]) if bool(du[0]) else 0
                elif du.__len__() == 2:
                    self.stats["M"] = int(du[0]) if bool(du[0]) else 0
                    self.stats["S"] = int(du[1]) if bool(du[1]) else 0
                elif du.__len__() == 3:
                    self.stats["H"] = int(du[0]) if bool(du[0]) else 0
                    self.stats["M"] = int(du[1]) if bool(du[1]) else 0
                    self.stats["S"] = int(du[2]) if bool(du[2]) else 0

                self.stats["TS"] = self.stats["H"] * 3600 + self.stats["M"] * 60 + self.stats["S"]
                # print(self.stats)
        except Exception as e:
            print("Error in _getDuration : " + str(e), file=stderr)
            return False

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
        self._search = su
        self._getDuration()
        # print(self.stats)

    def play(self):
        # print(self.stats)
        self.ytdlcmdline[0] = self.ytdlexe
        self.ytdlcmdline[7] = self.songNameOrUrl
        self.ffplaycmdline[0] = self.ffplay
        try:
            with Popen(self.ytdlcmdline, stdout=PIPE) as ytproc:

                with Popen(self.ffplaycmdline, stdin=ytproc.stdout, stderr=PIPE) as ffplayproc:
                    line = ''
                    # self.stats.update({"ffplay": ffplayproc.pid})
                    # self.stats.update({"ytdl": ytproc.pid})
                    while ffplayproc.poll() is None:
                            c = ffplayproc.stderr.read(1).decode()
                            line = line + c
                            if c == '\r':
                                # line = line.replace("ALSA", "")
                                line = line.split()[0].strip()
                                try:
                                    if not line == 'nan':
                                        self.ctime = int(line.split('.')[0])
                                        self.stats["CS"] = self.ctime
                                        yield self.stats
                                    line = ''
                                except Exception as e:
                                    print("Error in play->ffplay : " + str(e), file=stderr)
                                    line = ''

        except Exception as e:
            print("Error in play : " + str(e), file=stderr)
            return False

    @staticmethod
    def getPidof(pname, argToLook):
        try:
            for proc in process_iter():
                if argToLook in " ".join(proc.cmdline()):
                    return int(proc.pid)
        except Exception as e:
            print("Error in getPidof : " + str(e), file=stderr)


    @staticmethod
    def streamCtl(command):
        try:
            pidff = Stream.getPidof(Stream.ffplay, "-nodisp -autoexit -loglevel 8 -volume 100 -stats -i -")
            pidyt = Stream.getPidof(Stream.ytdlexe, "-q -f bestaudio")
            if name != 'nt':
                if command == "pause":
                    system(f"kill -STOP {pidff}")
                elif command == "resume":
                    system(f"kill -CONT {pidff}")
                elif command == "stop":
                    system(f"kill -9 {pidff} {pidyt}")
            if pidff:
                psProcess = Process(pid=pidff)
                if command == "pause":
                    psProcess.suspend()
                elif command == "stop":
                    Process(pid=pidyt).kill()
                    psProcess.kill()
                elif command == "resume":
                    psProcess.resume()

                return True

            else:
                return False
        except Exception as e:
            print("Error in streamCtl : " + str(e), file=stderr)
            return False

if __name__ == "__main__":

    if not len(argv) == 1:
        obj = Stream()

        # print(obj.getPidof(Stream.ffplay, "-q -f bestaudio"))
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
