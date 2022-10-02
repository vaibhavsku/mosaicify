from functools import lru_cache
from math import ceil
import cv2 as cv
import numpy as np
import os
import  pickle
import faiss
import hashlib
import multiprocessing
import imghdr
import copy
import shutil

valid_img_formats = ['bmp', 'jpeg', 'png', 'webp', 'rast', 'exr', 'pbm', 'pgm', 'ppm', 'tiff']

def generateMD5(img_path):
    md5sum = hashlib.md5()
    buffer_size = 4096
    with open(img_path, 'rb') as fileobj:
        for chunk in iter(lambda: fileobj.read(buffer_size), b''):
            md5sum.update(chunk)
    return md5sum.hexdigest()

def tile_and_vectorize_image(img_path, tile_w, tile_h):
    img = cv.imread(img_path)
    img_res = cv.resize(img, (tile_w, tile_h), cv.INTER_AREA)
    img_vec = img_res.flatten().astype(np.float32)
    return (img_res, img_vec)

def tiles_and_vectors(img_paths, tile_w, tile_h, conn):
    tiles = []
    vectors = []
    checklist = []
    for i in img_paths:
        x, y = tile_and_vectorize_image(i, tile_w, tile_h)
        tiles.append(x)
        vectors.append(y)
        checklist.append(generateMD5(i))
    conn.send((tiles, vectors, checklist)) 
    conn.close()



def return_image_paths(img_dir, numberOfChunks, checklist):
    global valid_img_formats
    img_paths = []
    img_sources = os.listdir(img_dir)
    paths = []
    chunks = []
    for i in img_sources:
        x = imghdr.what(img_dir+'/'+i)
        if x in valid_img_formats:
            md5_x = generateMD5(img_dir+'/'+i)
            if md5_x not in checklist:
                img_paths.append(img_dir+'/'+i)
            else:
                print(f'Image already processed. Omiting. Directory : {img_dir} Filename : {i}')
        else:
            print(f'Invalid image. Omitting. Directory : {img_dir} Filename : {i}')
    chunkSize = ceil(len(img_paths)/numberOfChunks)
    for j in img_paths:
        chunks.append(j)
        if len(chunks) == chunkSize:
            x = copy.deepcopy(chunks)
            paths.append(x)
            chunks.clear()
    if len(chunks) > 0:
        x = copy.deepcopy(chunks)
        paths.append(chunks)
    return paths

def vectorize_and_save(tile_w, tile_h, img_paths):
    pipes = []
    processes = []
    recieved = []

    r = len(img_paths)

    for i in range(0, r):
        x, y = multiprocessing.Pipe()
        pipes.append((x, y))
    for i in range(0, r):
        p = multiprocessing.Process(target=tiles_and_vectors, args=(img_paths[i], tile_w, tile_h, pipes[i][1]))
        processes.append(p)
        processes[i].start()
    for i in range(0, r):
        recieved.append(pipes[i][0].recv())
    for i in range(0, r):
        processes[i].join()

    return recieved


def generateDatabase(tile_w, tile_h):
    img_path = os.getcwd()+'/'+'images'
    tile_db_path = os.getcwd()+'/'+'db_cache'+'/'+str(tile_w)+'_'+str(tile_h)+'.pkl'
    checklist_path = os.getcwd()+'/'+'checklists'+'/'+str(tile_w)+'_'+str(tile_h)+'.pkl'
    index_path = os.getcwd()+'/'+'indexes'+'/'+str(tile_w)+'_'+str(tile_h)+'.index'
    available_tiles_path = os.getcwd()+'/'+'config.pkl'

    if(os.path.isdir(img_path)==False):
        os.makedirs(img_path)
    if(os.path.isdir(os.getcwd()+'/'+'db_cache')==False):
        os.makedirs(os.getcwd()+'/'+'db_cache')
    if(os.path.isdir(os.getcwd()+'/'+'checklists')==False):
        os.makedirs(os.getcwd()+'/'+'checklists')
    if(os.path.isdir(os.getcwd()+'/'+'indexes')==False):
        os.makedirs(os.getcwd()+'/'+'indexes')

    if(os.path.isfile(tile_db_path)==False):
        with open(tile_db_path, 'wb') as outfile:
            pickle.dump([], outfile, pickle.HIGHEST_PROTOCOL)
    if(os.path.isfile(checklist_path)==False):
        with open(checklist_path, 'wb') as outfile:
            pickle.dump([], outfile, pickle.HIGHEST_PROTOCOL)
    if(os.path.isfile(available_tiles_path)==False):
        with open(available_tiles_path, 'wb') as outfile:
            pickle.dump([], outfile, pickle.HIGHEST_PROTOCOL)
    if(os.path.isfile(index_path)==False):
        index = faiss.IndexFlatL2(tile_w*tile_h*3)
        faiss.write_index(index, index_path)

    with open(checklist_path, 'rb') as infile:
        checklist = pickle.load(infile)
    img_paths = return_image_paths(img_path, 4, checklist)
    if len(img_paths) > 0:
        with open(tile_db_path, 'rb') as infile:
            tiles = pickle.load(infile)
        vectors = []
        index = faiss.read_index(index_path)
        p_data = vectorize_and_save(tile_w, tile_h, img_paths)
        for p in p_data:
            for c in p[2]:
                checklist.append(c)
            for v in p[1]:
                vectors.append(v)
            for t in p[0]:
                tiles.append(t)
        index.add(np.asarray(vectors))
        with open(checklist_path, 'wb') as outfile:
            pickle.dump(checklist, outfile, pickle.HIGHEST_PROTOCOL)
        with open(tile_db_path, 'wb') as outfile:
            pickle.dump(tiles, outfile, pickle.HIGHEST_PROTOCOL)
        faiss.write_index(index, index_path)
        with open(available_tiles_path, 'rb') as infile:
            available_tiles = pickle.load(infile)
        if (tile_w, tile_h) not in available_tiles:
            available_tiles.append((tile_w, tile_h))
        with open(available_tiles_path, 'wb') as outfile:
            pickle.dump(available_tiles, outfile, pickle.HIGHEST_PROTOCOL)

