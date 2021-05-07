from subprocess import check_output, Popen, PIPE


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

print(getPidof("ffplay.exe", "-nodisp -autoexit -loglevel 8 -volume 100 -stats -i -"))
print(getPidof("youtube-dl.exe", "-q -f bestaudio"))