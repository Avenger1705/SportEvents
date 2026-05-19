from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text, SmallInteger, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class RoleEnum(str, enum.Enum):
    admin   = "admin"
    joueur  = "joueur"
    visitor = "visitor"


class MatchStatusEnum(str, enum.Enum):
    a_venir   = "a_venir"
    en_cours  = "en_cours"
    termine   = "termine"
    reporte   = "reporte"


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    nom             = Column(String(100), nullable=True)
    prenom          = Column(String(100), nullable=True)
    address         = Column(String(255), nullable=True)
    username        = Column(String(50),  unique=True, nullable=False, index=True)
    email           = Column(String(100), unique=True, nullable=False, index=True)
    password_hash   = Column(String(255), nullable=False)
    role            = Column(Enum(RoleEnum), nullable=True)
    is_verified     = Column(Boolean, default=False)
    otp_code        = Column(String(6),   nullable=True)
    otp_expires_at  = Column(DateTime,    nullable=True)
    created_at      = Column(DateTime,    default=datetime.utcnow)

    age                 = Column(Integer, nullable=True)
    height              = Column(Float, nullable=True)
    weight              = Column(Float, nullable=True)
    ranking             = Column(String(50), nullable=True)
    mean_global_ranking = Column(String(50), nullable=True)
    profile_image       = Column(String(255), nullable=True)
    practice_sport      = Column(String(100), nullable=True)

    matches_played = Column(Integer, default=0)
    matches_won    = Column(Integer, default=0)
    matches_lost   = Column(Integer, default=0)

    athlete_pref    = relationship("AthletePreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sport_interests = relationship("SportInterest",     back_populates="user",                cascade="all, delete-orphan")
    visitor_pref    = relationship("VisitorPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    events          = relationship("Event",             back_populates="organizer",           cascade="all, delete-orphan")
    team_memberships = relationship("TeamMember",       back_populates="user",                cascade="all, delete-orphan")
    bookings        = relationship("Booking",           back_populates="user",                cascade="all, delete-orphan")
    comments        = relationship("Comment",           back_populates="user",                cascade="all, delete-orphan")
    match_comments  = relationship("MatchComment",      back_populates="user",                cascade="all, delete-orphan")


class AthletePreference(Base):
    __tablename__ = "athlete_preferences"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    practice_sport = Column(String(100), nullable=False)

    user = relationship("User", back_populates="athlete_pref")


class SportInterest(Base):
    __tablename__ = "sport_interests"

    id             = Column(Integer,     primary_key=True, index=True)
    user_id        = Column(Integer,     ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sport_name     = Column(String(100), nullable=False)
    interest_level = Column(SmallInteger, nullable=False, default=3)
    notify         = Column(Boolean, default=False)

    user = relationship("User", back_populates="sport_interests")


class VisitorPreference(Base):
    __tablename__ = "visitor_preferences"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    favorite_sports = Column(Text, nullable=True)

    user = relationship("User", back_populates="visitor_pref")


class Event(Base):
    __tablename__ = "events"

    id           = Column(Integer,      primary_key=True, index=True)
    title        = Column(String(200),  nullable=False)
    description  = Column(Text,         nullable=True)
    sport        = Column(String(100),  nullable=True)
    location     = Column(String(200),  nullable=True)
    latitude     = Column(Float,        nullable=True)
    longitude    = Column(Float,        nullable=True)
    cover_photo  = Column(String(255),  nullable=True)
    event_date   = Column(DateTime,     nullable=True)
    event_time   = Column(String(50),   nullable=True)
    duration     = Column(String(50),   nullable=True)
    organizer_id = Column(Integer,      ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at   = Column(DateTime,     default=datetime.utcnow)

    organizer = relationship("User", back_populates="events")
    photos    = relationship("EventPhoto", back_populates="event", cascade="all, delete-orphan")
    comments  = relationship("Comment", back_populates="event", cascade="all, delete-orphan")


class EventPhoto(Base):
    __tablename__ = "event_photos"

    id         = Column(Integer,     primary_key=True, index=True)
    event_id   = Column(Integer,     ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    photo_path = Column(String(255), nullable=False)

    event = relationship("Event", back_populates="photos")


class Team(Base):
    __tablename__ = "teams"

    id         = Column(Integer,     primary_key=True, index=True)
    name       = Column(String(200), nullable=False)
    sport      = Column(String(100), nullable=False)
    logo       = Column(String(255), nullable=True)
    created_at = Column(DateTime,    default=datetime.utcnow)
    created_by = Column(Integer,     ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    members          = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    tournament_teams = relationship("TournamentTeam", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"

    id        = Column(Integer, primary_key=True, index=True)
    team_id   = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id   = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    player_name  = Column(String(100), nullable=False)
    player_email = Column(String(100), nullable=True)
    position     = Column(String(50),  nullable=True)
    jersey_number = Column(Integer, nullable=True)

    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")


class Tournament(Base):
    __tablename__ = "tournaments"

    id            = Column(Integer,     primary_key=True, index=True)
    name          = Column(String(200), nullable=False)
    sport         = Column(String(100), nullable=False)
    description   = Column(Text,        nullable=True)
    location      = Column(String(200), nullable=True)
    start_date    = Column(DateTime,    nullable=True)
    end_date      = Column(DateTime,    nullable=True)
    match_duration = Column(String(50), nullable=True)
    status        = Column(String(20),  default="a_venir")
    cover_photo   = Column(String(255), nullable=True)
    created_by    = Column(Integer,     ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at    = Column(DateTime,    default=datetime.utcnow)

    teams   = relationship("TournamentTeam", back_populates="tournament", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="tournament", cascade="all, delete-orphan")


class TournamentTeam(Base):
    __tablename__ = "tournament_teams"

    id            = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    team_id       = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    seed          = Column(Integer, nullable=True)

    tournament = relationship("Tournament", back_populates="teams")
    team       = relationship("Team", back_populates="tournament_teams")


class Match(Base):
    __tablename__ = "matches"

    id              = Column(Integer, primary_key=True, index=True)
    tournament_id   = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    round_number    = Column(Integer, nullable=False)
    match_order     = Column(Integer, nullable=False)
    team_a_id       = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    team_b_id       = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    score_a         = Column(Integer, nullable=True)
    score_b         = Column(Integer, nullable=True)
    winner_id       = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    match_date      = Column(DateTime, nullable=True)
    match_time      = Column(String(50), nullable=True)
    location        = Column(String(200), nullable=True)
    status          = Column(Enum(MatchStatusEnum), default=MatchStatusEnum.a_venir)
    played_at       = Column(DateTime, nullable=True)

    tournament = relationship("Tournament", back_populates="matches")
    team_a     = relationship("Team", foreign_keys=[team_a_id])
    team_b     = relationship("Team", foreign_keys=[team_b_id])
    winner     = relationship("Team", foreign_keys=[winner_id])
    bookings   = relationship("Booking",      back_populates="match", cascade="all, delete-orphan")
    comments   = relationship("MatchComment", back_populates="match", cascade="all, delete-orphan")


class Booking(Base):
    __tablename__ = "bookings"

    id         = Column(Integer,     primary_key=True, index=True)
    user_id    = Column(Integer,     ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_id   = Column(Integer,     ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    qr_code    = Column(String(255), nullable=True)
    booked_at  = Column(DateTime,    default=datetime.utcnow)

    user  = relationship("User", back_populates="bookings")
    match = relationship("Match", back_populates="bookings")


class Comment(Base):
    __tablename__ = "comments"

    id         = Column(Integer,  primary_key=True, index=True)
    event_id   = Column(Integer,  ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(Integer,  ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content    = Column(Text,     nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="comments")
    user  = relationship("User", back_populates="comments")


class MatchComment(Base):
    __tablename__ = "match_comments"

    id         = Column(Integer,  primary_key=True, index=True)
    match_id   = Column(Integer,  ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(Integer,  ForeignKey("users.id",   ondelete="CASCADE"), nullable=False)
    content    = Column(Text,     nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="comments")
    user  = relationship("User",  back_populates="match_comments")
