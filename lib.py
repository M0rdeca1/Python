from telebot import types
import threading
#Подключения блокировщика потока 
lock = threading.Lock()
 
#Дублирующиеся или громоздкие сообщения
welcome_mes = "Вас приветствует бот интернет-магазина Деревяшка. Вы можете посмотреть товары, обратиться за поддержкой или написать отзыв. Для навигации используйте кнопки"
view_products_mes = "Выберите категорию или нажмите смотреть все товары, чтобы посмотреть все товары"
deltovar_mes = 'Пожалуйста, введите артикул товара, который желаете удалить из корзины.\nАртикул написан латиницей.'
addmark_mes = "Чтобы оценить товар, напишите его артикул, оценку и комментарий через ';'.\nАртикул пишется с большой буквы латиницей. Оценка производиться от 0 до 5. Комментарий можно не писать"
response_user_mes = "Запрос принят на рассмотрение. В скором времени с вами свяжется менеджер"
error_mes = 'Не удалось выполнить запрос.'
 
#Дублирующийся запрос
view_basket_request = "SELECT tovar_article, name, price, count FROM basket JOIN tovary on tovary.article = basket.tovar_article WHERE basket.id_user = "
 
#Функция принимает массив данных по товару и преобразует их в удобный формат
#Выводит текст карточки товара, его фотографию и кнопки под карточкой товара для последующей навигации
def view_tovary(tovary):
    
    if tovary[10] == None:
        avg_mark = "-"
    else:
        avg_mark = tovary[10]
    text = f"<b>Средняя оценка:</b> {avg_mark}\n<b>Тип:</b> {tovary[8]}\n<b>Артикул:</b> {tovary[0]}\n<b>Название:</b> {tovary[1]}\n<b>Цена:</b> {tovary[3]}\n<b>Размер:</b> {tovary[4]}\n<b>Материал:</b> {tovary[5]}\n<b>Производитель:</b> {tovary[6]}\n<b>Гариантия:</b> {tovary[7]}\n<b>Описание:</b> {tovary[9]}\n\n"
    photo = open("tovary_photo/"+tovary[2]+'.jpg', 'rb')    
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='Купить', callback_data='addtovar')
    item2 = types.InlineKeyboardButton(text='Посмотреть отзывы', callback_data='view_review')
    markup.add(item1, item2)
    return(text,photo,markup)
#Функция создаёт шаблон для вывода запроса пользователя менеджеру
#Выводит шаблон текста сообщения и кнопки под сообщением для навигации
def ticket_template():
    ticket_mes = "<b>Появился новый запрос от пользователя: </b>"
    
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text='Принять запрос', callback_data='accept_ticket')
    markup.add(item1)   
    return(ticket_mes,markup)
#Функция принимает: экземпляр курсора БД, экземпляр БД, тип запроса, id сообщения в группе менеджеров, дату запроса и имя пользователя
#Далее она создаёт на основании этих данных новую запись в БД 
def write_ticket(sql,db, id_user, problem,mes_id, date, user_username):
    with lock:
        sql.execute("INSERT INTO tickets (id_user, problem, id_message, date, user_username) VALUES (?, ?, ?, ?, ?);", 
(f"{id_user}", f"{problem}", f"{mes_id}", f"{str(date)}", f"{user_username}"))
        db.commit() 
#Функция принимает массив товаров, которые являются массивами данных о товаре
#Далее она преобразует эту информацию в удобный формат и выводит получившееся сообщение  
def view_basket(tovary):
    text = "<b>Корзина:</b>\nАртикул | Название | Цена | Количество\n"
    sum_price=0
    for tovar in tovary:
        text += f"{tovar[0]} | {tovar[1]} | {tovar[2]} | {tovar[3]}\n"
        sum_price+=int(tovar[2])*int(tovar[3])
    text+="Всего: " +str(sum_price)+" рублей"
    return(text)
#Функция принимает экземпляр курсора БД, экземпляр БД и id клиента
#Далее функция удаляет записи о товарах данного пользователя в БД
def clear_basket(sql,db, user_id):
    with lock:
        rows = sql.execute(f"SELECT id FROM basket where id_user= '{user_id}'").fetchall()
    for row in rows:
        with lock:
            sql.execute(f"DELETE from basket where id = {row[0]}")
            db.commit()    