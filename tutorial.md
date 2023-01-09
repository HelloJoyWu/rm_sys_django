# build_web_log
*build by Django*
### virtual environment
#### 起始設定
```bash=
# mkvirtualenv -v 3 -a C:\Users\rmpeter0474\Documents\repo_programes\web djando_web
mkdir web
cd web
virtualenv --python C:\\Users\\rmpeter0474\\AppData\\Local\\Programs\\Python\\Python38\\python.exe django_web
```
    mkvirtualenv options:
    -a project_path       Associate existing path as project directory
    -i package            Install package in new environment. This option
                        can be repeated to install more than one package.
    -r requirements_file  requirements_file is passed to
                        pip install -r requirements_file
#### 使用方法
*   deactivate — 退出當前的Python虛擬環境
*   workon — 列出可用的虛擬環境
*   workon name_of_environment — 激活指定(name_of_environment)的Python虛擬環境
*   rmvirtualenv name_of_environment — 刪除指定的環境
```bash=
## terminal啟動
.\django_web\Scripts\activate # source venv/bin/activate
pip install django
pip list >> requirements.txt
```
### django
#### 架構
```
rmsys/                # Website folder
    manage.py         # Script to run Django tools for this project (created using django-admin)
    rmsys/            # Website/project folder (created using django-admin)
    catalog/          # Application folder (created using manage.py)
```
#### 創建
```bash=
django-admin startproject rmsys
cd rmsys
python manage.py startapp catalog

python manage.py runserver
```
```
rmsys/rmsys/
*    __init__.py  是一個空文件，指示 Python 將此目錄視為 Python 套件。
*    settings.py  包含所有的網站設置。這是可以註冊所有創建的應用的地方，也是靜態文件，數據庫配置的地方，等等。
*    urls.py      定義了網站url到view的映射。雖然這裡可以包含所有的url，但是更常見的做法是把應用相關的url包含在相關應用中，你可以在接下來的教程裡看到。
*    wsgi.py      幫助Django應用和網絡服務器間的通訊。你可以把這個當作模板。

rmsys/catalog/
*    migrations/  一個migration文件夾，用來存放 “migrations” ——當你修改你的數據模型時，這個文件會自動升級你的資料庫。
*    views.py     視圖函數
*    models.py    模型
*    tests.py     測試
*    admin.py     網站管理設置
*    apps.py      註冊應用
```
#### **筆記**
*   在startapp後，記得將app加入settings.py的INSTALLED_APPS，django才能讀取到該app下的templates或static 

    參考: [Project and apps](https://djangogirlstaipei.gitbooks.io/django-girls-taipei-tutorial/content/django/project_and_app.html)
*   File structure
```
    rmsys/ 
    |-- manage.py
    |-- rmsys/ #project
        |-- settings.py
        |-- urls.py
    |-- catalog/ # app 1
        |-- templates/
        |-- static/
        |-- admin.py
        |-- apps.py
        |-- models.py
        |-- tests.py
        |-- urls.py
        |-- views.py
    |-- account/ # app 2
        ...
    ...
```
*   MTV web-frame 
 
| 一般MVC架構 | Django 架構 |
| ---: | ---: |
| Model | Model(Data Access Logic) |
| View | Template(Presentation Logic) |
| View | View(Business Logic) |
| Controller | Django itself |
    View的目的不是"資料如何呈現"，而是"呈現哪一個資料"! 
由Models儲存資料，View邏輯運算與處理呈現，最後套在Tamplates發布呈現    
參考: [傳統 MVC 模式與 Django MTV 模式介紹與比較](https://mropengate.blogspot.com/2015/08/mvcdjangomtv.html) 

*   開發流程 


    需求分析 --> 資料庫設計(model) --> html模板設計與關聯 

*    django auth

1. auth_user 欄位
    
    
    * *groups*

        Many-to-many relationship to Group
    * *user_permission*
        
        Many-to-many relationship to Permission
    * *is_staff*
        
        Designates whether this user can access the admin site.
    * *is_active*
        
        Designates whether this user account should be considered active. We recommend that you set this flag to False instead of deleting accounts; that way, if your applications have any foreign keys to users, the foreign keys won’t break.

* JQuery in local 


    To add to what others have written, if you want to make JQuery available throughout your site/app and you don't like external dependencies such as Google you can do the following:

    1. Download the latest "compressed, production" JQuery at https://jquery.com/download/ - for example, on the command line in your static directory (might be <projectname>/static): wget https://code.jquery.com/jquery-2.1.3.min.js
    2. Add a reference to load JQuery in your site's "base" template file (might be <projectname>/<appname>/templates/base.html) - for example: Add <script src="{% static 'jquery-2.1.3.min.js' %}"></script> in the <head> section
    3. Test the JQuery installation by adding something like the following to one of your templates:

    <script type="text/javascript">
      $(document).ready(
        function(){
          $("#jqtest").html("JQuery installed successfully!");
        }
      );
    </script>
    <p id="jqtest"></p>
    
    4. If necessary/usual after making template updates, restart your Django server, then load a page which uses the template with the test code

#### 常用指令
*   每次模型改變，都需要運行下面命令:
```bash=
python manage.py makemigrations
python manage.py migrate
```