def fillMatrix(output_image, input_image, tile_w, tile_h, x_t, y_t):
    y_start = y_t
    y_end = y_t + tile_h
    x_start = x_t
    x_end = x_t + tile_w
    output_image[y_start:y_end, x_start:x_end] = input_image[0:tile_h, 0:tile_w]

def getTile(input_image, tile_w, tile_h, x_t, y_t):
    y_start = y_t
    y_end = y_t + tile_h
    x_start = x_t
    x_end = x_t + tile_w
    return input_image[y_start:y_end, x_start:x_end]
        
def generateMosiac(img_source, tile_w, tile_h):
    img = cv.imread(img_source)
    img_h, img_w, _ = img.shape
    db_path = os.getcwd()+'/'+'db_cache'+'/'+str(tile_w)+'_'+str(tile_h)+'.pkl'
    index_path = os.getcwd()+'/'+'indexes'+'/'+str(tile_w)+'_'+str(tile_h)+'.index'
    if (img_w*img_h)%(tile_w*tile_h) != 0:
        print('The input image cannot be tiled into the given tile dimensions.')
    else:
        with open(db_path, 'rb') as infile:
            db = pickle.load(infile)
        index = faiss.read_index(index_path)
        search_vector = []
        res_img = np.zeros((img_h, img_w, 3), np.uint8)
        for o_y in range(0, img_h, tile_h):
            for o_x in range(0, img_w, tile_w):
                search_vector.append(getTile(img, tile_w, tile_h, o_x, o_y).flatten().astype(np.float32))
        _, results = index.search(np.asarray(search_vector), 1)
        curr_pos = 0
        for o_y in range(0, img_h, tile_h):
            for o_x in range(0, img_w, tile_w):
                fillMatrix(res_img, db[results[curr_pos][0]], tile_w, tile_h, o_x, o_y)
                curr_pos = curr_pos+1
        return res_img

def saveMosiac(img_dest, mosaic_matrix):
    cv.imwrite(img_dest,mosaic_matrix)


def add_images(img_src):
    for i in img_src:
        shutil.copy(i, os.getcwd()+'/images')

def delete_state():
    shutil.rmtree(os.getcwd()+'/images')
    shutil.rmtree(os.getcwd()+'/checklists')
    shutil.rmtree(os.getcwd()+'/db_cache')
    shutil.rmtree(os.getcwd()+'/indexes')
    os.remove(os.getcwd()+'/config.pkl')


    
# if __name__ == '__main__':
#     tiles = []
#     vectors = []
#     checklist = []
#     img_paths = return_image_paths(os.getcwd()+'/'+'images', 4, checklist)
#     pipes = []
#     processes = []
#     recieved = []
#     #print(img_paths)
#     # parent_conn1, child_conn1 = multiprocessing.Pipe()
#     # parent_conn2, child_conn2 = multiprocessing.Pipe()
#     # parent_conn3, child_conn3 = multiprocessing.Pipe()
#     # parent_conn4, child_conn4 = multiprocessing.Pipe()

#     for i in range(0, 4):
#         x, y = multiprocessing.Pipe()
#         pipes.append((x, y))
#     for i in range(0, 4):
#         p = multiprocessing.Process(target=tiles_and_vectors, args=(img_paths[i], 10, 10, pipes[i][1]))
#         processes.append(p)
#         processes[i].start()
#     for i in range(0, 4):
#         recieved.append(pipes[i][0].recv())
#     for i in range(0, 4):
#         processes[i].join()

#     for r in recieved:
#         for c in r[2]:
#             checklist.append(c)
#         for v in r[1]:
#             vectors.append(v)
#         for t in r[0]:
#             tiles.append(t)

#     print(checklist)

    
#     p2 = multiprocessing.Process(target=tiles_and_vectors, args=(img_paths, 4, 7, 10, 10, child_conn2))
#     p3 = multiprocessing.Process(target=tiles_and_vectors, args=(img_paths, 8, 11, 10, 10, child_conn3))
#     p4 = multiprocessing.Process(target=tiles_and_vectors, args=(img_paths, 12, 13, 10, 10, child_conn4))
#     p1.start()
#     p2.start()
#     p3.start()
#     p4.start()
#     recv1 = parent_conn1.recv()
#     recv2 = parent_conn2.recv()
#     recv3 = parent_conn3.recv()
#     recv4 = parent_conn4.recv()
#     p1.join()
#     p2.join()
#     p3.join()
#     p4.join()

#     generateDatabase(30, 40)

#     mm = generateMosiac(os.getcwd()+'/'+'0123.jpeg', 30, 40)
#     saveMosiac(os.getcwd()+'/'+'mosiac4.png', mm)







