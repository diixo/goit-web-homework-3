# from task04_path
import re
import os
import shutil
import sys
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import RLock, Thread
import logging

executor = ThreadPoolExecutor(max_workers=2)
category_files = dict()
category_exts  = dict()

##########################################################
img_f = {".jpeg", ".png", ".jpg", ".svg", ".bmp", ".ico"}
mov_f = {".avi", ".mp4", ".mov", ".mkv", ".webm", ".wmv", ".flv"}
doc_f = {".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx", ".ini", ".cmd", ".ppt", ".xml", ".msg", ".cpp", ".hpp", ".py", ".md", ".csv"}
mus_f = {".mp3", ".ogg", ".wav", ".amr", ".aiff"}
arch_f = {".zip", ".tar"}

##########################################################
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

CATEGORIES = { "images" : img_f, "video" : mov_f, "documents" : doc_f, "audio": mus_f, "archives" : arch_f, "others" : {} }
TRANS = {}
for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = t
    TRANS[ord(c.upper())] = t.upper()

###########################################################
def getCategory(suffix: str):
    for cat, exts in CATEGORIES.items():
        if suffix in exts:
            return cat, True
    return "others", False

###########################################################
def normalize(name):
    rename = name.translate(TRANS)
    rename = re.sub(r'[^a-zA-Z0-9 -]', "_", rename)
    return rename
###########################################################
def moveStatistic():
    global category_files, category_exts

    if len(category_exts.items()) > 0:
        print(f"{'='*18} #Extentions {'='*19}")
        for cat, exts in category_exts.items():
            print(f"[{cat}.*]: {exts}")
        print("="*50)

    if len(category_files.items()) > 0:
        print(f"{'='*21} #Files {'='*21}")
        for cat, amount in category_files.items():
            print(f"[{cat}]: {amount}")
        print("="*50)

def job_move_file(file_src: str, file_dest: str, category: str, suffix: str):
    #pathFile.replace(targetFile)
    #shutil.copyfile(file_src, file_dest)

    locker = RLock()
    #locker.acquire()
    with locker:
        category_files[category] = category_files.get(category, 0) + 1
        exts = category_exts.get(category, set())
        exts.add(suffix)
        category_exts[category] = exts
    #locker.release()

    logging.debug(f"COPY: from# {file_src} to# {file_dest}")

def job_unpack_archive(file_src: str, file_dest: str):
    #shutil.unpack_archive(file_src, file_dest)
    logging.debug(f"UNPACK: from# {file_src} to# {file_dest}")

###########################################################
def parse_directory(root, ipath = None):
    global executor
    if not Path(root).exists(): return False

    # check if current directory is root.
    absPath = root if ipath == None else ipath

    folders = []
    path = Path(absPath)
    absPath += "/"

    for i in path.iterdir():
        if i.is_dir():
            if ipath == None:
                if i.name.lower() in CATEGORIES.keys():
                    continue

            parse_directory(root, absPath + i.name)
        
        elif i.is_file():
            pathFile = Path(absPath + i.name)
            suffix = pathFile.suffix.lower()
            cat, success = getCategory(suffix)
            # if success:
            # for any category:
            newName = normalize(pathFile.stem)

            # prepare target folder for category
            targetDir = Path(root + "/" + cat)

            if not targetDir.exists():
                targetDir.mkdir()

            targetFile = Path(root + "/" + cat + "/" + newName + suffix)
            if targetFile.exists():
                targetFile = targetFile.with_name(f"{targetFile.stem}-{uuid.uuid4()}{suffix}")

            #move-copy file to destination category-directory in separated Thread:
            executor.submit(job_move_file, str(pathFile.absolute()), str(targetFile.absolute()), cat, suffix)

            if cat == "archives":
                #unpack file in separated Thread
                executor.submit(job_unpack_archive, str(targetFile.absolute()), root + "/" + cat + "/" + targetFile.stem)

#############################################################
def rm_directory(root, ipath = None):
    if not Path(root).exists(): return False

    # check if current directory is root.
    absPath = root if ipath == None else ipath

    folders = []
    path = Path(absPath)
    absPath += "/"

    for i in path.iterdir():
        if i.is_dir():
            if ipath == None:
                if i.name.lower() in CATEGORIES.keys():
                    continue
            
            folders.append(i.name)
    #*********************************
    for i, dirName in enumerate(folders):
        if rm_directory(root, absPath + dirName) == True:
            # remove sub-directory if is empty
            rmDir = Path(absPath + dirName)
            logging.debug(f"RMDIR: {rmDir.absolute()}")

    return len(folders) == 0

###############################################################
def main():
    global executor

    root = "."
    if len(sys.argv) > 1:
        root = sys.argv[1]
    path = Path(root)

    if not path.exists():
        return f"Folder with path {root} doesn`t exists."

    parse_directory(root)

    # stop with blocking current thread before shutdown, but waits for all threads will be finished
    executor.shutdown(wait=True)

    # start to remove all sub-directories in separated thread
    thread = Thread(target=rm_directory, args=(root,))
    thread.start()
    thread.join()

    # выводим статистику перемещения всех файлов по категориям, которые были перемещены последним вызовом приложения
    moveStatistic()

    return "Ok"
###############################################################
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    print(main())
