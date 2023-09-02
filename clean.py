# from task04_path

import re
import os
import shutil
import sys
import uuid
from pathlib import Path

##########################################################
img_f = {'.jpeg', '.png', '.jpg', '.svg', ".bmp", ".ico"}
mov_f = {'.avi', '.mp4', '.mov', '.mkv', ".webm", ".wmv", ".flv"}
doc_f = {'.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx', ".ini", ".cmd", ".ppt", ".xml", ".msg", ".cpp", ".hpp", ".py"}
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
def getCategory(pathFile):              # (string fileName)
    for cat, exts in CATEGORIES.items():
        if pathFile.suffix.lower() in exts:
            return cat, True            #(string, Bool)
    return "others", False               #(string, Bool)

###########################################################
def normalize(name):
    rename = name.translate(TRANS)
    rename = re.sub(r'[^a-zA-Z0-9 -]', "_", rename)
    return rename
###########################################################
def parse_folder(root, ipath = None):
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
            else:
                folders.append(i.name)
                empties = False
        
        elif i.is_file():
            pathFile = Path(absPath + i.name)
            cat, success = getCategory(pathFile)  #(string, Bool)
            # if success:
            # # for any category:
            newName = normalize(pathFile.stem)
            #print(newName)

            # prepare target folder for category
            targetDir = Path(root + "/" + cat)
            #print(targetDir.absolute())
            if not targetDir.exists():
                targetDir.mkdir()

            targetFile = Path(root + "/" + cat + "/" + newName + pathFile.suffix)
            if not targetFile.exists():
                pathFile.replace(targetFile)
                #shutil.copyfile(str(pathFile.absolute()), str(targetFile.absolute()))
            else:
                targetFile = targetFile.with_name(f"{targetFile.stem}-{uuid.uuid4()}{targetFile.suffix}")
                pathFile.replace(targetFile)
                #shutil.copyfile(str(pathFile.absolute()), str(targetFile.absolute()))

            if cat == "archives":
                shutil.unpack_archive(str(targetFile.absolute()), root + "/" + cat + "/" + targetFile.stem)
                        
    #*********************************
    # remove empty directories
    for i, dirName in enumerate(folders):
        if parse_folder(root, absPath + dirName) == True:
            # remove sub-directory if empty is OK
            rmDir = Path(absPath + dirName)
            rmDir.rmdir()

    empties = True
    for iter in path.iterdir():
        if iter.is_file() or iter.is_dir():
            # return empty-flag that allow to delete
            empties = False
            break

    return empties

#############################################################
def printStatistic(root: str):
    global CATEGORIES
    cat_amount = dict() # cat_amount[category] = files-count

    # try to traverse each directory-category:
    for cat, exts in CATEGORIES.items():
        dirCat = Path(root + "/" + cat)

        if dirCat.exists():
            ext = set()     # known extentions
            uext = set()    # unknown extentions
            for item in dirCat.iterdir():
                if(item.is_file()):
                    print("[{}]: {}".format(cat, item.name))
                    cat_amount[cat] = cat_amount.get(cat, 0) + 1

                    if item.suffix in CATEGORIES[cat]:
                        ext.add(item.suffix)
                    else:
                        uext.add(item.suffix)
            
            # category [others] has empty extentions dictionary
            if len(CATEGORIES[cat]) > 0:    # check, if category is any category, except [others]
                print("[*{}*].extentions:".format(cat), ext)
            else:                           # [others] category
                print("[*{}*].extentions:".format(cat), uext)

    print("----------------------\n", cat_amount)

###############################################################
def main():
    root = "."
    if len(sys.argv) > 1:
        root = sys.argv[1]
    path = Path(root)

    if not path.exists():
        return f"Folder with path {root} dos`n exists."

    parse_folder(root)
    printStatistic(root)
    return "Ok"
###############################################################
if __name__ == "__main__":
    print(main())
