import datetime
import httpx
import os
import pandas as pd
import math
from telegram.ext import ContextTypes
from typing import List
from wbnotifierbot import config
from wbnotifierbot.db import fetch_all
from wbnotifierbot.handlers.response import send_response
from wbnotifierbot.templates import render_template



class Wildberries:
    
    async def stocks(self) -> List[dict]:
        '''Остатки товаров на складах WB
        Данная функция возвращает данные по остаткам на складах для всех артикулов на вчерашних день
        :quantity в ответе - остаток на всех складах'''
        date_yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        headers = {"Authorization": config.WBAPIMPCONT, "content-Type": "application/json"}
        api_url = config.WBURLGETSTOCKS+"?dateFrom="+date_yesterday
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
        return response.json()

    async def get_all_articles(self) -> dict:
        '''Функция возвращает словарь всех товаров с картинками'''
        request_body = {"sort": {
              "cursor": {
                      "limit": 1000
                  },
              "filter": {
                  "withPhoto": -1
                  }
          }
        }
        headers = {"Authorization": config.WBAPIMPCONT, "content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(config.WBURLCURSORLIST, headers=headers, json=request_body)
        all_cards = response.json()["data"]["cards"]
        all_mnID_with_img = {}
        for _ in all_cards:
            all_mnID_with_img[_["nmID"]] = {"img":_['mediaFiles'][0]}
        return all_mnID_with_img

    async def detail(self, nmIDs: list) -> dict:
        '''Получение статистики КТ за выбранный период, по nmID'''
        
        date_time_from = (datetime.datetime.today() - datetime.timedelta(days=22)).strftime("%Y-%m-%d 00:00:00")
        date_time_to = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        request_body = {
            "nmIDs": nmIDs,
            "timezone": "Europe/Moscow",
            "period": {
                "begin": date_time_from,
                "end": date_time_to
            },
            "orderBy": {
                "field": "ordersSumRub",
                "mode": "asc"
            },
            "page": 1
        }
        headers = {"Authorization": config.WBAPIANALYTPRICEDISC, "content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(config.WBURLGETDETAIL, headers=headers, json=request_body)
        return response.json()
    
    async def _send_alter_for_admins(self, context: ContextTypes.DEFAULT_TYPE, articles: dict, count:int):
        admins = await fetch_all(
                        "select telegram_user_id from bot_users where is_admin=:is_admin",
                        {"is_admin": 1},
                        ) 
        if count > 5:
            today = datetime.datetime.today().strftime("%d.%m.%y %H-%M")
            today_date = datetime.datetime.today().strftime("%d.%m.%Y")
            name_file = f"./results_checking_stocks_{today}.xlsx"
            df = pd.DataFrame(articles)
            df_T = df.T
            df_T_only_true = df_T[df_T['Нужно собрать'] > 0] 
            del df_T_only_true['img']
            df_T_only_true_total = df_T_only_true.sort_values(by=['Нужно собрать'], ascending=False)
            df_T_only_true_total.to_excel(name_file)
            for admin in admins:
                await context.bot.send_message(chat_id=admin["telegram_user_id"], text=f"░░░░░░░░░░░░░░░░░░░░ {today_date}")
                await send_response(response=render_template( "result_checking.j2"),
                                    document=name_file, chat_id=admin["telegram_user_id"],
                                    context=context)
            os.remove(name_file)
        else:
            for admin in admins:
                    await context.bot.send_message(chat_id=admin["telegram_user_id"], text=f"░░░░░░░░░░░░░░░░░░░░ {today_date}")
                    for nm in articles:
                        if articles[nm]['Нужно собрать'] > 0:
                            send_response(response=render_template(
                                                "alert_for_admin.j2", 
                                                 data={
                                                       "img":articles[nm]["img"],
                                                       "link": articles[nm]["Ссылка"],
                                                       "vendorCode":articles[nm]["Артикул продавца"],
                                                       "stock":articles[nm]["Остаток"],
                                                       "avgOrdersCountPerDay": articles[nm]["Ср.продажи в день"],
                                                       "need": articles[nm]["Нужно собрать"]
                                                  }
                                            ), chat_id=admin["telegram_user_id"], context=context 
                            )
    
    async def _send_alter_for_admin(self, context: ContextTypes.DEFAULT_TYPE, articles: dict, count:int, 
                                chat_id_for_del: int | None = None,
                                msg_id_for_del:int | None = None):
        await context.bot.delete_message(chat_id=chat_id_for_del, message_id=msg_id_for_del)
        if count > 5:
            today = datetime.datetime.today().strftime("%d.%m.%y %H-%M")
            name_file = f"{config.PATH4XLSXFILE}results_checking_stocks_{today}.xlsx"
            df = pd.DataFrame(articles)
            df_T = df.T
            df_T_only_true = df_T[df_T["Нужно собрать"] > 0] 
            del df_T_only_true['img']
            df_T_only_true_total = df_T_only_true.sort_values(by=['Нужно собрать'], ascending=False)
            df_T_only_true_total.to_excel(name_file)
            await send_response(response=render_template(
                                                "result_checking.j2"),
                                document=name_file,
                                chat_id=chat_id_for_del,
                                context=context)
            os.remove(name_file)

        else:
            for nm in articles:
                if articles[nm]["Нужно собрать"] > 0:
                    send_response(response=render_template(
                                        "alert_for_admin.j2", 
                                         data={
                                               "img":articles[nm]["img"],
                                               "link": articles[nm]["Ссылка"],
                                               "vendorCode":articles[nm]["Артикул продавца"],
                                               "stock":articles[nm]["Остаток"],
                                               "avgOrdersCountPerDay": articles[nm]["Ср.продажи в день"],
                                               "need": articles[nm]["Нужно собрать"]
                                          }
                                    ), chat_id=chat_id_for_del, context=context 
                    )
                            
    async def start_checking(self, context: ContextTypes.DEFAULT_TYPE, 
                                chat_id_for_del: int | None = None,
                                msg_id_for_del:int | None = None):
        articles = await self.get_all_articles()
        articles_detail = await self.detail(list(articles.keys()))
        count_art_for_alert = 0
        for _ in articles_detail["data"]["cards"]:
            articles[_["nmID"]]["Артикул продавца"] = _["vendorCode"]
            articles[_["nmID"]]["Остаток"] = _["stocks"]["stocksWb"]
            articles[_["nmID"]]["Ср.продажи в день"] = math.ceil(_['statistics']['selectedPeriod']['avgOrdersCountPerDay'])
            articles[_["nmID"]]["Нужно собрать"] = articles[_["nmID"]]["Ср.продажи в день"]*21 - articles[_["nmID"]]["Остаток"]
            articles[_["nmID"]]["Ссылка"] = f"https://www.wildberries.ru/catalog/{_['nmID']}/detail.aspx?targetUrl=SP"
            if articles[_["nmID"]]["Нужно собрать"] > 0:
                count_art_for_alert += 1
        if chat_id_for_del:
            await self._send_alter_for_admin(context, articles, count_art_for_alert, chat_id_for_del, msg_id_for_del)
        else:
            await self._send_alter_for_admins(context, articles, count_art_for_alert)
        
        
wildberries = Wildberries()
