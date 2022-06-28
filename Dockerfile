# 實際上所有的指令都是一層layer，如果有前面做過的layer，那麼就可以直接使用他的cache使用
# 如果該層layer都沒有update，那麼就不用重新build一次，而是用cache，若有改變才重新build layer
# 因此才會先有COPY requirements.txt 然後再一次COPY . .的行為產生，為了就是optimize 時間
# 會從updated的layer作開始重新build layer的動作。

FROM python:3.9.13

# 設定目前的work directory
WORKDIR /usr/src/app 

# 將requirements.txt複製一份到container的/usr/src/app當中
COPY requirements.txt ./  

RUN pip install --no-cache-dir -r requirements.txt 

# copy所有現在local directory當中的所有檔案到work directory in container
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]