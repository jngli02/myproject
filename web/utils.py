import re

def replace_emoji(content):
    # 定义表情与图片的映射关系
    emoji_mapping = {
        '苦笑': '苦笑.png',
        '得意': '得意.png',
        '放声大哭': '放声大哭.png'
        # 添加更多表情与图片的映射关系
    }

    # 使用正则表达式查找消息内容中的表情代码
    emoji_pattern = re.compile(r':(苦笑|得意|放声大哭):')  # 匹配示例中的表情代码
    matches = emoji_pattern.findall(content)

    # 遍历匹配到的表情代码，并替换为对应的图片标签
    for match in matches:
        emoji_img = f'<img src="/static/emojis/{emoji_mapping.get(match)}" alt="{match}">'
        content = content.replace(f':{match}:', emoji_img)
    return content

