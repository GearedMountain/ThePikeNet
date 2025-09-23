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

def addTag(tagName, noteId):
    tagName = tagName.lower()
    try:
        # SQL statement with ON CONFLICT DO NOTHING to handle duplicates
        sql= text("""
            INSERT INTO tags (name) VALUES (:tagName)
            ON CONFLICT (name) DO NOTHING;
        """)

        db.session.execute(sql, {
            "tagName" : tagName.strip()
            })
        db.session.commit()

        # SQL statement to get the tag's ID, regardless of whether it was inserted
        sql = text("""
            SELECT id FROM tags WHERE name = :tagName;
        """)

        result = db.session.execute(sql, {
            "tagName" : tagName.strip()
            })
        
        tagId = result.fetchone()
        

        # If note ID is also provided, add the tag to the note
        if noteId:
            sql= text("""
                INSERT INTO note_tags (note_id, tag_id) VALUES (:noteId, :tagId)
            """)
            print(f"Got tagid {noteId}")

            db.session.execute(sql, {
                "noteId" : noteId,
                "tagId" : tagId[0]
            })
            
            db.session.commit()
        return "Success"

    except Exception as e:
        print(e)
        db.session.rollback()
        return "Fail"
    
def getAllTags():
    sql= text(""" SELECT * FROM tags; """)
    result = db.session.execute(sql) 
    rows = result.all()   
    data = [dict(row._mapping) for row in rows]
    return data