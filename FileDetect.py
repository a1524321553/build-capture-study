import os
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY
from common import removeDir

tempPath = ""


# sudo sysctl fs.inotify.max_user_watches=16384
# echo 16384 | sudo tee -a /proc/sys/fs/inotify/max_user_watches
# for more information about pyinotify:
# http://seb.dbzteam.org/pyinotify/

class EventHandler(ProcessEvent):
    def process_IN_CREATE(self, event):
        if os.path.isfile(os.path.join(event.path, event.name)):
            os.system("cp -f " + os.path.join(event.path, event.name) + " " + os.path.join(tempPath, event.name))
        elif os.path.isdir(os.path.join(event.path, event.name)):
            os.system("cp -rf " + os.path.join(event.path, event.name) + " " + os.path.join(tempPath, event.name))
        # print "Create file:%s." %os.path.join(event.path,event.name)

    def process_IN_DELETE(self, event):
        return 0

    # print "Delete file:%s." %os.path.join(event.path,event.name)

    def process_IN_MODIFY(self, event):
        if os.path.isfile(os.path.join(event.path, event.name)):
            os.system("cp -f " + os.path.join(event.path, event.name) + " " + os.path.join(tempPath, event.name))
        elif os.path.isdir(os.path.join(event.path, event.name)):
            os.system("cp -rf " + os.path.join(event.path, event.name) + " " + os.path.join(tempPath, event.name))
        # print "Modify file:%s." %os.path.join(event.path,event.name)


def FsMonitor(path='.'):
    global tempPath
    tempPath = os.path.join(path, "../BCFILES")
    if os.path.exists(tempPath):
        removeDir(tempPath)
    os.mkdir(tempPath)

    wm = WatchManager()
    mask = IN_DELETE | IN_CREATE | IN_MODIFY
    notifier = Notifier(wm, EventHandler())
    wm.add_watch(path, mask, auto_add=True, rec=True)

    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            notifier.stop()
            break
