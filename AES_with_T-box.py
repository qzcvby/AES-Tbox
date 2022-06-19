import hashlib
import os.path
import time

import numpy as np

s_box = [
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
]

inv_s_box = [
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D,
]

t = [[[] for p in range(256)] for o in range(4)]
k = [[[] for b in range(4)] for a in range(11)]


def multiply(a, b):
    tmp = a
    result = 0
    if b & 1 == 1:
        result = a
    for i in range(1, 8):
        if tmp < 0:
            tmp = (tmp << 1) ^ 27
        else:
            tmp = tmp << 1
        b = (b & 0xff) >> 1
        if (b & 1) == 1:
            result ^= tmp
    return result


def keyExpansion(key_):
    w = [[] for j in range(44)]
    RC = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
    for i in range(4):
        w[i].append(key_[(i * 4) + 0])
        w[i].append(key_[(i * 4) + 1])
        w[i].append(key_[(i * 4) + 2])
        w[i].append(key_[(i * 4) + 3])
    for i in range(4, 44):
        if i % 4 == 0:
            x = i / 4 - 1
            w[i].append(w[i - 4][0] ^ s_box[w[i - 1][1] & 0xff] ^ RC[int(x)])
            w[i].append(w[i - 4][1] ^ s_box[w[i - 1][2] & 0xff])
            w[i].append(w[i - 4][2] ^ s_box[w[i - 1][3] & 0xff])
            w[i].append(w[i - 4][3] ^ s_box[w[i - 1][0] & 0xff])
        else:
            for j in range(4):
                w[i].append(w[i - 4][j] ^ w[i - 1][j])
    for i in range(11):
        for j in range(4):
            k[i][j] = (w[i * 4 + j])


def invMixColumns(state):
    matrix = [[0xE, 0x9, 0xD, 0xB], [0xB, 0xE, 0x9, 0xD], [0xD, 0xB, 0xE, 0x9], [0x9, 0xD, 0xB, 0xE]]
    result = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            x = 0
            for m in range(4):
                x ^= multiply(state[i][m], matrix[m][j])
            result[i].append(x)
    return result


def init(mode, key_, change_flag):
    keyExpansion(key_)
    if mode == "decrypt":
        for i in range(1, 10):
            k[i] = invMixColumns(k[i])
    if change_flag:
        if mode == "encrypt":
            matrix = [[2, 1, 1, 3], [3, 2, 1, 1], [1, 3, 2, 1], [1, 1, 3, 2]]
            for i in range(4):
                for j in range(256):
                    for m in range(4):
                        t[i][j].append(multiply(s_box[j], matrix[i][m]))
        if mode == "decrypt":
            matrix = [[0xE, 0x9, 0xD, 0xB], [0xB, 0xE, 0x9, 0xD], [0xD, 0xB, 0xE, 0x9],
                      [0x9, 0xD, 0xB, 0xE]]
            for i in range(4):
                for j in range(256):
                    for m in range(4):
                        if np.array(t).shape == (4, 256, 4):
                            t[i][j][m] = multiply(inv_s_box[j], matrix[i][m])
                        else:
                            t[i][j].append(multiply(inv_s_box[j], matrix[i][m]))


def encrypt(file_p, file_c):
    f_in = open(file_p, mode="rb")
    f_out = open(file_c, mode="wb")
    length = 16
    size = os.path.getsize(file_p)
    while size > 0:
        plain = f_in.read(length)
        if len(plain) != 16:
            for i in range(16 - len(plain)):
                plain += bytes(1)
        cipher = encrypt_text(plain)
        f_out.write(cipher)
        size -= length
    f_in.close()
    f_out.close()


