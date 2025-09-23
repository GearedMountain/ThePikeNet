from pikenet.utils.database import db
from sqlalchemy import text

def addNote(title):
    sql= text("""
        INSERT INTO notes (title, description)
        VALUES (:title, :description)
        RETURNING id
        """)
    
    result = db.session.execute(sql, {
            "title": title,
            "description": ""
    })
    db.session.commit()
    return result.scalar()