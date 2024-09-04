import heapq
import os
import argparse
import hashlib
from queue import Queue
import math
import heapq
import os
import argparse
import hashlib
from queue import Queue


def CLI(command=None, in_file_path=None, code_file_path=None, decode_file_path=None):
    if command is None:
        import argparse
        parser = argparse.ArgumentParser(description='CLI_Huffman_LZ78_United')
        parser.add_argument('command', choices=['help', 'encode', 'decode'],
                            help='Choose command: help or encode or decode')
        args = parser.parse_args()
        command = args.command

    if command == 'help':
        print('CLI_Huffman_LZ78_United\n\nUsage: python script.py <command>\n\n'
              'Commands:\n '
              'help         Display help information\n  '
              'encode       Encode a file using Huffman_LZ78_United coding\n  '
              'decode       Decode a file encoded with Huffman_LZ78_United coding\n\n'
              'Example:\n  python script.py')
    elif command == 'encode':
        if in_file_path is None:
            in_file_path = input("请输入要编码的文件路径: ")
        if not os.path.exists(in_file_path):
            print("Error: 输入文件不存在")
            return
        if code_file_path is None:
            code_file_path = input("请输入编码文件存放路径: ")
        # 打开一个新文件，如果文件不存在，则会被创建；如果文件已存在，则会被覆盖
        with open('temp.bin', 'w') as f:
            f.write("")
        Huffman_encode(in_file_path, 'temp.bin')
        LZ78_encode('temp.bin', code_file_path)
        os.remove('temp.bin')
        test1(in_file_path, code_file_path)
    elif command == 'decode':
        if code_file_path is None:
            code_file_path = input("请输入要解码的文件路径: ")
        if not os.path.exists(code_file_path):
            print("Error: 编码文件不存在")
            return
        if decode_file_path is None:
            decode_file_path = input("请输入解码文件存放路径: ")
        LZ78_decode(code_file_path, 'temp.bin')
        Huffman_decode('temp.bin', decode_file_path)
        os.remove('temp.bin')
        test2(code_file_path, decode_file_path)
    else:
        print('Unknown command')


class Node:
    def __init__(self, num, cnt):
        self.num = num
        self.cnt = cnt
        self.son = [0, 0]

    def __lt__(self, other):
        return self.cnt < other.cnt


tree = [Node(i, 0) for i in range(5005)]
tot = 256
root = 0
code = ['' for _ in range(300)]
q = []


def init():
    global tot
    tot = 256
    for i in range(1, 257):
        tree[i].num = i


def dfs(x, deep, code_num):
    if tree[x].son[0] == 0 and tree[x].son[1] == 0:
        for j in range(deep):
            code[x] = str((code_num >> j) & 1) + code[x]
        return
    dfs(tree[x].son[0], deep + 1, (code_num << 1))
    dfs(tree[x].son[1], deep + 1, (code_num << 1) | 1)


# 建立Huffman编码树
def Huffman_tree(in_file_path, code_file_path):
    # 开始编码
    global root, tot
    init()
    with open(in_file_path, "rb") as IN:
        while True:
            c = IN.read(1)
            if not c:
                break
            tree[ord(c) + 1].cnt += 1
    for i in range(1, 257):
        if tree[i].cnt:
            heapq.heappush(q, tree[i])
    tot = 257
    while len(q) > 1:
        left_son = heapq.heappop(q)
        right_son = heapq.heappop(q)
        tree[tot].cnt = left_son.cnt + right_son.cnt
        tree[tot].num = tot
        tree[tot].son[0] = left_son.num
        tree[tot].son[1] = right_son.num
        heapq.heappush(q, tree[tot])
        tot += 1
    root = q[0].num
    if root <= 256:
        print("Error: 文件中只有一个字符，无法进行Huffman编码")
        return
    dfs(root, 0, 0)


def Huffman_encode(in_file_path, code_file_path):
    Huffman_tree(in_file_path, code_file_path)
    with open(in_file_path, "rb") as IN, open(code_file_path, "wb") as OUT:
        # 将扩展名in_file_extension存入编码文件中
        # 码树编码 BFS
        que = Queue()
        result = ""
        que.put(root)
        while not que.empty():
            x = que.get()
            if tree[x].son[0] == 0:
                result += '0'
                for j in range(7, -1, -1):
                    result += str(((x - 1) >> j) & 1)
            else:
                result += '1'
                que.put(tree[x].son[0])
                que.put(tree[x].son[1])

        # 实际编码
        while True:
            c = IN.read(1)
            if not c:
                break
            result = result + code[ord(c) + 1]
            # 如果结果的长度达到8位（一个字节），就将其转换为整数，并写入文件
        while len(result) >= 8:
            result_byte = result[:8]  # 取出前8位作为一个字节
            result = result[8:]  # 剩余部分
            result_int = int(result_byte, 2)  # 将二进制字符串转换为整数
            try:
                OUT.write(bytes([result_int]))
            except IOError:
                print("Error: 写入文件出错")  # 将整数转换为字节对象并写入文件

        # 如果结果的长度大于0但小于8位，补足为8位，并写入文件
        if len(result) > 0:
            result_byte = result.ljust(8, '0')  # 补足为8位
            num_zeros_added = max(0, 8 - (len(result) % 8))
            result_int = int(result_byte, 2)  # 将二进制字符串转换为整数
            try:
                OUT.write(bytes([result_int]))
                OUT.write(bytes([num_zeros_added]))
            except IOError:
                print("Error: 写入文件出错")
        else:
            try:
                OUT.write(bytes([0]))
            except IOError:
                print("Error: 写入文件出错")


