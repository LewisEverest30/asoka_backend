# from django.test import TestCase

# Create your tests here.

import re

def parse_component_string(component_string):
    # 正则表达式模式
    pattern = r'(\d+)\*(\w+)-(\d+)'
    
    # 使用 findall 方法匹配所有符合模式的字符串
    matches = re.findall(pattern, component_string)
    
    # 将结果转换为字典列表
    components = []
    for match in matches:
        quantity = int(match[0])  # 个数
        product_type = match[1]    # 产品类型
        product_id = int(match[2])  # 产品ID
        components.append({
            'quantity': quantity,
            'product_type': product_type,
            'product_id': product_id
        })
    
    return components

# 示例字符串
component_string = "3*珠-1 2*珠-2 1*手链-1"

# 调用函数并打印结果
parsed_components = parse_component_string(component_string)
print(parsed_components)