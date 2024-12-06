import os
import csv
from pelican import signals
from pelican.contents import Page
from pelican.utils import slugify
from pelican.generators import Generator

class CSVPageGenerator(Generator):
    def __init__(self, context, settings, path, theme, output_path, *null):
        super().__init__(context, settings, path, theme, output_path, )
        #print("\n=== 初始化 CSVPageGenerator ===")
        self.output_path = output_path
        self.context = context
        self.settings = settings
        self.path = path
        self.theme = theme
        self.content_path = os.path.join(path, '')
        #print(f"内容目录路径: {self.content_path}")
        self.categories = {}  # 用于存储每个分类下的页面

    def generate_output(self, writer):
        #print("\n=== 开始生成页面 ===")
        try:
            content_items = os.listdir(self.content_path)
            #print(f"找到目录项: {content_items}")
            total = 0
            for item in content_items:
                item_path = os.path.join(self.content_path, item)
                #print(f"\n检查目录项: {item}")
                
                # 跳过articles和pages目录，以及非目录项
                if item in ['articles', 'pages'] or not os.path.isdir(item_path):
                    #print(f"跳过 {item} (articles/pages或非目录)")
                    continue
                
                # 使用目录名作为category
                category = item
                #print(f"\n处理分类: {category}")
                
                # 初始化分类的页面列表
                if category not in self.categories:
                    self.categories[category] = []
                
                # 查找目录下的CSV文件
                files = os.listdir(item_path)
                #print(f"目录下的文件: {files}")
                
                for file in files:
                    if file.endswith('.csv'):
                        csv_file = os.path.join(item_path, file)
                        #print(f"\n=== 处理CSV文件: {csv_file} ===")
                        
                        with open(csv_file, 'r', encoding='utf-8-sig') as f:
                            reader = csv.DictReader(f)
                            for index, row in enumerate(reader):
                                #print(f"\n处理第 {index + 1} 条记录")
                                total += 1
                                # 创建页面内容
                                title = row.get('标题', f'Page {index}')
                                url = row.get('网址', '')
                                favicon = row.get('favicon', '')
                                screenshot = row.get('截图', '')
                                description = row.get('描述', '')
                                
                                #print(f"标题: {title}")
                                #print(f"网址: {url}")

                                # 检查必需字段是否为空
                                if not all([title, url, favicon, screenshot, description]):
                                    print(f"跳过第 {index + 1} 条记录：必需字段缺失")
                                    continue
                                
                                # 生成页面路径
                                slug = slugify(f"{category}-{index}")
                                save_as = f'post-{category}-{index}.html'
                                url_path = f'post-{category}-{index}'
                                
                                #print(f"生成页面: {save_as}")

                                # 创建页面元数据
                                metadata = {
                                    'title': title,
                                    'category': {
                                        'name': category,
                                        'url': f'category/{category}.html'
                                    },
                                    'save_as': save_as,
                                    'url': url_path,
                                    'website_url': url,
                                    'favicon_path': favicon,
                                    'screenshot_path': screenshot,
                                    'website_description': description,
                                    'index': index,
                                    'status': 'published',
                                }

                                # 创建Page对象并写入页面
                                page = Page(
                                    content='',
                                    metadata=metadata,
                                    settings=self.settings,
                                    source_path=csv_file,
                                    context=self.context
                                )
                                
                                # 将页面添加到对应分类
                                self.categories[category].append(page)
                                
                                writer.write_file(
                                    save_as,
                                    self.get_template('post-nav'),
                                    self.context,
                                    page=page,
                                    relative_urls=self.settings.get('RELATIVE_URLS'),
                                    override_output=True
                                )
                                #print(f"✅ 成功生成页面: {save_as}")
                                
            # 生成分类页面
            for category, pages in self.categories.items():
                # 创建分类页面元数据
                category_metadata = {
                    'title': f'{category}',
                    'save_as': f'category/{category}.html',
                    'url': f'category/{category}',
                    'status': 'published',
                    'total': len(pages),
                    'categories': self.categories,
                }
                
                # 创建分类页面
                category_page = Page(
                    content='',
                    metadata=category_metadata,
                    settings=self.settings,
                    source_path='',
                    context=self.context,
                )
                
                # 添加该分类下的所有页面到上下文
                category_context = self.context.copy()
                category_context['articles_page'] = type('Obj', (), {'object_list': pages})  # 创建一个模拟的 articles_page 对象
                category_context['category'] = category
                
                # 写入分类页面
                writer.write_file(
                    category_metadata['save_as'],
                    self.get_template('category-nav'),
                    category_context,
                    page=category_page,
                    relative_urls=self.settings.get('RELATIVE_URLS'),
                    override_output=True
                )
                
        except Exception as e:
            print(f"生成页面时出错: {str(e)}")

def get_generators(pelican_object):
    #print("\n=== 注册 CSVPageGenerator ===")
    return CSVPageGenerator

def register():
    #print("\n=== 连接 CSVPageGenerator 到信号 ===")
    signals.get_generators.connect(get_generators) 