def encrypt_text(plain):
    cipher = bytearray(16)
    state = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            state[i].append(plain[j + 4 * i])
    state = addRoundKey(state, k[0])
    for i in range(1, 10):
        state = roundFunction(state, k[i])
    state = subBytes(state)
    state = shiftRows(state)
    addRoundKey(state, k[10])
    for i in range(4):
        cipher[(i * 4) + 0] = state[i][0]
        cipher[(i * 4) + 1] = state[i][1]
        cipher[(i * 4) + 2] = state[i][2]
        cipher[(i * 4) + 3] = state[i][3]
    return cipher


def roundFunction(state, key_):
    result = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            result[i].append(t[0][state[i][0] & 0xff][j]
                             ^ t[1][state[(i + 1) % 4][1] & 0xff][j]
                             ^ t[2][state[(i + 2) % 4][2] & 0xff][j]
                             ^ t[3][state[(i + 3) % 4][3] & 0xff][j]
                             ^ key_[i][j])
    return result


def shiftRows(state):
    result = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            result[j].append(state[(j + i) % 4][i])
    return result


def subBytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = s_box[state[i][j] & 0xff]
    return state


def decrypt(file_c, file_p):
    f_in = open(file_c, mode="rb")
    f_out = open(file_p, mode="wb")
    length = 16
    size = os.path.getsize(file_c)
    while size > 0:
        cipher = f_in.read(length)
        plain = decrypt_text(cipher)
        f_out.write(plain)
        size -= length
    f_in.close()
    f_out.close()


def decrypt_text(plain):
    text = bytearray(16)
    state = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            state[i].append(plain[j + 4 * i])
    state = addRoundKey(state, k[10])
    for i in range(9, 0, -1):
        state = invRoundFunction(state, k[i])
    state = invSubBytes(state)
    state = invShiftRows(state)
    state = addRoundKey(state, k[0])
    for i in range(4):
        text[(i * 4) + 0] = state[i][0]
        text[(i * 4) + 1] = state[i][1]
        text[(i * 4) + 2] = state[i][2]
        text[(i * 4) + 3] = state[i][3]
    return text


def invShiftRows(state):
    result = [[] for i in range(4)]
    for i in range(4):
        for j in range(4):
            result[j].append(state[(j - i + 4) % 4][i])
    return result


def invSubBytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = inv_s_box[state[i][j] & 0xff]
    return state


def invRoundFunction(state, k_):
    result = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            result[i].append(t[0][state[i][0] & 0xff][j]
                             ^ t[1][state[(i + 3) % 4][1] & 0xff][j]
                             ^ t[2][state[(i + 2) % 4][2] & 0xff][j]
                             ^ t[3][state[(i + 1) % 4][3] & 0xff][j]
                             ^ k_[i][j])
    return result


def addRoundKey(state, k_):
    for i in range(4):
        for j in range(4):
            state[i][j] ^= k_[i][j]
    return state


def get_md5_01(file_path):
    md5 = None
    if os.path.isfile(file_path):
        f = open(file_path, 'rb')
        md5_obj = hashlib.md5()
        md5_obj.update(f.read())
        hash_code = md5_obj.hexdigest()
        f.close()
        md5 = str(hash_code).lower()
    return md5


if __name__ == '__main__':
    key = [0x0f, 0x15, 0x71, 0xc9, 0x47, 0xd9, 0xe8, 0x59, 0x0c, 0xb7, 0xad,
           0xd6, 0xaf, 0x7f, 0x67, 0x98]
    print("With T-box")
    md5_1 = get_md5_01("plain.txt")
    init("encrypt", key, True)
    time_start_1 = time.time()
    encrypt("plain.txt", "cipher.txt")
    time_end_1 = time.time()
    print("encrypt time： %f s" % (time_end_1 - time_start_1))
    time_start_2 = time.time()
    init("decrypt", key, True)
    time_end_2 = time.time()
    print("decrypt time： %f s" % (time_end_2 - time_start_2))
    decrypt("cipher.txt", "plain.txt")
    md5_2 = get_md5_01("plain.txt")
    if md5_1 == md5_2:
        print("The md5 is same")
    else:
        print("Not same")