def Huffman_decode(code_file_path, decode_file_path):
    with open(code_file_path, "rb") as IN, open(decode_file_path, "wb+") as OUT:
        # 将文件指针移动到文件末尾
        IN.seek(-1, 2)
        # 读取最后一个字节
        last_byte = IN.read(1)
        # 获取最后一个字节的数值
        last_byte_value = int.from_bytes(last_byte, byteorder='big')
        result1 = ""
        # 将文件指针移动到文件开头
        IN.seek(0)
        byte = IN.read(1)
        while byte:
            # 将字节转换为整数
            byte_int = int.from_bytes(byte, byteorder='big')
            # 将整数转换为8位的二进制字符串
            binary_str = format(byte_int, '08b')
            # 将二进制字符串添加到结果中
            result1 += binary_str
            byte = IN.read(1)
        num = len(result1) - last_byte_value - 8
        result2 = result1[:num]  # 带解码字符串
        # 建树

        root = 1
        now_num = 0
        cnt = 1
        num = 1
        pos = 0
        while cnt > 0:
            now_num += 1
            cnt -= 1
            if result2[pos] == '1':
                cnt += 2
                num += 1
                tree[now_num].son[0] = num
                num += 1
                tree[now_num].son[1] = num
            else:
                tree[now_num].son[0] = 0
                tree[now_num].son[1] = 0
                xx = 0
                for i in range(1, 9):
                    pos += 1
                    if result2[pos] == '1':
                        xx = xx * 2 + 1
                    else:
                        xx *= 2
                tree[now_num].num = xx + 1
            pos += 1

        # 解码
        p = root
        result2 = result2[pos:]
        for c in result2:
            if c == '0':
                p = tree[p].son[0]
            else:
                p = tree[p].son[1]
            if tree[p].son[0] == 0:
                try:
                    OUT.write((tree[p].num - 1).to_bytes(1, 'big'))
                except IOError:
                    print("Error: 写入文件出错")

                p = root


N = 6000006
seg = [""] * N
s_len = 0
id = [0] * N
r_id = [0] * N
seg_cnt = 0
char_id = [-1] * 300
char_v = [0] * 300
id_char = [''] * 300
char_cnt = 0
seg_map = {}
len1 = 0
len2 = 0


def find_seg(seg_s):
    if seg_s in seg_map:
        return seg_map[seg_s]
    return 0


def LZ78_encode(in_file_path, code_file_path):
    global s_len, seg_cnt, char_cnt, len1, len2
    with open(in_file_path, "rb") as IN:
        s = ""
        while True:
            c = IN.read(1)
            if not c:
                break
            byte_int = int.from_bytes(c, byteorder='big')
            s += chr(byte_int)
            char_v[byte_int] = 1
        s_len = len(s)
    for i in range(256):
        if char_v[i]:
            char_id[i] = char_cnt
            char_cnt += 1

    seg_s = ""
    pre_id = 0
    for i in range(s_len):
        seg_s += s[i]
        temp_id = find_seg(seg_s)
        if temp_id == 0 or i == s_len - 1:
            seg_cnt += 1
            seg[seg_cnt] = seg_s
            id[seg_cnt] = pre_id
            seg_map[seg_s] = seg_cnt
            r_id[seg_cnt] = char_id[ord(s[i])]
            seg_s = ""
            pre_id = 0
        else:
            pre_id = temp_id
    len1 = int(math.log2(seg_cnt - 1)) + 1
    len2 = int(math.log2(char_cnt - 1)) + 1
    result = bin(len1 - 1)[2:].zfill(5) + bin(len2 - 1)[2:].zfill(3)
    for i in range(256):
        result += '1' if char_v[i] else '0'
    for i in range(1, seg_cnt + 1):
        result += bin(id[i])[2:].zfill(len1)
        result += bin(r_id[i])[2:].zfill(len2)
    with open(code_file_path, "wb") as OUT:
        while len(result) >= 8:
            result_byte = result[:8]  # 取出前8位作为一个字节
            result = result[8:]  # 剩余部分
            result_int = int(result_byte, 2)  # 将二进制字符串转换为整数
            try:
                OUT.write(bytes([result_int]))  # 将整数转换为字节对象并写入文件
            except IOError:
                print("Error: 写入文件出错")

        if len(result) > 0:
            result_byte = result.ljust(8, '0')  # 补足为8位
            num_zeros_added = max(0, 8 - (len(result) % 8))
            result_int = int(result_byte, 2)  # 将二进制字符串转换为整数
            try:
                OUT.write(bytes([result_int]))  # 将整数转换为字节对象并写入文件
                OUT.write(bytes([num_zeros_added]))
            except IOError:
                print("Error: 写入文件出错")


        else:
            try:
                OUT.write(bytes([0]))
            except IOError:
                print("Error: 写入文件出错")


