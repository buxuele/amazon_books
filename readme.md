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
