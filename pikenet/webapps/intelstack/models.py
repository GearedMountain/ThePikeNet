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

def getMostRecent():
    """
    Retrieves the 10 most recently added notes along with their tags.

    Returns:
        list: A list of dictionaries, where each dictionary represents a note
              and its tags. Returns an empty list if no notes are found.
    """
    sql = text("""
        SELECT
            n.id,
            n.title,
            n.description,
            n.created_at,
            STRING_AGG(t.name, ', ') AS tags
        FROM
            notes AS n
        LEFT JOIN
            note_tags AS nt ON n.id = nt.note_id
        LEFT JOIN
            tags AS t ON nt.tag_id = t.id
        GROUP BY
            n.id
        ORDER BY
            n.created_at DESC
        LIMIT 10;
    """)

    data = db.session.execute(sql)
    
    notesList = []

    for row in data:
        note_data = {
            'id': row.id,
            'title': row.title,
            'description': row.description,
            'created_at': row.created_at,
            'tags': row.tags.split(', ') if row.tags else []
        }
        notesList.append(note_data)
    return notesList