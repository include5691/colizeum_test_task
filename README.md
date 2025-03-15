## Task 1:
Create and activate your virtual environment  
```pip install -r requirements.txt```  
```python3 tasks/1.async_data_fetcher.py```  
Open result.xlsx  

#### Note 1:
Добавлять env-файл в git-репозиторий - плохая практика, но в этом тестовом примере env-файл включен

#### Note 2:
Во время теста сервера OpenWeather периодически не подгружались, поэтому если наблюдается ошибка соединения - попробуйте чуть позже

## Task 2:

#### Note 1:
Не представляю возможным извлекать динамически загружаемый контент с помощью библиотеки BeautifulSoup без эмуляции браузера, например, playwright 

#### Note 1:
Я полагаю, что в описании задачи сознательно допущены пропуски библиотек, поскольку библиотека pandas не предоставляет методов для работы с Google таблицами. Распространенный способ чтения и записи в Google таблицы - использовать библиотеку `gspread`. Также вы можете ознакомиться с моим [пользовательским](https://github.com/include5691/au_sheets) решение.