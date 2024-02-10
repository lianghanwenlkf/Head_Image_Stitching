# 好友头像大图拼接
## 1 素材准备（source）
### 1.1 qq头像url
可以从qq邮箱导出联系人，得到QQmail.csv，第一列为昵称，第三列为qq邮箱，包含qq号，后续可通过qq号下载头像
### 1.2 微信头像url
可以从留痕（MemoTrace）中导出联系人，得到wechat.xlsx，’Remark‘列为昵称，’bigHeadImgUrl‘列为头像url
## 2 参数设置（configs.yaml）
### 2.1 原始数据路径
#### （1）qq_file_path # QQ联系人文件
#### （2）wechat_file_path # 微信联系人文件
### 2.2 保存路径
#### （1）head_img_path # 头像保存路径
#### （2）output_path # 拼接大图保存路径
#### （3）log_path # 运行日志保存路径
### 2.3 过程控制
#### （1）qq_download_mode # 是否下载qq头像
#### （2）wechat_download_mode # 是否下载微信头像
#### （3）stitch_mode: True # 是否拼接大图
### 2.4 图像设置
#### （1）image_size: 2560 # 大图边长像素
#### （2）edge_percentage # 小图边缘计算范围百分比
## 3 运行
### head_image_stitching.py