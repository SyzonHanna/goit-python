from distutils import extension
import re
import sys
import shutil
import os
from pathlib import Path

# Скрипт должен проходить по указанной во время вызова папке и сортироват все файлы по группам 
# new folders for sorted files
images = ['jpeg','png','jpg','svg']
video = ['avi','mp4','mov','mkv']
documents = ['doc','docx','txt','pdf','xlsx','pptx']
audio = ['mp3','ogg','wav','amr']
archives = ['zip','gz','tar'] 

# В результатах работы должны быть:
# список файлов в каждой категории (музыка, видео, фото и пр.)
files_images=[]
files_video=[]
files_documents=[]
files_audio=[]
files_archives=[]
unknown_files=[]

# перечень всех известных скрипту расширений, которые встречаются в целевой папке.
# перечень всех расширений, которые скрипту неизвестны.
known_ext=set()
unknown_ext=set()


categories = ['images','video','documents','audio','archives']
categories_list={'images':[files_images, images],'video':[files_video, video],'documents': [files_documents, documents],'audio': [files_audio, audio],'archives': [files_archives, archives]}


# все файлы и папки нужно переименовать, удалив из названия все потенциально приводящие к проблемам символы
# функция normalize
def normalize(unnormalize_name):
    symbols_dictionary = ('абвгґдеєжзиіїйклмнопрстуфхцчшщюяыэёАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЮЯЫЭЁЪЬъь', (*(u'abvhgde'), 'ye', 'zh', *(u'zyi'), 'yi', *(u'yklmnoprstuf'), 'kh', 'ts', 'ch', 'sh', 'shch', 'yu', 'ya', 'y', 'ye', 'yo', *(u'ABVHGDE'), 'YE', 'ZH', *(u'ZYI'), 'YI', *(u'YKLMNOPRSTUF'), 'KH', 'TS', 'CH', 'SH', 'SHCH', 'YU', 'YA', 'Y', 'YE', 'YO', *(u'_' * 4)))  
    map_cyr_to_latin = {ord(src): dest for src, dest in zip(*symbols_dictionary)}
    normalize_name = unnormalize_name.translate(map_cyr_to_latin)
    result_sentence = re.sub(r'\W', "_", normalize_name)
    return result_sentence


#Создаем папки для сортировки файлов
def create_category_dirs(path: Path):
    for category in categories:
        if not os.path.exists(path+'\\'+category):
            os.mkdir(path+'\\'+category)
            

# Сортировка содержимого папки
def sort_directory(path: Path):   
    for element in Path(path).iterdir():
        if element.is_dir():
            if element.name in categories:
                continue
            # удаляем папку, если она пустая
            elif len(os.listdir(element)) == 0 and element.name not in categories:
                shutil.rmtree(element)
            else:
                # Переименовываем папку, убирая с названия кирилицу
                new_name = normalize(element.name)
                new_file = Path(f'{element.parent}/{new_name}')
                os.rename(element, new_file)
                sort_directory(new_file)
        elif element.is_file():
            sort_file(element)


# Функция переименования файла 
def file_rename(path: Path, new_name, extension):
    path.rename(Path(path.parent, new_name + extension))
    new_file = Path(new_name + extension)
    return new_file


# переименовываем и переносим файл в соответственную папку
# создаем списки с содержимым папок и списки с известными\не известными расширениями
def sort_file(file):
    extension = file.suffix
    name = file.stem
    new_name = normalize(name)
    new_file = file_rename(file, new_name, extension)

    nmbr_of_attempts=0
    for category, dest in categories_list.items():
        nmbr_of_attempts+=1
        if extension.replace(".","").lower() in dest[1]:
            categories_list.get(category)[0].append(new_name + extension)
            known_ext.add(extension)
            shutil.move(f'{file.parent}/{new_file}', f'{p}/{category}/{new_file}')
            nmbr_of_attempts=6              
            if category=='archives':
                shutil.unpack_archive(f'{p}/{category}/{new_file}', f'{p}/{category}/{new_name}')
                os.remove(f'{p}/{category}/{new_file}')
        elif nmbr_of_attempts==len(categories_list):
            unknown_files.append(name + extension) 
            unknown_ext.add(extension)


# принимаем и проверяем аргументы
if __name__ == '__main__':
    #try:
        #p = Path(sys.argv[1])
    #except:
        #print(f'{sys.argv[1]} does not exist or is not a directory')
    p = sys.argv[1] #p=os.getcwd()   

    if not os.path.isdir(p):#len(sys.argv) != 2:
        #print ("Alarm: wrong arguments! It should be: program_name_to_sort folder_to_sort")
        print(f'{sys.argv[1]} does not exist or is not a directory')
    else:
        if os.path.isdir(p):
            create_category_dirs(p)
            sort_directory(p)
            try:
                print(Path(p).glob('**/*'))
                for p in Path(p).glob('**/*'):
                    if p.is_dir() and len(list(p.iterdir())) == 0 and p.name not in categories:
                        os.removedirs(p)
            except:
                print(f'директория {p} уже удалена')

            print(f'Images: {files_images}\nVideo: {files_video}\nDocuments: {files_documents}\nAudio: {files_audio}\nArchives: {files_archives}\nKnown extensions: {known_ext}\nFiles with Unknown extensions: {unknown_files}\nUnknown extensions: {unknown_ext}')
        else:
            print(f'{sys.argv[1]} does not exist or is not a directory')

