"""
Módulo de Banco de Dados para Métricas e Estatísticas

Armazena histórico de gerações, uploads e estatísticas do sistema.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from loguru import logger
import json

from ..config import settings


class Database:
    """Banco de dados SQLite para métricas"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Usa caminho absoluto baseado no diretório atual
            base_dir = Path(__file__).parent.parent.parent
            self.db_path = base_dir / "config" / "metrics.db"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
        logger.info(f"Database inicializado: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Obtém conexão com o banco"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Cria tabelas do banco"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabela de gerações de conteúdo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                noticia_titulo TEXT,
                noticia_fonte TEXT,
                roteiro_completo TEXT,
                modelo_ia TEXT,
                tokens_usados INTEGER,
                audio_path TEXT,
                audio_duracao REAL,
                video_path TEXT,
                video_duracao REAL,
                status TEXT,
                erro TEXT
            )
        """)

        # Tabela de uploads
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                video_path TEXT NOT NULL,
                video_titulo TEXT,
                tiktok_video_id TEXT,
                status TEXT,
                erro TEXT,
                agendado_para TEXT,
                visualizacoes INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comentarios INTEGER DEFAULT 0,
                compartilhamentos INTEGER DEFAULT 0
            )
        """)

        # Tabela de configurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)

        # Tabela de logs de atividade
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                level TEXT DEFAULT 'INFO'
            )
        """)

        # Índices para performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_generations_timestamp 
            ON content_generations(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_uploads_timestamp 
            ON uploads(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_timestamp 
            ON activity_logs(timestamp)
        """)

        conn.commit()
        conn.close()

    # =============================================================================
    # CONTENT GENERATIONS
    # =============================================================================

    def save_generation(self, data: Dict[str, Any]) -> int:
        """Salva uma geração de conteúdo"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO content_generations (
                timestamp, noticia_titulo, noticia_fonte, roteiro_completo,
                modelo_ia, tokens_usados, audio_path, audio_duracao,
                video_path, video_duracao, status, erro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("timestamp", datetime.now().isoformat()),
            data.get("noticia_titulo", ""),
            data.get("noticia_fonte", ""),
            data.get("roteiro_completo", ""),
            data.get("modelo_ia", ""),
            data.get("tokens_usados", 0),
            data.get("audio_path", ""),
            data.get("audio_duracao", 0),
            data.get("video_path", ""),
            data.get("video_duracao", 0),
            data.get("status", "pending"),
            data.get("erro", ""),
        ))

        generation_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.log_activity("generation_saved", {"id": generation_id})
        return generation_id

    def get_generations(
        self,
        limit: int = 50,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Obtém gerações recentes"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT * FROM content_generations
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (cutoff_date, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    # =============================================================================
    # UPLOADS
    # =============================================================================

    def save_upload(self, data: Dict[str, Any]) -> int:
        """Salva um upload"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO uploads (
                timestamp, video_path, video_titulo, tiktok_video_id,
                status, erro, agendado_para
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("timestamp", datetime.now().isoformat()),
            data.get("video_path", ""),
            data.get("video_titulo", ""),
            data.get("tiktok_video_id", ""),
            data.get("status", "pending"),
            data.get("erro", ""),
            data.get("agendado_para"),
        ))

        upload_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.log_activity("upload_saved", {"id": upload_id})
        return upload_id

    def update_upload_stats(
        self,
        upload_id: int,
        visualizacoes: int = None,
        likes: int = None,
        comentarios: int = None,
        compartilhamentos: int = None,
    ):
        """Atualiza estatísticas de um upload"""
        conn = self._get_connection()
        cursor = conn.cursor()

        updates = []
        values = []

        if visualizacoes is not None:
            updates.append("visualizacoes = ?")
            values.append(visualizacoes)
        if likes is not None:
            updates.append("likes = ?")
            values.append(likes)
        if comentarios is not None:
            updates.append("comentarios = ?")
            values.append(comentarios)
        if compartilhamentos is not None:
            updates.append("compartilhamentos = ?")
            values.append(compartilhamentos)

        if updates:
            values.append(upload_id)
            cursor.execute(f"""
                UPDATE uploads
                SET {', '.join(updates)}
                WHERE id = ?
            """, values)

            conn.commit()

        conn.close()

    def get_uploads(
        self,
        limit: int = 50,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Obtém uploads recentes"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT * FROM uploads
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (cutoff_date, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    # =============================================================================
    # SETTINGS
    # =============================================================================

    def save_setting(self, key: str, value: str):
        """Salva uma configuração"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_setting(self, key: str) -> Optional[str]:
        """Obtém uma configuração"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()

        return row["value"] if row else None

    def get_all_settings(self) -> Dict[str, str]:
        """Obtém todas as configurações"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT key, value FROM settings")
        results = {row["key"]: row["value"] for row in cursor.fetchall()}
        conn.close()

        return results

    # =============================================================================
    # ACTIVITY LOGS
    # =============================================================================

    def log_activity(self, event_type: str, event_data: Dict, level: str = "INFO"):
        """Registra uma atividade"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO activity_logs (timestamp, event_type, event_data, level)
            VALUES (?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            event_type,
            json.dumps(event_data),
            level,
        ))

        conn.commit()
        conn.close()

    def get_activity_logs(
        self,
        limit: int = 100,
        level: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Obtém logs de atividade"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if level:
            cursor.execute("""
                SELECT * FROM activity_logs
                WHERE level = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (level, limit))
        else:
            cursor.execute("""
                SELECT * FROM activity_logs
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

        results = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            try:
                row_dict["event_data"] = json.loads(row_dict["event_data"])
            except:
                pass
            results.append(row_dict)

        conn.close()
        return results

    # =============================================================================
    # STATISTICS & ANALYTICS
    # =============================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas gerais do sistema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        # Total de gerações
        cursor.execute("SELECT COUNT(*) FROM content_generations")
        stats["total_geracoes"] = cursor.fetchone()[0]

        # Total de uploads
        cursor.execute("SELECT COUNT(*) FROM uploads")
        stats["total_uploads"] = cursor.fetchone()[0]

        # Uploads com sucesso
        cursor.execute("SELECT COUNT(*) FROM uploads WHERE status = 'success'")
        stats["uploads_sucesso"] = cursor.fetchone()[0]

        # Uploads com erro
        cursor.execute("SELECT COUNT(*) FROM uploads WHERE status = 'error'")
        stats["uploads_erro"] = cursor.fetchone()[0]

        # Gerações hoje
        hoje = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM content_generations
            WHERE timestamp LIKE ?
        """, (f"{hoje}%",))
        stats["geracoes_hoje"] = cursor.fetchone()[0]

        # Uploads hoje
        cursor.execute("""
            SELECT COUNT(*) FROM uploads
            WHERE timestamp LIKE ?
        """, (f"{hoje}%",))
        stats["uploads_hoje"] = cursor.fetchone()[0]

        # Total de visualizações (soma de todos os vídeos)
        cursor.execute("SELECT COALESCE(SUM(visualizacoes), 0) FROM uploads")
        stats["total_visualizacoes"] = cursor.fetchone()[0]

        # Total de likes
        cursor.execute("SELECT COALESCE(SUM(likes), 0) FROM uploads")
        stats["total_likes"] = cursor.fetchone()[0]

        # Última geração
        cursor.execute("""
            SELECT timestamp, noticia_titulo FROM content_generations
            ORDER BY timestamp DESC LIMIT 1
        """)
        row = cursor.fetchone()
        stats["ultima_geracao"] = {
            "timestamp": row["timestamp"] if row else None,
            "noticia": row["noticia_titulo"] if row else None,
        } if row else None

        # Último upload
        cursor.execute("""
            SELECT timestamp, video_titulo, status FROM uploads
            ORDER BY timestamp DESC LIMIT 1
        """)
        row = cursor.fetchone()
        stats["ultimo_upload"] = {
            "timestamp": row["timestamp"] if row else None,
            "titulo": row["video_titulo"] if row else None,
            "status": row["status"] if row else None,
        } if row else None

        # Média de duração de vídeos
        cursor.execute("""
            SELECT AVG(video_duracao) FROM content_generations
            WHERE video_duracao > 0
        """)
        stats["media_duracao_videos"] = round(cursor.fetchone()[0] or 0, 2)

        # Modelo de IA mais usado
        cursor.execute("""
            SELECT modelo_ia, COUNT(*) as count FROM content_generations
            WHERE modelo_ia != ''
            GROUP BY modelo_ia
            ORDER BY count DESC LIMIT 1
        """)
        row = cursor.fetchone()
        stats["modelo_ia_mais_usado"] = row["modelo_ia"] if row else "N/A"

        # Fontes de notícias mais usadas
        cursor.execute("""
            SELECT noticia_fonte, COUNT(*) as count FROM content_generations
            WHERE noticia_fonte != ''
            GROUP BY noticia_fonte
            ORDER BY count DESC LIMIT 5
        """)
        stats["fontes_mais_usadas"] = [
            {"fonte": row["noticia_fonte"], "count": row["count"]}
            for row in cursor.fetchall()
        ]

        # Gerações por dia (últimos 7 dias)
        cursor.execute("""
            SELECT DATE(timestamp) as data, COUNT(*) as count
            FROM content_generations
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY data
        """)
        stats["geracoes_por_dia"] = [
            {"data": row["data"], "count": row["count"]}
            for row in cursor.fetchall()
        ]

        # Uploads por dia (últimos 7 dias)
        cursor.execute("""
            SELECT DATE(timestamp) as data, COUNT(*) as count
            FROM uploads
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY data
        """)
        stats["uploads_por_dia"] = [
            {"data": row["data"], "count": row["count"]}
            for row in cursor.fetchall()
        ]

        conn.close()
        return stats

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtém dados completos para o dashboard"""
        stats = self.get_statistics()
        recent_generations = self.get_generations(limit=10)
        recent_uploads = self.get_uploads(limit=10)
        recent_logs = self.get_activity_logs(limit=20)

        return {
            "statistics": stats,
            "recent_generations": recent_generations,
            "recent_uploads": recent_uploads,
            "recent_logs": recent_logs,
            "timestamp": datetime.now().isoformat(),
        }

    def reset_database(self):
        """Reseta todo o banco de dados (cuidado!)"""
        self.db_path.unlink(missing_ok=True)
        self._create_tables()
        logger.warning("Database resetado!")


# Instância global
db = Database()
