import time as t
import json as j
import os
import tempfile
from watchdog.observers import Observer as O
from watchdog.events import FileSystemEventHandler as F

class DirectoryWatcherHandler(F):
    def __init__(self, log_file):
        
        self.log_file = log_file
        self.last_changes = {}

    def on_any_event(self, event):
        file_name = os.path.basename(event.src_path)

        if file_name.startswith(".") or file_name.endswith(("~", "#")):
            return

        if event.event_type == "created":
            change_type = "created"
        elif event.event_type == "deleted":
            change_type = "deleted"
        elif event.event_type == "modified":
            change_type = "modified"
        elif event.event_type == "moved":
            change_type = "moved"
        elif event.event_type == "opened":
            change_type = "opened"
        else:
            return

        current_time = t.time()

        if file_name in self.last_changes and (current_time - self.last_changes[file_name]) < 1:
            return
        
        time_str = t.strftime("%Y-%m-%d %H:%M:%S", t.localtime(current_time))

       
        log_entry = {
            "file_name": file_name,
            "change_type": change_type,
            "time": time_str
        }

        try:
            with open(self.log_file, "a") as f:
                j.dump(log_entry, f, ensure_ascii=False)
                f.write("\n")
            self.last_changes[file_name] = current_time
        except Exception as e:
            print(f"Failed to write log: {e}")

if __name__ == "__main__":
    watch_directory = "C:\\Users\\HP\\Desktop\\bsm\\test" 
    log_file = "C:\\Users\\HP\\Desktop\\bsm\\logs\\changes.json"  

    with tempfile.NamedTemporaryFile(delete=False) as temp_pid_file:
        pid_file = temp_pid_file.name
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

    event_handler = DirectoryWatcherHandler(log_file)
    observer = O()
    observer.schedule(event_handler, watch_directory, recursive=True)

    print(f"Watching started on directory: {watch_directory}")
    
    try:
        observer.start()
        while True:
            t.sleep(1) 
    except KeyboardInterrupt:
        observer.stop()
    finally:
        os.remove(pid_file)

