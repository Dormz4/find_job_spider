import hashlib


def lagou_calc_x_http_token(user_trace_token):
    ori_data = 'HTTP_JS_KEY'+user_trace_token
    md5_data = hashlib.md5(ori_data.encode('utf-8'))
    num_list = list()
    md5_data = md5_data.hexdigest()
    is_record = False
    for i in range(0,len(md5_data)):
        if is_record is True:
            is_record = False
            print(md5_data[i-1],md5_data[i])
            num = int(md5_data[i-1],16)*0x10 +int(md5_data[i],16)
            num_list.append(num)
        if i%2==0:
            is_record = True

    res = ''
    for i in range(0,len(num_list)):
        res += hex(num_list[i]>>0x4).split('x')[1]+ hex(num_list[i]&0xf).split('x')[1]

    return res