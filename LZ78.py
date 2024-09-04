import math
import os
import argparse
import hashlib

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


def CLI(command=None, in_file_path=None, code_file_path=None, decode_file_path=None):
    if command is None:
        parser = argparse.ArgumentParser(description='CLI_LZ78')
        parser.add_argument('command', choices=['help', 'encode', 'decode'],
                            help='Choose command: help or encode or decode')
        args = parser.parse_args()
        command = args.command

    if command == 'help':
        print('CLI_LZ78\n\nUsage: python script.py <command>\n\n'
              'Commands:\n '
              'help         Display help information\n  '
              'encode       Encode a file using LZ78 coding\n  '
              'decode       Decode a file encoded with LZ78 coding\n\n'
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


def find_seg(seg_s):
    if seg_s in seg_map:
        return seg_map[seg_s]
    return 0


def encode(in_file_path, code_file_path):
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


def decode(code_file_path, decode_file_path):
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

    # 输出表格

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
