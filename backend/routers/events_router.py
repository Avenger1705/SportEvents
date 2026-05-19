from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import os
import shutil
import uuid
import json

import models
import schemas
import auth_utils
import email_service
from database import get_db

router = APIRouter(prefix="/api/events", tags=["Events"])

_ROUTER_DIR  = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_ROUTER_DIR)
_ROOT_DIR    = os.path.dirname(_BACKEND_DIR)
UPLOAD_DIR   = os.path.join(_ROOT_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _save_upload(file: UploadFile) -> str:
    raw_name = file.filename or "upload"
    ext = os.path.splitext(raw_name)[-1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOAD_DIR, filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return filename


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[models.User]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = auth_utils.decode_token(token)
        user_id = int(payload["sub"])
        return db.get(models.User, user_id)
    except Exception:
        return None


def require_admin(user: Optional[models.User] = Depends(get_optional_user)) -> models.User:
    if not user:
        raise HTTPException(status_code=401, detail="Authentification requise")
    if str(user.role) not in ("admin", "RoleEnum.admin"):
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return user


def _event_dict(ev: models.Event) -> dict:
    return {
        "id":             ev.id,
        "title":          ev.title,
        "description":    ev.description,
        "sport":          ev.sport,
        "location":       ev.location,
        "latitude":       ev.latitude,
        "longitude":      ev.longitude,
        "cover_photo":    f"/uploads/{ev.cover_photo}" if ev.cover_photo else None,
        "event_date":     ev.event_date.isoformat() if ev.event_date else None,
        "event_time":     ev.event_time,
        "duration":       ev.duration,
        "organizer_id":   ev.organizer_id,
        "organizer_name": ev.organizer.username if ev.organizer else None,
        "photos": [
            {"id": p.id, "photo_path": f"/uploads/{p.photo_path}"}
            for p in ev.photos
        ],
    }


def _notify_subscribers(db: Session, event: models.Event):
    if not event.sport:
        return
    subscribers = db.query(models.SportInterest).filter(
        models.SportInterest.sport_name == event.sport,
        models.SportInterest.notify == True,
    ).all()

    for sub in subscribers:
        user = db.get(models.User, sub.user_id)
        if user and user.email:
            display = f"{user.prenom or ''} {user.nom or ''}".strip() or user.username
            date_str = event.event_date.strftime("%d/%m/%Y %H:%M") if event.event_date else None
            email_service.send_event_notification_email(
                user.email, display, event.title, event.sport,
                date_str, event.location or ""
            )


@router.get("", summary="Lister tous les événements")
def list_events(db: Session = Depends(get_db)):
    events = (
        db.query(models.Event)
        .order_by(models.Event.event_date.asc())
        .all()
    )
    return [_event_dict(ev) for ev in events]


@router.get("/{event_id}", summary="Détail d'un événement")
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.get(models.Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    return _event_dict(ev)


@router.post("", status_code=201, summary="Créer un événement (admin)")
async def create_event(
    title:          str           = Form(...),
    description:    Optional[str] = Form(None),
    sport:          Optional[str] = Form(None),
    location:       Optional[str] = Form(None),
    latitude:       Optional[float] = Form(None),
    longitude:      Optional[float] = Form(None),
    event_date:     Optional[str] = Form(None),
    event_time:     Optional[str] = Form(None),
    duration:       Optional[str] = Form(None),
    cover_photo:    Optional[UploadFile] = File(None),
    gallery_photos: List[UploadFile]    = File(default=[]),
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Le titre est requis")

    parsed_date = None
    if event_date:
        try:
            parsed_date = datetime.fromisoformat(event_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide (ISO attendu)")

    cover_filename = None
    if cover_photo and cover_photo.filename:
        cover_filename = _save_upload(cover_photo)

    ev = models.Event(
        title        = title.strip(),
        description  = description,
        sport        = sport or None,
        location     = location or None,
        latitude     = latitude,
        longitude    = longitude,
        cover_photo  = cover_filename,
        event_date   = parsed_date,
        event_time   = event_time,
        duration     = duration,
        organizer_id = admin.id,
    )
    db.add(ev)
    db.flush()

    for f in gallery_photos:
        if f and f.filename:
            fname = _save_upload(f)
            db.add(models.EventPhoto(event_id=ev.id, photo_path=fname))

    db.commit()
    db.refresh(ev)

    _notify_subscribers(db, ev)

    return _event_dict(ev)


@router.put("/{event_id}", summary="Modifier un événement (admin)")
async def update_event(
    event_id:       int,
    title:          Optional[str] = Form(None),
    description:    Optional[str] = Form(None),
    sport:          Optional[str] = Form(None),
    location:       Optional[str] = Form(None),
    latitude:       Optional[float] = Form(None),
    longitude:      Optional[float] = Form(None),
    event_date:     Optional[str] = Form(None),
    event_time:     Optional[str] = Form(None),
    duration:       Optional[str] = Form(None),
    cover_photo:    Optional[UploadFile] = File(None),
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ev = db.get(models.Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    if title is not None:
        ev.title = title.strip()
    if description is not None:
        ev.description = description
    if sport is not None:
        ev.sport = sport or None
    if location is not None:
        ev.location = location or None
    if latitude is not None:
        ev.latitude = latitude
    if longitude is not None:
        ev.longitude = longitude
    if event_date is not None:
        try:
            ev.event_date = datetime.fromisoformat(event_date) if event_date else None
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide")
    if event_time is not None:
        ev.event_time = event_time
    if duration is not None:
        ev.duration = duration

    if cover_photo and cover_photo.filename:
        ev.cover_photo = _save_upload(cover_photo)

    db.commit()
    db.refresh(ev)
    return _event_dict(ev)


@router.delete("/{event_id}", summary="Supprimer un événement (admin)")
def delete_event(
    event_id: int,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ev = db.get(models.Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    db.delete(ev)
    db.commit()
    return {"message": "Événement supprimé avec succès"}


@router.post("/{event_id}/photos", status_code=201, summary="Ajouter des photos (admin)")
async def add_event_photos(
    event_id: int,
    photos:   List[UploadFile] = File(...),
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ev = db.get(models.Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    added = []
    for f in photos:
        if f and f.filename:
            fname = _save_upload(f)
            photo = models.EventPhoto(event_id=ev.id, photo_path=fname)
            db.add(photo)
            added.append(fname)

    db.commit()
    return {"message": f"{len(added)} photo(s) ajoutée(s)", "added": added}


@router.delete("/{event_id}/photos/{photo_id}", summary="Supprimer une photo (admin)")
def delete_event_photo(
    event_id: int,
    photo_id: int,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ev = db.get(models.Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    photo = db.get(models.EventPhoto, photo_id)
    if not photo or photo.event_id != event_id:
        raise HTTPException(status_code=404, detail="Photo introuvable")

    db.delete(photo)
    db.commit()
    return {"message": "Photo supprimée"}