def LZ78_decode(code_file_path, decode_file_path):
    global len1, len2, seg_cnt, char_cnt
    with open(code_file_path, "rb") as IN:
        IN.seek(-1, 2)
        # 读取最后一个字节
        last_byte = IN.read(1)
        # 获取最后一个字节的数值
        last_byte_value = int.from_bytes(last_byte, byteorder='big')
        result1 = ""
        # 将文件指针移动到文件开头
        IN.seek(0)
        byte = IN.read(1)
        while byte:
            # 将字节转换为整数
            byte_int = int.from_bytes(byte, byteorder='big')
            # 将整数转换为8位的二进制字符串
            binary_str = format(byte_int, '08b')
            # 将二进制字符串添加到结果中
            result1 += binary_str
            byte = IN.read(1)
        num = len(result1) - last_byte_value - 8
        s = result1[:num]  # 带解码字符串
    pos = 0
    len1 = 0
    len2 = 0
    while pos <= 4:
        len1 = len1 * 2 + int(s[pos])
        pos += 1
    len1 += 1
    while pos <= 7:
        len2 = len2 * 2 + int(s[pos])
        pos += 1
    len2 += 1
    pos = 8
    for i in range(256):
        if s[pos] == '1':
            id_char[char_cnt] = chr(i)
            char_cnt += 1
        pos += 1
    result = ""
    while pos < len(s):
        seg_id = 0
        cr_id = 0
        for _ in range(len1):
            seg_id = seg_id * 2 + int(s[pos])
            pos += 1
        for _ in range(len2):
            cr_id = cr_id * 2 + int(s[pos])
            pos += 1
        if seg_id == 0:
            seg_cnt += 1
            seg[seg_cnt] = id_char[cr_id]
        else:
            seg_cnt += 1
            seg[seg_cnt] = seg[seg_id] + id_char[cr_id]
        result += seg[seg_cnt]
    with open(decode_file_path, "wb+") as OUT:
        for c in result:
            try:
                OUT.write(ord(c).to_bytes(1, 'big'))
            except IOError:
                print("Error: 写入文件出错")


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # 逐块读取文件，以节省内存
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def test1(in_file_path, code_file_path):
    # 编码前的文件大小
    original_size = os.path.getsize(in_file_path)
    original_sha256 = calculate_sha256(in_file_path)
    # 编码后的文件大小
    encoded_size = os.path.getsize(code_file_path)
    encode_sha256 = calculate_sha256(code_file_path)

    efficiency = ((original_size - encoded_size) * 100) / original_size

    # 输出美化的表格
    print("+-------------------------+-------------------------+-------------------------+---------------------+")
    print(f"| 编码前的文件大小       {str(original_size).rjust(70)} 字节 |")
    print(f"| 编码前的文件sha256值        {str(original_sha256).rjust(70)} |")
    print(f"| 编码后的文件大小       {str(encoded_size).rjust(70)} 字节 |")
    print(f"| 编码后的文件sha256值        {str(encode_sha256).rjust(70)} |")
    print(f"| 编码前后的大小差异     {str(encoded_size - original_size).rjust(70)} 字节 |")
    print(f"| 编码效率                  {str(efficiency).rjust(70)} % |")
    print("+-------------------------+-------------------------+-------------------------+---------------------+")


def test2(code_file_path, decode_file_path):
    # 编码前的文件大小
    encoded_size = os.path.getsize(code_file_path)
    encode_sha256 = calculate_sha256(code_file_path)
    # 编码后的文件大小
    decoded_size = os.path.getsize(decode_file_path)
    decoded_sha256 = calculate_sha256(decode_file_path)

    efficiency = ((decoded_size - encoded_size) * 100) / decoded_size

    print("+-------------------------+-------------------------+-------------------------+---------------------+")
    print(f"| 解码前的文件大小        {str(encoded_size).rjust(70)} 字节 |")
    print(f"| 解码前的文件sha256值         {str(encode_sha256).rjust(70)} |")
    print(f"| 解码后的文件大小        {str(decoded_size).rjust(70)} 字节 |")
    print(f"| 解码后的文件sha256值         {str(decoded_sha256).rjust(70)} |")
    print(f"| 解码前后的大小差异      {(str(decoded_size - encoded_size).rjust(70))} 字节 |")
    print(f"| 解码效率                   {str(efficiency).rjust(70)} % |")
    print("+-------------------------+-------------------------+-------------------------+---------------------+")


if __name__ == "__main__":
    CLI()
