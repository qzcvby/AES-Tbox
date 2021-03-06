import copy
import hashlib
import os
import time

import numpy as np

# Sç 16 * 16
S_box = [0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
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
         0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16]
# éSç 16 * 16
Inv_S_box = [0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
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
             0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D]
# 11ä¸Şċ­ċŻé?ïĵċ½˘ċĵä¸şbyte[][][]ïĵĉŻä¸ä¸Şċ­ċŻé?çħ4ä¸Şċ­(4ċ­è)çğĉïĵä¸èĦä¸şä¸ä¸Şċ­
k = [[[] for b in range(4)] for a in range(11)]


def key_expansion(key):
    w = [[] for i in range(44)]
    RC = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
    # ċ°ċnkä¸Şċ­ċĦĞċ?w
    for i in range(4):
        w[i].append(key[(i * 4) + 0])
        w[i].append(key[(i * 4) + 1])
        w[i].append(key[(i * 4) + 2])
        w[i].append(key[(i * 4) + 3])
    for i in range(4, 44):
        # ċĤĉiĉŻnkçċĉ°ïĵwi = wi-nk â g(wi-1)ïĵgä¸şċ?ŞçŻċ·Ĥç§ğ1ċ­èâċ­èäğ£ĉżâRcon
        if i % 4 == 0:
            # ċĵĉRconċ³çĴĴä¸ä¸Şċ­èċĵĉRC
            # print(type(w[i][0]))
            x = i / 4 - 1
            w[i].append(w[i - 4][0] ^ S_box[w[i - 1][1] & 0xff] ^ RC[int(x)])
            w[i].append(w[i - 4][1] ^ S_box[w[i - 1][2] & 0xff])
            w[i].append(w[i - 4][2] ^ S_box[w[i - 1][3] & 0xff])
            w[i].append(w[i - 4][3] ^ S_box[w[i - 1][0] & 0xff])
        # ċĥäğwi = wi-nk â wi-1
        else:
            for j in range(4):
                w[i].append(w[i - 4][j] ^ w[i - 1][j])
    for i in range(11):
        for j in range(4):
            k[i][j] = (w[i * 4 + j])


def encrypt(plain):
    """AESċ ċŻ"""
    # 16ċ­èċŻĉ
    cipher = bytearray(16)
    # çĥĉçİéµ
    state = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            state[i].append(plain[j + 4 * i])
    # è½?ċŻé?ċ 
    add_round_key(state, k[0])
    for i in range(1, 10):
        # ċ­èäğ£ĉż
        sub_bytes(state)
        # èĦä½ç§ğ
        state = shift_rows(state)
        # ċĉ··ĉ·
        state = mix_columns(state)
        # è½?ċŻé?ċ 
        add_round_key(state, k[i])
    # ċ­èäğ£ĉż
    sub_bytes(state)
    # èĦä½ç§ğ
    state = shift_rows(state)
    # è½?ċŻé?ċ 
    add_round_key(state, k[10])
    for i in range(4):
        cipher[i * 4: i * 4 + 4] = copy.deepcopy(state[i])
    return cipher


def decrypt(cipher):
    # 16ċ­èĉĉ
    plain = bytearray(16)
    # çĥĉçİéµ
    state = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            state[i].append(cipher[j + 4 * i])
    # è½?ċŻé?ċ 
    add_round_key(state, k[10])
    # éċèĦç§ğä½
    state = inv_shift_rows(state)
    # éċċ­èäğ£ĉż
    inv_sub_bytes(state)
    for i in reversed(range(1, 10)):
        # è½?ċŻé?ċ 
        add_round_key(state, k[i])
        # éċċĉ··ĉ·
        state = inv_mix_columns(state)
        # éċèĦç§ğä½
        state = inv_shift_rows(state)
        # éċċ­èäğ£ĉż
        inv_sub_bytes(state)
    # è½?ċŻé?ċ 
    add_round_key(state, k[0])
    for i in range(4):
        plain[i * 4: i * 4 + 4] = copy.deepcopy(state[i])
    return plain


def encrypt_file(plain_file, cipher_file):
    file_in = open(plain_file, 'rb')
    # temp = open(cipher_file, 'wb')
    # temp.close()  # ĉ¸çİş
    file_out = open(cipher_file, 'wb')
    # ĉŻä¸çğçĉĉċċŻĉ
    length = 16
    plain = np.zeros(16)
    # èŻğċïĵċ ċŻ
    size = os.path.getsize(plain_file)
    while size > 0:
        plain = file_in.read(length)
        if len(plain) != 16:
            for i in range(16 - len(plain)):
                plain += bytes(1)
        cipher = encrypt(plain)
        file_out.write(cipher)
        size -= length
    file_in.close()
    file_out.close()


def decrypt_file(cipher_file, plain_file):
    file_in = open(cipher_file, 'rb')
    file_out = open(plain_file, 'wb')
    length = 16
    size = os.path.getsize(cipher_file)
    while size > 0:
        cipher = file_in.read(length)
        plain = decrypt(cipher)
        file_out.write(plain)
        size -= length
    file_in.close()
    file_out.close()


def add_round_key(state, key):
    """è½?ċŻé?ċ """
    for i in range(4):
        for j in range(4):
            # print(type(state[i][j]))
            # print(type(key[i][j]))
            state[i][j] ^= key[i][j]


