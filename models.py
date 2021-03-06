"""SQLAlchemy models"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # Create database object

def connect_db(app):
  """Connect database to the Flask app"""

  db.app = app # Connect database to Flask object
  db.init_app(app) # Initialize database

class GuestUser(db.Model):
  """Guest user"""
  
  __tablename__ = 'guest_users'

  id = db.Column(db.Text, primary_key=True)
  phone_number = db.Column(db.Text, unique=True)
  active_playlist_id = db.Column(db.Text)
  user_type = db.Column(db.String(32), nullable=False)

  @property
  def active_playlist(self):
    return Playlist.query.filter_by(id=self.active_playlist_id).first()

  __mapper_args__ = {
    "polymorphic_identity": "guest_users",
    "polymorphic_on": user_type,
  }
  
class HostUser(GuestUser):
  """ A host user is associated with a spotify account
  Playlists are stored on their account"""

  __tablename__ = 'host_users'

  id = db.Column(db.Text, db.ForeignKey('guest_users.id'), primary_key=True)
  display_name = db.Column(db.Text, nullable=False)
  email = db.Column(db.Text, nullable=False, unique=True)
  url = db.Column(db.Text, nullable=False)
  access_token = db.Column(db.Text)
  refresh_token = db.Column(db.Text)

  playlists = db.relationship('Playlist', backref='owner', cascade='all, delete-orphan')

  @property
  def auth_header(self):
    """Create the authorization header from the acccess token. Return as a python dictionary"""

    return {'Authorization': f'Bearer {self.access_token}'}

  __mapper_args__ = {"polymorphic_identity": "host_users"}


class Playlist(db.Model):
  """Playlist"""

  __tablename__ = 'playlists'

  id = db.Column(db.Text, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  key = db.Column(db.Text, unique=True, nullable=False)
  url = db.Column(db.Text, nullable=False)
  endpoint = db.Column(db.Text, nullable=False)

  owner_id = db.Column(db.Text, db.ForeignKey('host_users.id'), nullable=False)
  
  tracks = db.relationship(
    'Track',
    secondary="playlist_tracks",
    cascade="all, delete",
    backref="playlists"
  )

class PlaylistTrack(db.Model):
  """A track in a playlist that was added by someone with a text message"""

  __tablename__ = "playlist_tracks"

  playlist_id = db.Column(db.Text, db.ForeignKey('playlists.id'), primary_key=True)
  track_id = db.Column(db.Text, db.ForeignKey('tracks.id'), primary_key=True)
  added_by = db.Column(db.Text)


class Track(db.Model):
  """Track"""

  __tablename__ = 'tracks'

  id = db.Column(db.Text, primary_key=True)
  name = db.Column(db.Text, nullable=False)
  artist = db.Column(db.Text, nullable=False)
  
  # @property
  def added_by(self, playlist):
    playlist_track = PlaylistTrack.query.filter_by(track_id=self.id,playlist_id=playlist.id).first()
    if playlist_track:
      return playlist_track.added_by
