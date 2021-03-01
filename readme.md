### 爬取亚马逊官网, 计算机类目的全部图书


#### 1. 效果图
- 这里放2张 Excel 的截图。
![全部图书的链接](https://raw.githubusercontent.com/buxuele/amazon_books/master/data/book_urls_2021-02-23--20-58-54.png)
![全部图书的详情](https://raw.githubusercontent.com/buxuele/amazon_books/master/data/2021-02-26--22-34-18.png)


#### 2. 思路
1. 获取全部图书的链接 
2. 获取一本书的信息
3. 改进第二步， 获取全部图书的信息,并保存。

#### 3. 数据保存
- 个人喜欢直接保存在 MongoDB
- 但是保存到 Excel 的话，视觉效果更好一些，也更友好一些。

#### 4.下一步 todo 
- 尝试爬取其他类目下的图书。


##### 5. 历程 roadmap

2021-02-28
1. 爬到第600条数据的时候，就已经被限制了。 
2. 因此需要把线程数提升大一点，代理的数量和质量都需要提高。
3. 稍后再试。

使用代理。稍后再试一次。多次请求的话，必然面临验证码的问题。todo 

2021-02-27
1. 设置时间停歇
2. 检查数据完整性，对不完整的数据进行处理。主要是给 food = {} 设置一个初始值。目的是防止后面 写入Excel 报错。
3. 增加重试
4. todo 用代理!。多次请求的话，必然面临验证码的问题。


2021-02-26 之前:
- 完成基本的内容