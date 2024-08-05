#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sqlite3
import json


class DataBase(object):
    def __init__(self):
        self.conn = sqlite3.connect('data.db')
        self.cursor = self.conn.cursor()
        self.create_user_post_table()
        self.create_creators_table()
        self.create_user_like_table()
        self.create_mix_table()
        self.create_music_table()

    # def create_user_post_table(self):
    #     sql = """CREATE TABLE if not exists t_user_post (
    #                     id integer primary key autoincrement,
    #                     sec_uid varchar(200),
    #                     aweme_id integer unique, 
    #                     rawdata json
    #                 );"""
    #
    #     try:
    #         self.cursor.execute(sql)
    #         self.conn.commit()
    #     except Exception as e:
    #         pass
    #
    # def get_user_post(self, sec_uid: str, aweme_id: int):
    #     sql = """select id, sec_uid, aweme_id, rawdata from t_user_post where sec_uid=? and aweme_id=?;"""
    #
    #     try:
    #         self.cursor.execute(sql, (sec_uid, aweme_id))
    #         self.conn.commit()
    #         res = self.cursor.fetchone()
    #         return res
    #     except Exception as e:
    #         pass
    #
    # def insert_user_post(self, sec_uid: str, aweme_id: int, data: dict):
    #     insertsql = """insert into t_user_post (sec_uid, aweme_id, rawdata) values(?,?,?);"""
    #
    #     try:
    #         self.cursor.execute(insertsql, (sec_uid, aweme_id, json.dumps(data)))
    #         self.conn.commit()
    #     except Exception as e:
    #         pass
    
    def create_user_post_table(self):
        sql = """CREATE TABLE if not exists t_user_post (
            id integer primary key autoincrement,
            sec_uid varchar(200),
            aweme_id integer unique,
            nickname varchar(200),
            create_time integer,
            desc text,
            uid varchar(200),
            owner_handle varchar(200),
            comment_count integer,
            digg_count integer,
            collect_count integer,
            share_count integer,
            rawdata json
        );"""
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            pass

    def create_creators_table(self):
        sql = """CREATE TABLE if not exists creators (
            uid varchar(200) primary key,
            sec_uid varchar(200),
            nickname varchar(200),
            owner_handle varchar(200)
        );"""
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            pass

    def get_user_post(self, sec_uid: str, aweme_id: int):
        sql = """select id, sec_uid, aweme_id, nickname, create_time, desc, uid, owner_handle, 
                comment_count, digg_count, collect_count, share_count, rawdata 
                from t_user_post where sec_uid=? and aweme_id=?;"""
        try:
            self.cursor.execute(sql, (sec_uid, aweme_id))
            self.conn.commit()
            res = self.cursor.fetchone()
            return res
        except Exception as e:
            pass

    def insert_user_post(self, sec_uid: str, aweme_id: int, data: dict):
        # 清理和提取所需数据
        cleaned_data = {
            "aweme_id": data.get("aweme_id"),
            "desc": data.get("desc"),
            "create_time": data.get("create_time"),
        }
    
        # 从 author 中获取信息
        author = data.get("author", {})
        cleaned_data.update({
            "nickname": author.get("nickname"),
            "uid": author.get("uid"),
        })
    
        # 从 music 中获取 owner_handle
        music = data.get("music", {})
        cleaned_data["owner_handle"] = music.get("owner_handle")
    
        # 从 statistics 中获取信息
        statistics = data.get("statistics", {})
        cleaned_data.update({
            "comment_count": statistics.get("comment_count"),
            "digg_count": statistics.get("digg_count"),
            "collect_count": statistics.get("collect_count"),
            "share_count": statistics.get("share_count"),
        })

        # 插入到 t_user_post 表
        insert_sql = """INSERT INTO t_user_post (sec_uid, aweme_id, nickname, create_time, desc, uid, 
                        owner_handle, comment_count, digg_count, collect_count, share_count, rawdata) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    
        # 插入或更新 creators 表
        upsert_creator_sql = """INSERT OR REPLACE INTO creators (uid, sec_uid, nickname, owner_handle) 
                                VALUES (?, ?, ?, ?);"""
    
        try:
            # 插入 t_user_post
            self.cursor.execute(insert_sql, (
                sec_uid, 
                cleaned_data["aweme_id"], 
                cleaned_data["nickname"], 
                cleaned_data["create_time"], 
                cleaned_data["desc"], 
                cleaned_data["uid"], 
                cleaned_data["owner_handle"],
                cleaned_data["comment_count"],
                cleaned_data["digg_count"],
                cleaned_data["collect_count"],
                cleaned_data["share_count"],
                json.dumps(data)
            ))
        
            # 插入或更新 creators
            self.cursor.execute(upsert_creator_sql, (
                cleaned_data["uid"],
                sec_uid,
                cleaned_data["nickname"],
                cleaned_data["owner_handle"]
            ))
        
            self.conn.commit()
        except Exception as e:
            pass

    def create_user_like_table(self):
        sql = """CREATE TABLE if not exists t_user_like (
                        id integer primary key autoincrement,
                        sec_uid varchar(200),
                        aweme_id integer unique,
                        rawdata json
                    );"""

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            pass

    def get_user_like(self, sec_uid: str, aweme_id: int):
        sql = """select id, sec_uid, aweme_id, rawdata from t_user_like where sec_uid=? and aweme_id=?;"""

        try:
            self.cursor.execute(sql, (sec_uid, aweme_id))
            self.conn.commit()
            res = self.cursor.fetchone()
            return res
        except Exception as e:
            pass

    def insert_user_like(self, sec_uid: str, aweme_id: int, data: dict):
        insertsql = """insert into t_user_like (sec_uid, aweme_id, rawdata) values(?,?,?);"""

        try:
            self.cursor.execute(insertsql, (sec_uid, aweme_id, json.dumps(data)))
            self.conn.commit()
        except Exception as e:
            pass

    def create_mix_table(self):
        sql = """CREATE TABLE if not exists t_mix (
                        id integer primary key autoincrement,
                        sec_uid varchar(200),
                        mix_id varchar(200),
                        aweme_id integer,
                        rawdata json
                    );"""

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            pass

    def get_mix(self, sec_uid: str, mix_id: str, aweme_id: int):
        sql = """select id, sec_uid, mix_id, aweme_id, rawdata from t_mix where sec_uid=? and  mix_id=? and aweme_id=?;"""

        try:
            self.cursor.execute(sql, (sec_uid, mix_id, aweme_id))
            self.conn.commit()
            res = self.cursor.fetchone()
            return res
        except Exception as e:
            pass

    def insert_mix(self, sec_uid: str, mix_id: str, aweme_id: int, data: dict):
        insertsql = """insert into t_mix (sec_uid, mix_id, aweme_id, rawdata) values(?,?,?,?);"""

        try:
            self.cursor.execute(insertsql, (sec_uid, mix_id, aweme_id, json.dumps(data)))
            self.conn.commit()
        except Exception as e:
            pass

    def create_music_table(self):
        sql = """CREATE TABLE if not exists t_music (
                        id integer primary key autoincrement,
                        music_id varchar(200),
                        aweme_id integer unique,
                        rawdata json
                    );"""

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            pass

    def get_music(self, music_id: str, aweme_id: int):
        sql = """select id, music_id, aweme_id, rawdata from t_music where music_id=? and aweme_id=?;"""

        try:
            self.cursor.execute(sql, (music_id, aweme_id))
            self.conn.commit()
            res = self.cursor.fetchone()
            return res
        except Exception as e:
            pass

    def insert_music(self, music_id: str, aweme_id: int, data: dict):
        insertsql = """insert into t_music (music_id, aweme_id, rawdata) values(?,?,?);"""

        try:
            self.cursor.execute(insertsql, (music_id, aweme_id, json.dumps(data)))
            self.conn.commit()
        except Exception as e:
            pass


if __name__ == '__main__':
    pass
