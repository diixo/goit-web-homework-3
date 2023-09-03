# from task04_path
import re
import os
import shutil
import sys
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
import logging

executor = ThreadPoolExecutor(max_workers=2)
category_files = dict()
category_exts  = dict()

##########################################################
img_f = {'.jpeg', '.png', '.jpg', '.svg', ".bmp", ".ico"}
mov_f = {'.avi', '.mp4', '.mov', '.mkv', ".webm", ".wmv", ".flv"}
doc_f = {'.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx', ".ini", ".cmd", ".ppt", ".xml", ".msg", ".cpp", ".hpp", ".py", ".md", ".csv"}
mus_f = {'.mp3', '.ogg', '.wav', '.amr', ".aiff"}
arch_f = {'.zip', '.tar'}

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

    if len(category_files.items()) > 0:
        print(f"{'='*21} #Files {'='*21}")
        for cat, amount in category_files.items():
            print(f"[{cat}]: {amount}")
        print("="*50)

    if len(category_exts.items()) > 0:
        print(f"{'='*18} #Extentions {'='*19}")
        for cat, exts in category_exts.items():
            print(f"[{cat}.*]: {exts}")
        print("="*50)

def job_copy_file(file_src: str, file_dest: str, category: str, suffix: str):
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
            
            folders.append(i.name)
        
        elif i.is_file():
            pathFile = Path(absPath + i.name)
            suffix = pathFile.suffix.lower()
            cat, success = getCategory(suffix)
            # if success:
            # # for any category:
            newName = normalize(pathFile.stem)

            # prepare target folder for category
            targetDir = Path(root + "/" + cat)

            if not targetDir.exists():
                targetDir.mkdir()

            targetFile = Path(root + "/" + cat + "/" + newName + suffix)
            if targetFile.exists():
                targetFile = targetFile.with_name(f"{targetFile.stem}-{uuid.uuid4()}{suffix}")

            #move-copy file to destination category-directory in separated Thread:
            #pathFile.replace(targetFile)
            executor.submit(job_copy_file, str(pathFile.absolute()), str(targetFile.absolute()), cat, suffix)

            if cat == "archives":
                #unpack file in separated Thread
                executor.submit(job_unpack_archive, str(targetFile.absolute()), root + "/" + cat + "/" + targetFile.stem)

    #*********************************
    for i, dirName in enumerate(folders):
        parse_directory(root, absPath + dirName)

#############################################################
def allStatistic(root: str):
    global CATEGORIES
    cat_files_all = dict()

    # try to traverse each directory-category:
    for cat, exts in CATEGORIES.items():
        dirCat = Path(root + "/" + cat)

        if dirCat.exists():
            ext = set()                     # known extentions
            uext = set()                    # unknown extentions
            for item in dirCat.iterdir():
                if(item.is_file()):
                    print(f"[{cat}]: {item.name}")
                    cat_files_all[cat] = cat_files_all.get(cat, 0) + 1

                    if item.suffix in CATEGORIES[cat]:
                        ext.add(item.suffix)
                    else:
                        uext.add(item.suffix)
            
            # category [others] has empty extentions dictionary
            if len(CATEGORIES[cat]) > 0:    # check, if category is any category, except [others]
                if len(ext)>0: print(f"[*{cat}*].extentions: {ext}")
            else:                           # [others] category
                if len(uext)>0: print(f"[*{cat}*].extentions: {uext}")

    if cat_files_all: print("----------------------\n", cat_files_all)

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

    moveStatistic()

    return "Ok"
###############################################################
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    print(main())
