from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
from jose import JWTError
import json
import shutil
import uuid
import os
import base64
from typing import Optional

import models
import schemas
import auth_utils
import email_service
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    try:
        payload  = auth_utils.decode_token(token)
        user_id  = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    return user


@router.post("/register", response_model=schemas.MessageResponse, status_code=201)
def register(req: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    base_username = f"{req.prenom.lower()}.{req.nom.lower()}".replace(" ", "")
    username = base_username
    counter = 1
    while db.query(models.User).filter(models.User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    filename = None
    if req.profile_image_base64:
        os.makedirs("photos", exist_ok=True)
        header, encoded = req.profile_image_base64.split(",", 1) if "," in req.profile_image_base64 else ("", req.profile_image_base64)
        ext = "jpg"
        if "png" in header:
            ext = "png"
        elif "jpeg" in header or "jpg" in header:
            ext = "jpg"

        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join("photos", filename)
        encoded = encoded + '=' * (-len(encoded) % 4)
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(encoded))

    otp  = auth_utils.generate_otp()
    user = models.User(
        nom            = req.nom,
        prenom         = req.prenom,
        address        = req.address,
        username       = username,
        email          = req.email,
        password_hash  = auth_utils.hash_password(req.password),
        role           = req.role,
        otp_code       = otp,
        otp_expires_at = auth_utils.otp_expiry(),
        age            = req.age if req.role == schemas.RoleEnum.joueur else None,
        height         = req.height if req.role == schemas.RoleEnum.joueur else None,
        weight         = req.weight if req.role == schemas.RoleEnum.joueur else None,
        ranking        = req.ranking if req.role == schemas.RoleEnum.joueur else None,
        mean_global_ranking = req.mean_global_ranking if req.role == schemas.RoleEnum.joueur else None,
        practice_sport = req.practice_sport if req.role == schemas.RoleEnum.joueur else None,
        profile_image  = filename,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if req.role == schemas.RoleEnum.visitor and req.notify_sports:
        for sport in req.notify_sports:
            db.add(models.SportInterest(user_id=user.id, sport_name=sport, interest_level=3, notify=True))
        db.commit()

    if req.role == schemas.RoleEnum.visitor and req.favorite_sports:
        db.query(models.VisitorPreference).filter_by(user_id=user.id).delete()
        db.add(models.VisitorPreference(
            user_id=user.id,
            favorite_sports=json.dumps(req.favorite_sports, ensure_ascii=False),
        ))
        db.commit()

    display_name = f"{req.prenom} {req.nom}"
    if not email_service.send_otp_email(req.email, display_name, otp):
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=500, detail="Erreur d'envoi d'email. Réessayez.")

    return {"message": "Compte créé ! Consultez votre email pour le code OTP."}


@router.post("/register-manager", response_model=schemas.MessageResponse, status_code=201)
def register_manager(req: schemas.ManagerRegisterRequest, db: Session = Depends(get_db)):
    ADMIN_SECRET = os.getenv("ADMIN_SECRET", "ADMIN2026")
    if req.admin_code != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Code administrateur invalide")

    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if db.query(models.User).filter(models.User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    user = models.User(
        username       = req.username,
        email          = req.email,
        password_hash  = auth_utils.hash_password(req.password),
        role           = schemas.RoleEnum.admin,
        is_verified    = True,
    )
    db.add(user)
    db.commit()

    return {"message": "Compte Admin créé avec succès. L'utilisateur peut maintenant se connecter."}


@router.post("/verify-otp", response_model=schemas.TokenResponse)
def verify_otp(req: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Aucun compte trouvé pour cet email")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Ce compte est déjà vérifié")
    if not user.otp_code or user.otp_code != req.otp.strip():
        raise HTTPException(status_code=400, detail="Code OTP incorrect")
    if user.otp_expires_at and datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Code OTP expiré. Demandez-en un nouveau.")

    user.is_verified   = True
    user.otp_code      = None
    user.otp_expires_at = None
    db.commit()

    token = auth_utils.create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type":   "bearer",
        "user_id":      user.id,
        "username":     user.username,
        "role":         user.role,
        "is_verified":  True,
    }


@router.post("/resend-otp", response_model=schemas.MessageResponse)
def resend_otp(req: schemas.ResendOTPRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Aucun compte trouvé pour cet email")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Compte déjà vérifié")

    otp = auth_utils.generate_otp()
    user.otp_code       = otp
    user.otp_expires_at = auth_utils.otp_expiry()
    db.commit()

    display_name = f"{user.prenom or ''} {user.nom or ''}".strip() or user.username
    if not email_service.send_otp_email(user.email, display_name, otp):
        raise HTTPException(status_code=500, detail="Erreur d'envoi d'email. Réessayez.")

    return {"message": "Nouveau code OTP envoyé !"}


@router.post("/login", response_model=schemas.TokenResponse)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        (models.User.email == req.username_or_email) | (models.User.username == req.username_or_email)
    ).first()
    if not user or not auth_utils.verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe incorrect")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Compte non vérifié. Vérifiez votre email.")

    token = auth_utils.create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type":   "bearer",
        "user_id":      user.id,
        "username":     user.username,
        "role":         user.role,
        "is_verified":  user.is_verified,
    }


