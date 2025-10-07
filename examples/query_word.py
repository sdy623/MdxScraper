#!/usr/bin/env python
"""快速查询单个词汇并输出完整 HTML（含 CSS）

使用方法:
    python query_word.py <word> [--mdx FILE] [--output FILE]

示例:
    # 查询单词并打印到控制台
    python query_word.py hello
    
    # 指定词典文件
    python query_word.py hello --mdx data/mdict/my_dict.mdx
    
    # 保存到文件
    python query_word.py hello --output hello.html
    
    # 完整示例
    python query_word.py hello --mdx data/mdict/dict.mdx --output result.html
"""

import argparse
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from mdxscraper import Dictionary
from mdxscraper.core.renderer import merge_css, embed_images


def query_word(mdx_file: Path, word: str, output_file: Path = None, embed_dict_images: bool = True) -> str:
    """查询单个词汇并返回完整 HTML
    
    Args:
        mdx_file: MDX 词典文件路径
        word: 要查询的单词
        output_file: 可选的输出文件路径
        embed_dict_images: 是否嵌入词典中的图片（base64）
        
    Returns:
        包含完整 CSS 的 HTML 字符串
    """
    
    # 打开词典
    with Dictionary(mdx_file) as dict:
        # 查询单词（自动处理大小写、连字符等）
        html_content = dict.lookup_html(word)
        
        if not html_content:
            print(f"❌ 未找到单词: {word}", file=sys.stderr)
            return None
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 尝试提取词典内部的 CSS
        dict_css = ""
        try:
            # 检查原始 HTML 是否包含 link 标签引用 CSS
            if '<link' in html_content.lower():
                # 创建完整的 HTML 结构供 merge_css 处理
                temp_html = f"<html><head>{html_content}</head><body></body></html>"
                temp_soup = BeautifulSoup(temp_html, 'lxml')
                
                # 调用 merge_css 提取并合并 CSS
                merged_soup = merge_css(temp_soup, mdx_file.parent, dict.impl, None)
                
                # 提取合并后的 CSS
                if merged_soup.head and merged_soup.head.style:
                    dict_css = merged_soup.head.style.string or ""
                    if dict_css:
                        print(f"✅ 已提取词典 CSS ({len(dict_css)} 字符)")
            else:
                print(f"ℹ️  词典内容未包含 CSS 引用")
        except Exception as e:
            print(f"ℹ️  无法提取词典 CSS: {e}")
            import traceback
            traceback.print_exc()
        
        # 如果需要嵌入图片
        if embed_dict_images:
            try:
                temp_soup = BeautifulSoup(f"<html><body>{html_content}</body></html>", 'lxml')
                embedded_soup = embed_images(temp_soup, dict.impl)
                # 更新 html_content
                html_content = str(embedded_soup.body)
                html_content = html_content.replace('<body>', '').replace('</body>', '')
                print(f"✅ 已嵌入词典图片")
            except Exception as e:
                print(f"ℹ️  无法嵌入图片: {e}")
        
        # 构建完整的 HTML 文档
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{word}</title>
    <style>
        /* ========== 词典内部 CSS ========== */
        {dict_css}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        # 保存到文件（如果指定）
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(full_html, encoding='utf-8')
            print(f"✅ 已保存到: {output_file}")
            print(f"📊 文件大小: {len(full_html):,} 字符")
        
        return full_html


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="查询 MDX 词典中的单个词汇并输出完整 HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "word",
        help="要查询的单词"
    )
    
    parser.add_argument(
        "--mdx",
        type=Path,
        default=Path("data/mdict/your_dictionary.mdx"),
        help="MDX 词典文件路径 (默认: data/mdict/your_dictionary.mdx)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="输出 HTML 文件路径（不指定则打印到控制台）"
    )
    
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="不嵌入词典中的图片（减小文件大小）"
    )
    
    args = parser.parse_args()
    
    # 检查词典文件是否存在
    if not args.mdx.exists():
        print(f"❌ 词典文件不存在: {args.mdx}", file=sys.stderr)
        print(f"   当前目录: {Path.cwd()}", file=sys.stderr)
        print(f"   请使用 --mdx 指定正确的词典文件路径", file=sys.stderr)
        return 1
    
    print("=" * 70)
    print(f"📖 查询单词: {args.word}")
    print(f"📚 词典: {args.mdx}")
    print("=" * 70)
    
    # 执行查询
    result = query_word(args.mdx, args.word, args.output, embed_dict_images=not args.no_images)
    
    if result:
        if not args.output:
            # 如果没有指定输出文件，打印部分内容到控制台
            print("\n" + "=" * 70)
            print("HTML 输出预览（前 1000 字符）:")
            print("=" * 70)
            print(result[:1000])
            if len(result) > 1000:
                print(f"\n... (还有 {len(result) - 1000:,} 个字符)")
            print("\n提示: 使用 --output 参数保存到文件")
        
        print("\n" + "=" * 70)
        print("✅ 查询完成!")
        print("=" * 70)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