def sub_bytes(state):
    """ċ­èäğ£ĉż"""
    for i in range(4):
        for j in range(4):
            state[i][j] = S_box[state[i][j] & 0xff]


def inv_sub_bytes(state):
    """éċ­èäğ£ĉż"""
    for i in range(4):
        for j in range(4):
            state[i][j] = Inv_S_box[state[i][j] & 0xff]


def shift_rows(state):
    """èĦç§ğä½, çħäşçĥĉçİéµĉŻĉèĦċĦĞċç, ĉäğ?èżéċ?éä¸ĉŻâċç§ğä½â, ċŞĉŻäżçäşċĉıĉ³ċ"""
    result = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            result[j].append(state[(j + i) % 4][i])
    return result


def inv_shift_rows(state):
    """éèĦç§ğä½, çħäşçĥĉçİéµĉŻĉèĦċĦĞċç, ĉäğ?èżéċ?éä¸ĉŻâéċç§ğä½â, ċŞĉŻäżçäşċĉıĉ³ċ"""
    result = [[] for i in range(4)]
    for i in range(4):
        for j in range(4):
            result[j].append(state[(j - i + 4) % 4][i])
    return result


def mix_columns(state):
    """ċĉ··ĉ·ïĵçħäşçĥĉçİéµĉŻĉèĦċĦĞċçïĵĉäğ?èżéċ?éä¸ĉŻâèĦĉ··ĉ·âïĵċŞĉŻäżçäşċĉıĉ³ċ"""
    # ċĉ··ĉ·ċŻäğ?èĦ¨ç¤şä¸şä¸äğ?ä¸çİéµç¸äı
    matrix = [[2, 1, 1, 3], [3, 2, 1, 1], [1, 3, 2, 1], [1, 1, 3, 2]]
    # 4*4çİéµç¸äı
    result = [[] for j in range(4)]
    for i in range(4):
        for j in range(4):
            x = 0
            for k in range(4):
                x ^= multiply(state[i][k], matrix[k][j])
            result[i].append(x)
    return result


def inv_mix_columns(state):
    """éċĉ··ĉ·ïĵçħäşçĥĉçİéµĉŻĉèĦċĦĞċçïĵĉäğ?èżéċ?éä¸ĉŻâéèĦĉ··ĉ·âïĵċŞĉŻäżçäşċĉıĉ³ċ"""
    # éċĉ··ĉ·ċŻäğ?èĦ¨ç¤şä¸şä¸äğ?ä¸çİéµç¸äı
    matrix = [[0xE, 0x9, 0xD, 0xB], [0xB, 0xE, 0x9, 0xD], [0xD, 0xB, 0xE, 0x9], [0x9, 0xD, 0xB, 0xE]]
    result = [[] for j in range(4)]
    # 4*4çİéµç¸äı
    for i in range(4):
        for j in range(4):
            x = 0
            for k in range(4):
                x ^= multiply(state[i][k], matrix[k][j])
            result[i].append(x)
    return result


def multiply(a, b):
    """GF(2^8)ä¸çäıĉ³"""
    tmp = a
    result = 0
    # b0ä¸ş1ĉĥïĵçğĉèĤçĉççĴĴä¸ä¸Şĉ°ä¸şa*0x01ïĵċĤċä¸ş0ïĵċĵĉ0ä¸şĉĴèşĞïĵ
    if (b & 1) == 1:
        result = a
    # ç?ċşaäı0b10, 0b100......
    for i in range(8):
        # ĉéĞä½ä¸ş1ĉĥċ·Ĥç§ğ1ä½ċċĵĉ11011
        if tmp < 0:
            tmp = (tmp << 1) ^ 27
        else:
            tmp = tmp << 1
        b = (b & 0xff) >> 1
        # biä¸ş1ïĵĉ?èżċĵĉbi*a^i
        if (b & 1) == 1:
            result ^= tmp
    return result


def get_md5(file):
    md5 = None
    if os.path.isfile(file):
        f = open(file, 'rb')
        md5_obj = hashlib.md5()
        md5_obj.update(f.read())
        hash_code = md5_obj.hexdigest()
        f.close()
        md5 = str(hash_code).lower()
    return md5


if __name__ == '__main__':
    if __name__ == '__main__':
        print("Without T-box")
        key = [0x0f, 0x15, 0x71, 0xc9, 0x47, 0xd9, 0xe8, 0x59, 0x0c, 0xb7, 0xad,
               0xd6, 0xaf, 0x7f, 0x67, 0x98]
        key_expansion(key)
        md51 = get_md5('plain.txt')
        time_start_1 = time.time()
        encrypt_file('plain.txt', 'cipher.txt')
        time_end_1 = time.time()
        print("encrypt timeïĵ %f s" % (time_end_1 - time_start_1))

        time_start_2 = time.time()
        decrypt_file('cipher.txt', 'plain.txt')
        time_end_2 = time.time()
        print("decrypt timeïĵ %f s" % (time_end_2 - time_start_2))
        md52 = get_md5('plain.txt')
        print('===========================================================')
        if md51 == md52:
            print("The md5 is same")
        else:
            print('The md5 is not same')