@router.post("/forgot-password", response_model=schemas.MessageResponse)
def forgot_password(req: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        (models.User.email == req.username_or_email) | (models.User.username == req.username_or_email)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Aucun compte trouvé.")

    otp = auth_utils.generate_otp()
    user.otp_code = otp
    user.otp_expires_at = auth_utils.otp_expiry()
    db.commit()

    display_name = f"{user.prenom or ''} {user.nom or ''}".strip() or user.username
    email_service.send_otp_email(user.email, display_name, otp)

    try:
        if "@" in req.username_or_email:
            email_masked = user.email
        else:
            name, domain = user.email.split('@')
            if len(name) <= 3:
                masked_name = name[0] + "****"
            else:
                masked_name = name[:2] + "****" + name[-2:]
            email_masked = f"{masked_name}@{domain}"
    except Exception:
        email_masked = user.email

    return {"message": "Un code OTP a été envoyé.", "email_masked": email_masked}


@router.post("/reset-password", response_model=schemas.MessageResponse)
def reset_password(req: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        (models.User.email == req.username_or_email) | (models.User.username == req.username_or_email)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="Identifiant ou code incorrect")

    if not user.otp_code or user.otp_code != req.otp.strip():
        raise HTTPException(status_code=400, detail="Code OTP incorrect")
    if user.otp_expires_at and datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Code OTP expiré")

    user.password_hash = auth_utils.hash_password(req.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    return {"message": "Votre mot de passe a été réinitialisé."}


@router.post("/change-unverified-email", response_model=schemas.MessageResponse)
def change_unverified_email(req: schemas.ChangeUnverifiedEmailRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.old_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Ce compte est déjà vérifié")

    existing = db.query(models.User).filter(models.User.email == req.new_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Le nouvel email est déjà utilisé")

    otp = auth_utils.generate_otp()
    user.email = req.new_email
    user.otp_code = otp
    user.otp_expires_at = auth_utils.otp_expiry()
    db.commit()

    display_name = f"{user.prenom or ''} {user.nom or ''}".strip() or user.username
    if not email_service.send_otp_email(user.email, display_name, otp):
        raise HTTPException(status_code=500, detail="Erreur d'envoi d'email.")

    return {"message": "Email mis à jour et nouveau code envoyé !"}


@router.post("/set-role", response_model=schemas.MessageResponse)
def set_role(
    req: schemas.SetRoleRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.role = req.role
    db.commit()
    return {"message": f"Rôle défini : {req.role}"}


@router.post("/athlete-preferences", response_model=schemas.MessageResponse)
def save_athlete_prefs(
    req: schemas.AthletePreferencesRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(models.AthletePreference).filter_by(user_id=current_user.id).delete()
    db.query(models.SportInterest).filter_by(user_id=current_user.id).delete()

    db.add(models.AthletePreference(user_id=current_user.id, practice_sport=req.practice_sport))
    current_user.practice_sport = req.practice_sport
    for sport in req.selected_sports:
        level = max(1, min(5, req.interest_levels.get(sport, 3)))
        db.add(models.SportInterest(user_id=current_user.id, sport_name=sport, interest_level=level))

    db.commit()
    return {"message": "Préférences athlète sauvegardées"}


@router.post("/visitor-preferences", response_model=schemas.MessageResponse)
def save_visitor_prefs(
    req: schemas.VisitorPreferencesRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(models.VisitorPreference).filter_by(user_id=current_user.id).delete()
    db.query(models.SportInterest).filter_by(user_id=current_user.id).delete()

    db.add(models.VisitorPreference(
        user_id=current_user.id,
        favorite_sports=json.dumps(req.favorite_sports, ensure_ascii=False),
    ))

    for sport in req.favorite_sports:
        notify = sport in (req.notify_sports or [])
        db.add(models.SportInterest(user_id=current_user.id, sport_name=sport, interest_level=3, notify=notify))

    db.commit()
    return {"message": "Préférences visiteur sauvegardées"}


@router.get("/me", response_model=schemas.UserProfile)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=schemas.MessageResponse)
def update_profile(
    req: schemas.ProfileUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.profile_image_base64:
        os.makedirs("photos", exist_ok=True)
        header, encoded = req.profile_image_base64.split(",", 1) if "," in req.profile_image_base64 else ("", req.profile_image_base64)
        ext = "jpg"
        if "png" in header:
            ext = "png"
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join("photos", filename)
        encoded = encoded + '=' * (-len(encoded) % 4)
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(encoded))
        current_user.profile_image = filename
        db.commit()

    return {"message": "Profil mis à jour"}


@router.post("/request-email-change", response_model=schemas.MessageResponse)
def request_email_change(
    req: schemas.ChangeEmailRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(models.User).filter(models.User.email == req.new_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce nouvel email est déjà utilisé par un autre compte.")

    otp = auth_utils.generate_otp()
    current_user.otp_code = otp
    current_user.otp_expires_at = auth_utils.otp_expiry()
    db.commit()

    display_name = f"{current_user.prenom or ''} {current_user.nom or ''}".strip() or current_user.username
    # Send OTP to both old and new emails
    email_service.send_otp_email(current_user.email, display_name, otp)
    email_service.send_otp_email(req.new_email, display_name, otp)

    return {"message": "Un code de vérification a été envoyé à votre ancienne et nouvelle adresse email."}


@router.post("/confirm-email-change", response_model=schemas.MessageResponse)
def confirm_email_change(
    req: schemas.ConfirmEmailChangeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.otp_code or current_user.otp_code != req.otp.strip():
        raise HTTPException(status_code=400, detail="Code OTP incorrect")
    if current_user.otp_expires_at and datetime.utcnow() > current_user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Code OTP expiré")

    existing = db.query(models.User).filter(models.User.email == req.new_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ce nouvel email est déjà utilisé par un autre compte.")

    current_user.email = req.new_email
    current_user.otp_code = None
    current_user.otp_expires_at = None
    db.commit()

    return {"message": "Votre adresse email a été mise à jour avec succès."}


@router.post("/request-password-change-otp", response_model=schemas.MessageResponse)
def request_password_change_otp(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    otp = auth_utils.generate_otp()
    current_user.otp_code = otp
    current_user.otp_expires_at = auth_utils.otp_expiry()
    db.commit()

    display_name = f"{current_user.prenom or ''} {current_user.nom or ''}".strip() or current_user.username
    email_service.send_otp_email(current_user.email, display_name, otp)

    return {"message": "Un code de vérification a été envoyé à votre adresse email."}


@router.post("/change-password", response_model=schemas.MessageResponse)
def change_password(
    req: schemas.ChangePasswordRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if req.old_password:
        if not auth_utils.verify_password(req.old_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect.")
    elif req.otp:
        if not current_user.otp_code or current_user.otp_code != req.otp.strip():
            raise HTTPException(status_code=400, detail="Code OTP incorrect.")
        if current_user.otp_expires_at and datetime.utcnow() > current_user.otp_expires_at:
            raise HTTPException(status_code=400, detail="Code OTP expiré.")
        
        current_user.otp_code = None
        current_user.otp_expires_at = None
    else:
        raise HTTPException(status_code=400, detail="Vous devez fournir soit l'ancien mot de passe, soit le code OTP.")

    current_user.password_hash = auth_utils.hash_password(req.new_password)
    db.commit()

    return {"message": "Votre mot de passe a été modifié avec succès."}
