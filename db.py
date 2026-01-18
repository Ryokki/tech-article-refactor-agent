# agent/db.py

"""
PostgreSQL 数据库模块

符合 Python 最佳实践：
- 使用连接池 (psycopg2.pool)
- 上下文管理器自动管理连接
- 参数化查询防止 SQL 注入
- 完整的错误处理
"""

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """数据库配置，从环境变量读取"""

    @staticmethod
    def get_config() -> dict:
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "database": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "kkbabe"),
            "password": os.getenv("DB_PASSWORD", ""),
            "minconn": int(os.getenv("DB_POOL_MIN", 1)),
            "maxconn": int(os.getenv("DB_POOL_MAX", 10)),
        }


class ConnectionPool:
    """PostgreSQL 连接池单例"""

    _instance: Optional[pool.ThreadedConnectionPool] = None
    _config: Optional[dict] = None

    @classmethod
    def initialize(cls, config: Optional[dict] = None):
        """初始化连接池"""
        if cls._instance is None:
            cls._config = config or DatabaseConfig.get_config()
            try:
                cls._instance = pool.ThreadedConnectionPool(
                    minconn=cls._config["minconn"],
                    maxconn=cls._config["maxconn"],
                    host=cls._config["host"],
                    port=cls._config["port"],
                    database=cls._config["database"],
                    user=cls._config["user"],
                    password=cls._config["password"],
                )
            except Exception as e:
                print(f"Error initializing connection pool: {e}")
                raise

    @classmethod
    def get_pool(cls) -> pool.ThreadedConnectionPool:
        """获取连接池实例"""
        if cls._instance is None:
            cls.initialize()
        return cls._instance

    @classmethod
    def close_all(cls):
        """关闭所有连接"""
        if cls._instance:
            cls._instance.closeall()
            cls._instance = None


@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor):
    """
    获取数据库游标的上下文管理器
    自动处理事务提交/回滚和连接归还
    """
    pool = ConnectionPool.get_pool()
    conn = pool.getconn()
    try:
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


class OptimizationLogRepository:
    """文章优化记录数据访问层"""

    TABLE_NAME = "article_optimization_logs"

    @classmethod
    def init_table(cls):
        """初始化表结构"""
        with get_db_cursor() as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    original_content TEXT NOT NULL,
                    analyst_prompt TEXT,
                    analyst_result TEXT,
                    architect_prompt TEXT,
                    architect_result TEXT,
                    writer_prompt TEXT,
                    writer_result TEXT,
                    evaluation TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 创建索引提高查询性能
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{cls.TABLE_NAME}_created_at
                ON {cls.TABLE_NAME}(created_at DESC)
            """)

    @classmethod
    def insert(cls,
               original_content: str,
               analyst_prompt: str,
               analyst_result: str,
               architect_prompt: str,
               architect_result: str,
               writer_prompt: str,
               writer_result: str,
               evaluation: str = None) -> int:
        """
        插入一条优化记录
        """
        with get_db_cursor() as cur:
            cur.execute(f"""
                INSERT INTO {cls.TABLE_NAME} (
                    original_content,
                    analyst_prompt, analyst_result,
                    architect_prompt, architect_result,
                    writer_prompt, writer_result,
                    evaluation, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                original_content,
                analyst_prompt, analyst_result,
                architect_prompt, architect_result,
                writer_prompt, writer_result,
                evaluation, datetime.utcnow()
            ))
            # fetchone() returns a RealDictRow which acts like a dict
            result = cur.fetchone()
            return result["id"]

    @classmethod
    def find_by_id(cls, record_id: int) -> Optional[Dict[str, Any]]:
        """根据 ID 查询记录"""
        with get_db_cursor() as cur:
            cur.execute(f"""
                SELECT *
                FROM {cls.TABLE_NAME}
                WHERE id = %s
            """, (record_id,))
            return cur.fetchone()

    @classmethod
    def find_all(cls, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """查询所有记录，按时间倒序"""
        with get_db_cursor() as cur:
            cur.execute(f"""
                SELECT *
                FROM {cls.TABLE_NAME}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            return cur.fetchall()

    @classmethod
    def count(cls) -> int:
        """获取记录总数"""
        with get_db_cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as count FROM {cls.TABLE_NAME}")
            return cur.fetchone()["count"]


# 初始化时自动创建表
try:
    OptimizationLogRepository.init_table()
except Exception as e:
    print(f"Warning: Failed to initialize database table: {e}")
