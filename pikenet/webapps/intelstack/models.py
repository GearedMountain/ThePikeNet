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

def getNoteById(noteId):
    try:
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
        WHERE
            n.id = :note_id
        GROUP BY
            n.id
        """)

        data = db.session.execute(sql, {"note_id":noteId})
        result = data.fetchone()
        print(f"note:")
        if result:
            # Unpack the result from the database row
            noteData = {
                'id': result[0],
                'title': result[1],
                'description': result[2],
                'created_at': result[3],
                'tags': result[4].split(', ') if result[4] else []
            }
            return noteData
        else:
            return "Note not found"

    except Exception as e:
        db.session.rollback()