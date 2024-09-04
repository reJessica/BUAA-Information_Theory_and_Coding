import heapq
import os
import argparse
import hashlib
from queue import Queue


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


def CLI(command=None, in_file_path=None, code_file_path=None, decode_file_path=None):
    if command is None:
        parser = argparse.ArgumentParser(description='CLI_Huffman')
        parser.add_argument('command', choices=['help', 'encode', 'decode'],
                            help='Choose command: help or encode or decode')
        args = parser.parse_args()
        command = args.command

    if command == 'help':
        print('CLI_Huffman\n\nUsage: python script.py <command>\n\n'
              'Commands:\n '
              'help         Display help information\n  '
              'encode       Encode a file using Huffman coding\n  '
              'decode       Decode a file encoded with Huffman coding\n\n'
              'Example:\n  python script.py encode')
    elif command == 'encode':
        if in_file_path is None:
            in_file_path = input("请输入要编码的文件路径: ")
        if not os.path.exists(in_file_path):
            print("Error: 输入文件不存在")
            return
        if code_file_path is None:
            code_file_path = input("请输入编码文件存放路径: ")
        encode(in_file_path, code_file_path)
        test1(in_file_path, code_file_path)
    elif command == 'decode':
        if code_file_path is None:
            code_file_path = input("请输入要解码的文件路径: ")
        if not os.path.exists(code_file_path):
            print("Error: 编码文件不存在")
            return
        if decode_file_path is None:
            decode_file_path = input("请输入解码文件存放路径: ")
        decode(code_file_path, decode_file_path)
        test2(code_file_path, decode_file_path)
    else:
        print('Unknown command')


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


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


def Huffman_tree(in_file_path, code_file_path):
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


def encode(in_file_path, code_file_path):
    Huffman_tree(in_file_path, code_file_path)
    with open(in_file_path, "rb") as IN, open(code_file_path, "wb") as OUT:
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

        while True:
            c = IN.read(1)
            if not c:
                break
            result = result + code[ord(c) + 1]
        while len(result) >= 8:
            result_byte = result[:8]
            result = result[8:]
            result_int = int(result_byte, 2)
            try:
                OUT.write(bytes([result_int]))
            except IOError:
                print("Error: 写入文件出错")

        if len(result) > 0:
            result_byte = result.ljust(8, '0')
            num_zeros_added = max(0, 8 - (len(result) % 8))
            result_int = int(result_byte, 2)
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


def decode(code_file_path, decode_file_path):
    with open(code_file_path, "rb") as IN, open(decode_file_path, "wb+") as OUT:
        IN.seek(-1, 2)
        last_byte = IN.read(1)
        last_byte_value = int.from_bytes(last_byte, byteorder='big')
        result1 = ""
        IN.seek(0)
        byte = IN.read(1)
        while byte:
            byte_int = int.from_bytes(byte, byteorder='big')
            binary_str = format(byte_int, '08b')
            result1 += binary_str
            byte = IN.read(1)
        num = len(result1) - last_byte_value - 8
        result2 = result1[:num]
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


def test1(in_file_path, code_file_path):
    original_size = os.path.getsize(in_file_path)
    original_sha256 = calculate_sha256(in_file_path)
    encoded_size = os.path.getsize(code_file_path)
    encode_sha256 = calculate_sha256(code_file_path)

    efficiency = ((original_size - encoded_size) * 100) / original_size

    print("+-------------------------+-------------------------+-------------------------+---------------------+")
    print(f"| 编码前的文件大小       {str(original_size).rjust(70)} 字节 |")
    print(f"| 编码前的文件sha256值        {str(original_sha256).rjust(70)} |")
    print(f"| 编码后的文件大小       {str(encoded_size).rjust(70)} 字节 |")
    print(f"| 编码后的文件sha256值        {str(encode_sha256).rjust(70)} |")
    print(f"| 编码前后的大小差异     {str(encoded_size - original_size).rjust(70)} 字节 |")
    print(f"| 编码效率                  {str(efficiency).rjust(70)} % |")
    print("+-------------------------+-------------------------+-------------------------+---------------------+")


def test2(code_file_path, decode_file_path):
    encoded_size = os.path.getsize(code_file_path)
    encode_sha256 = calculate_sha256(code_file_path)
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
