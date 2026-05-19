from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth_utils
from database import get_db
from routers.auth_router import get_current_user

router = APIRouter(prefix="/api/comments", tags=["Comments"])

@router.post("/event", response_model=schemas.MessageResponse)
def add_event_comment(req: schemas.EventCommentCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Le commentaire ne peut pas être vide")
    
    comment = models.Comment(
        event_id=req.event_id,
        user_id=user.id,
        content=req.content.strip()
    )
    db.add(comment)
    db.commit()
    return {"message": "Commentaire ajouté"}

@router.get("/event/{event_id}", response_model=List[schemas.CommentResponse])
def get_event_comments(event_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter(models.Comment.event_id == event_id).order_by(models.Comment.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "content": c.content,
            "created_at": str(c.created_at),
            "user": {
                "id": c.user_id,
                "username": c.user.username,
                "profile_image": c.user.profile_image
            }
        }
        for c in comments
    ]

@router.post("/match", response_model=schemas.MessageResponse)
def add_match_comment(req: schemas.MatchCommentCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Le commentaire ne peut pas être vide")
    
    comment = models.MatchComment(
        match_id=req.match_id,
        user_id=user.id,
        content=req.content.strip()
    )
    db.add(comment)
    db.commit()
    return {"message": "Commentaire ajouté"}

@router.get("/match/{match_id}", response_model=List[schemas.CommentResponse])
def get_match_comments(match_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.MatchComment).filter(models.MatchComment.match_id == match_id).order_by(models.MatchComment.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "content": c.content,
            "created_at": str(c.created_at),
            "user": {
                "id": c.user_id,
                "username": c.user.username,
                "profile_image": c.user.profile_image
            }
        }
        for c in comments
    ]

@router.delete("/{comment_type}/{comment_id}", response_model=schemas.MessageResponse)
def delete_comment(comment_type: str, comment_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Seuls les administrateurs peuvent supprimer des commentaires")
    
    if comment_type == "event":
        comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    elif comment_type == "match":
        comment = db.query(models.MatchComment).filter(models.MatchComment.id == comment_id).first()
    else:
        raise HTTPException(status_code=400, detail="Type de commentaire invalide")
    
    if not comment:
        raise HTTPException(status_code=404, detail="Commentaire introuvable")
    
    db.delete(comment)
    db.commit()
    return {"message": "Commentaire supprimé"}
