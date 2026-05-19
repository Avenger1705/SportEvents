from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict
from enum import Enum


class RoleEnum(str, Enum):
    admin   = "admin"
    joueur  = "joueur"
    visitor = "visitor"


class RegisterRequest(BaseModel):
    nom:      str
    prenom:   str
    address:  str
    email:    EmailStr
    password: str
    role:     RoleEnum
    age:      Optional[int] = None
    height:   Optional[float] = None
    weight:   Optional[float] = None
    ranking:  Optional[str] = None
    mean_global_ranking: Optional[str] = None
    profile_image_base64: Optional[str] = None
    practice_sport: Optional[str] = None
    favorite_sports: Optional[List[str]] = None
    notify_sports: Optional[List[str]] = None

    @field_validator("nom")
    @classmethod
    def nom_min(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Le nom doit avoir au moins 2 caractères")
        return v.strip()

    @field_validator("prenom")
    @classmethod
    def prenom_min(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Le prénom doit avoir au moins 2 caractères")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Le mot de passe doit avoir au moins 6 caractères")
        return v

class AdminUserCreate(BaseModel):
    nom: str
    prenom: str
    username: str
    email: EmailStr
    password: str
    role: RoleEnum
    practice_sport: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    ranking: Optional[str] = None

class AdminUserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    practice_sport: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    ranking: Optional[str] = None
    password: Optional[str] = None


class ManagerRegisterRequest(BaseModel):
    username: str
    email:    EmailStr
    password: str
    admin_code: str

    @field_validator("username")
    @classmethod
    def username_min(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Le nom d'utilisateur doit avoir au moins 3 caractères")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Le mot de passe doit avoir au moins 6 caractères")
        return v


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp:   str


class ResendOTPRequest(BaseModel):
    email: EmailStr


class SetRoleRequest(BaseModel):
    role: RoleEnum


class ForgotPasswordRequest(BaseModel):
    username_or_email: str


class ResetPasswordRequest(BaseModel):
    username_or_email: str
    otp: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Le mot de passe doit avoir au moins 6 caractères")
        return v


class ChangeUnverifiedEmailRequest(BaseModel):
    old_email: EmailStr
    new_email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user_id:      int
    username:     str
    role:         Optional[str]
    is_verified:  bool


class MessageResponse(BaseModel):
    message: str
    email_masked: Optional[str] = None


class AthletePreferencesRequest(BaseModel):
    practice_sport:  str
    selected_sports: List[str]
    interest_levels: Dict[str, int]


class VisitorPreferencesRequest(BaseModel):
    favorite_sports: List[str]
    notify_sports: Optional[List[str]] = None


class UserProfile(BaseModel):
    id:          int
    username:    str
    email:       str
    nom:         Optional[str] = None
    prenom:      Optional[str] = None
    role:        Optional[str] = None
    is_verified: bool
    profile_image: Optional[str] = None
    age:         Optional[int] = None
    height:      Optional[float] = None
    weight:      Optional[float] = None
    ranking:     Optional[str] = None
    practice_sport: Optional[str] = None
    matches_played: Optional[int] = 0
    matches_won:    Optional[int] = 0
    matches_lost:   Optional[int] = 0

    model_config = {"from_attributes": True}


class EventCreate(BaseModel):
    title:       str
    description: Optional[str] = None
    sport:       Optional[str] = None
    location:    Optional[str] = None
    latitude:    Optional[float] = None
    longitude:   Optional[float] = None
    event_date:  Optional[str] = None
    event_time:  Optional[str] = None
    duration:    Optional[str] = None


class EventPhotoOut(BaseModel):
    id:         int
    photo_path: str

    model_config = {"from_attributes": True}


class EventOut(BaseModel):
    id:             int
    title:          str
    description:    Optional[str]
    sport:          Optional[str]
    location:       Optional[str]
    latitude:       Optional[float]
    longitude:      Optional[float]
    cover_photo:    Optional[str]
    event_date:     Optional[str]
    event_time:     Optional[str]
    duration:       Optional[str]
    organizer_id:   Optional[int]
    organizer_name: Optional[str] = None
    photos:         List[EventPhotoOut] = []

    model_config = {"from_attributes": True}


class TeamMemberIn(BaseModel):
    player_name:  str
    player_email: Optional[str] = None
    position:     Optional[str] = None
    jersey_number: Optional[int] = None
    user_id:      Optional[int] = None


class TeamCreate(BaseModel):
    name:    str
    sport:   str
    members: List[TeamMemberIn] = []


class TeamUpdate(BaseModel):
    name:    Optional[str] = None
    sport:   Optional[str] = None
    members: Optional[List[TeamMemberIn]] = None


class TournamentCreate(BaseModel):
    name:           str
    sport:          str
    description:    Optional[str] = None
    location:       Optional[str] = None
    start_date:     Optional[str] = None
    end_date:       Optional[str] = None
    match_duration: Optional[str] = None
    team_ids:       List[int] = []


class MatchUpdate(BaseModel):
    score_a:    Optional[int] = None
    score_b:    Optional[int] = None
    winner_id:  Optional[int] = None
    status:     Optional[str] = None
    match_date: Optional[str] = None
    match_time: Optional[str] = None
    location:   Optional[str] = None
    team_a_id:  Optional[int] = None
    team_b_id:  Optional[int] = None


class CommentCreate(BaseModel):
    content: str


class MatchCommentCreate(BaseModel):
    content: str


class BookingCreate(BaseModel):
    match_id: int


class MatchScheduleItem(BaseModel):
    match_id:   int
    match_date: Optional[str] = None   # ISO datetime string
    match_time: Optional[str] = None   # e.g. "14h30"
    location:   Optional[str] = None


class TournamentScheduleRequest(BaseModel):
    matches: List[MatchScheduleItem]


class ProfileUpdateRequest(BaseModel):
    profile_image_base64: Optional[str] = None


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr


class ConfirmEmailChangeRequest(BaseModel):
    new_email: EmailStr
    otp: str


class ChangePasswordRequest(BaseModel):
    old_password: Optional[str] = None
    otp: Optional[str] = None
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Le mot de passe doit avoir au moins 6 caractères")
        return v

# ── Comments ──────────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    content: str

class CommentUser(BaseModel):
    id: int
    username: str
    profile_image: Optional[str] = None

class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: str
    user: CommentUser

class MatchCommentCreate(BaseModel):
    content: str
    match_id: int

class EventCommentCreate(BaseModel):
    content: str
    event_id: int
