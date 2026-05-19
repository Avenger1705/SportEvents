from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import json

import models
import schemas
import email_service
import auth_utils
from database import get_db
from routers.auth_router import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if str(current_user.role) not in ("admin", "RoleEnum.admin"):
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return current_user


SPORT_TEAM_SIZE = {
    "Football": 11,
    "Basketball": 5,
    "Basketball 3x3": 3,
    "Volleyball": 6,
    "Beach Volleyball": 2,
    "Handball": 7,
    "Rugby": 15,
    "Hockey": 11,
    "Water-polo": 7,
    "Futsal": 5,
    "Badminton": 1,
    "Tennis": 1,
    "Tennis de table": 1,
    "Boxe": 1,
    "Judo": 1,
    "Taekwondo": 1,
    "Escrime": 1,
    "Lutte": 1,
    "Golf": 1,
    "Natation": 1,
    "Athlétisme": 1,
    "Cyclisme sur route": 1,
    "Cyclisme sur piste": 1,
    "BMX freestyle": 1,
    "BMX racing": 1,
    "VTT": 1,
    "Escalade": 1,
    "Surf": 1,
    "Skateboard": 1,
    "Breaking": 1,
    "Gymnastique artistique": 1,
    "Gymnastique rythmique": 1,
    "Gymnastique trampoline": 1,
    "Haltérophilie": 1,
    "Tir": 1,
    "Tir à l'arc": 1,
    "Plongeon": 1,
    "Natation artistique": 2,
    "Natation marathon": 1,
    "Triathlon": 1,
    "Pentathlon moderne": 1,
    "Aviron": 2,
    "Canoë course en ligne": 2,
    "Canoë slalom": 1,
    "Voile": 2,
    "Sports équestres": 1,
}

SOLO_SPORTS = [s for s, count in SPORT_TEAM_SIZE.items() if count == 1]

SPORT_POSITIONS = {
    "Football": ["Gardien", "Défenseur central", "Arrière droit", "Arrière gauche", "Milieu défensif", "Milieu central", "Milieu offensif", "Ailier droit", "Ailier gauche", "Avant-centre"],
    "Basketball": ["Meneur", "Arrière", "Ailier", "Ailier fort", "Pivot"],
    "Basketball 3x3": ["Meneur", "Ailier", "Pivot"],
    "Volleyball": ["Passeur", "Réceptionneur-attaquant", "Central", "Opposé", "Libéro"],
    "Beach Volleyball": ["Bloqueur", "Défenseur"],
    "Handball": ["Gardien", "Arrière gauche", "Arrière droit", "Demi-centre", "Ailier gauche", "Ailier droit", "Pivot"],
    "Rugby": ["Pilier", "Talonneur", "Deuxième ligne", "Flanker", "Numéro 8", "Demi de mêlée", "Demi d'ouverture", "Centre", "Ailier", "Arrière"],
    "Hockey": ["Gardien", "Défenseur", "Milieu", "Attaquant"],
    "Water-polo": ["Gardien", "Arrière", "Ailier", "Centre avant", "Demi", "Pointu"],
    "Futsal": ["Gardien", "Fixo", "Ala", "Pivot"],
    "Tennis": ["Joueur"],
    "Tennis de table": ["Joueur"],
    "Badminton": ["Joueur"],
    "Boxe": ["Boxeur"],
    "Judo": ["Judoka"],
    "Taekwondo": ["Combattant"],
    "Escrime": ["Épéiste", "Fleurettiste", "Sabreur"],
    "Lutte": ["Lutteur"],
    "Golf": ["Golfeur"],
    "Natation": ["Nageur"],
    "Athlétisme": ["Sprinter", "Coureur de fond", "Sauteur", "Lanceur", "Marcheur"],
    "Cyclisme sur route": ["Grimpeur", "Sprinteur", "Rouleur"],
    "Cyclisme sur piste": ["Pistard"],
    "BMX freestyle": ["Rider"],
    "BMX racing": ["Rider"],
    "VTT": ["Rider"],
    "Escalade": ["Grimpeur"],
    "Surf": ["Surfeur"],
    "Skateboard": ["Skateur"],
    "Breaking": ["B-Boy / B-Girl"],
    "Gymnastique artistique": ["Gymnaste"],
    "Gymnastique rythmique": ["Gymnaste"],
    "Gymnastique trampoline": ["Gymnaste"],
    "Haltérophilie": ["Haltérophile"],
    "Tir": ["Tireur"],
    "Tir à l'arc": ["Archer"],
    "Plongeon": ["Plongeur"],
    "Natation artistique": ["Nageuse artistique"],
    "Natation marathon": ["Nageur"],
    "Triathlon": ["Triathlète"],
    "Pentathlon moderne": ["Pentathlonien"],
    "Aviron": ["Rameur", "Barreur"],
    "Canoë course en ligne": ["Pagayeur"],
    "Canoë slalom": ["Pagayeur"],
    "Voile": ["Barreur", "Équipier"],
    "Sports équestres": ["Cavalier"],
}


@router.get("/sports-config")
def get_sports_config(admin: models.User = Depends(require_admin)):
    return {
        "team_sizes": SPORT_TEAM_SIZE,
        "solo_sports": SOLO_SPORTS,
        "team_sports": [s for s in SPORT_TEAM_SIZE if s not in SOLO_SPORTS],
        "positions": SPORT_POSITIONS,
    }


@router.get("/dashboard")
def admin_dashboard(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.query(func.count(models.User.id)).scalar()
    total_joueurs = db.query(func.count(models.User.id)).filter(models.User.role == "joueur").scalar()
    total_visitors = db.query(func.count(models.User.id)).filter(models.User.role == "visitor").scalar()
    total_admins = db.query(func.count(models.User.id)).filter(models.User.role == "admin").scalar()
    total_events = db.query(func.count(models.Event.id)).scalar()
    total_teams = db.query(func.count(models.Team.id)).scalar()
    total_tournaments = db.query(func.count(models.Tournament.id)).scalar()
    total_matches = db.query(func.count(models.Match.id)).scalar()
    total_bookings = db.query(func.count(models.Booking.id)).scalar()
    total_comments = db.query(func.count(models.Comment.id)).scalar()

    sports_events = db.query(models.Event.sport, func.count(models.Event.id))\
        .filter(models.Event.sport.isnot(None))\
        .group_by(models.Event.sport).all()

    recent_users = db.query(models.User).order_by(models.User.created_at.desc()).limit(10).all()
    recent_events = db.query(models.Event).order_by(models.Event.created_at.desc()).limit(5).all()

    users_per_month = db.query(
        func.date_format(models.User.created_at, '%Y-%m').label('month'),
        func.count(models.User.id)
    ).group_by('month').order_by('month').all()

    return {
        "total_users": total_users,
        "total_joueurs": total_joueurs,
        "total_visitors": total_visitors,
        "total_admins": total_admins,
        "total_events": total_events,
        "total_teams": total_teams,
        "total_tournaments": total_tournaments,
        "total_matches": total_matches,
        "total_bookings": total_bookings,
        "total_comments": total_comments,
        "sports_distribution": [{"sport": s, "count": c} for s, c in sports_events],
        "recent_users": [
            {"id": u.id, "username": u.username, "email": u.email, "role": str(u.role).replace("RoleEnum.",""), "created_at": str(u.created_at), "profile_image": u.profile_image}
            for u in recent_users
        ],
        "recent_events": [
            {"id": e.id, "title": e.title, "sport": e.sport, "event_date": str(e.event_date) if e.event_date else None}
            for e in recent_events
        ],
        "users_per_month": [{"month": m, "count": c} for m, c in users_per_month],
    }


@router.get("/users")
def list_users(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.created_at.desc()).all()
    return [
        {
            "id": u.id, "nom": u.nom, "prenom": u.prenom, "username": u.username,
            "email": u.email, "role": str(u.role).replace("RoleEnum.",""),
            "is_verified": u.is_verified, "created_at": str(u.created_at),
            "profile_image": u.profile_image, "age": u.age, "height": u.height,
            "weight": u.weight, "ranking": u.ranking, "practice_sport": u.practice_sport,
            "matches_played": u.matches_played, "matches_won": u.matches_won,
        }
        for u in users
    ]


@router.post("/users", status_code=201)
def create_user(req: schemas.AdminUserCreate, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if db.query(models.User).filter(models.User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    
    hashed_pwd = auth_utils.hash_password(req.password)
    user = models.User(
        nom=req.nom,
        prenom=req.prenom,
        username=req.username,
        email=req.email,
        password_hash=hashed_pwd,
        role=req.role,
        is_verified=True,
        practice_sport=req.practice_sport,
        age=req.age,
        height=req.height,
        weight=req.weight,
        ranking=req.ranking
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Utilisateur créé", "id": user.id}


@router.put("/users/{user_id}")
def update_user(user_id: int, req: schemas.AdminUserUpdate, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    if req.email and req.email != user.email:
        if db.query(models.User).filter(models.User.email == req.email).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        user.email = req.email
        
    if req.username and req.username != user.username:
        if db.query(models.User).filter(models.User.username == req.username).first():
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
        user.username = req.username

    if req.nom is not None: user.nom = req.nom
    if req.prenom is not None: user.prenom = req.prenom
    if req.role is not None: user.role = req.role
    if req.practice_sport is not None: user.practice_sport = req.practice_sport
    if req.age is not None: user.age = req.age
    if req.height is not None: user.height = req.height
    if req.weight is not None: user.weight = req.weight
    if req.ranking is not None: user.ranking = req.ranking
    if req.password:
        user.password_hash = auth_utils.hash_password(req.password)
        
    db.commit()
    return {"message": "Utilisateur mis à jour"}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")
    db.delete(user)
    db.commit()
    return {"message": "Utilisateur supprimé"}


@router.delete("/events/{event_id}")
def admin_delete_event(event_id: int, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    ev = db.get(models.Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    db.delete(ev)
    db.commit()
    return {"message": "Événement supprimé"}


@router.delete("/comments/{comment_id}")
def admin_delete_comment(comment_id: int, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    comment = db.get(models.Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Commentaire introuvable")
    db.delete(comment)
    db.commit()
    return {"message": "Commentaire supprimé"}


@router.post("/teams", status_code=201)
def create_team(req: schemas.TeamCreate, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    team = models.Team(name=req.name, sport=req.sport, created_by=admin.id)
    db.add(team)
    db.flush()

    for m in req.members:
        member = models.TeamMember(
            team_id=team.id,
            player_name=m.player_name,
            player_email=m.player_email,
            position=m.position,
            jersey_number=m.jersey_number,
            user_id=m.user_id,
        )
        db.add(member)
        if m.player_email:
            email_service.send_team_assignment_email(m.player_email, m.player_name, req.name, req.sport)

    db.commit()
    db.refresh(team)
    return _team_dict(team)


@router.get("/teams")
def list_teams(admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    teams = db.query(models.Team).order_by(models.Team.created_at.desc()).all()
    return [_team_dict(t) for t in teams]


@router.get("/teams/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.get(models.Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Équipe introuvable")
    return _team_dict(team)


@router.put("/teams/{team_id}")
def update_team(team_id: int, req: schemas.TeamUpdate, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    team = db.get(models.Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Équipe introuvable")

    if req.name is not None:
        team.name = req.name
    if req.sport is not None:
        team.sport = req.sport

    if req.members is not None:
        db.query(models.TeamMember).filter_by(team_id=team.id).delete()
        for m in req.members:
            member = models.TeamMember(
                team_id=team.id,
                player_name=m.player_name,
                player_email=m.player_email,
                position=m.position,
                jersey_number=m.jersey_number,
                user_id=m.user_id,
            )
            db.add(member)
            if m.player_email:
                email_service.send_team_assignment_email(m.player_email, m.player_name, team.name, team.sport)

    db.commit()
    db.refresh(team)
    return _team_dict(team)


@router.delete("/teams/{team_id}")
def delete_team(team_id: int, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    team = db.get(models.Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Équipe introuvable")
    db.delete(team)
    db.commit()
    return {"message": "Équipe supprimée"}


def _team_dict(team: models.Team) -> dict:
    return {
        "id": team.id,
        "name": team.name,
        "sport": team.sport,
        "created_at": str(team.created_at),
        "members": [
            {
                "id": m.id, "player_name": m.player_name, "player_email": m.player_email,
                "position": m.position, "jersey_number": m.jersey_number, "user_id": m.user_id,
            }
            for m in team.members
        ],
    }


@router.post("/tournaments", status_code=201)
def create_tournament(req: schemas.TournamentCreate, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    from datetime import datetime
    start = datetime.fromisoformat(req.start_date) if req.start_date else None
    end = datetime.fromisoformat(req.end_date) if req.end_date else None

    tournament = models.Tournament(
        name=req.name, sport=req.sport, description=req.description,
        location=req.location, start_date=start, end_date=end,
        match_duration=req.match_duration, created_by=admin.id,
    )
    db.add(tournament)
    db.flush()

    for i, tid in enumerate(req.team_ids):
        db.add(models.TournamentTeam(tournament_id=tournament.id, team_id=tid, seed=i+1))

    num_teams = len(req.team_ids)
    if num_teams >= 2:
        _generate_bracket(db, tournament.id, req.team_ids)

    db.commit()
    db.refresh(tournament)
    return _tournament_dict(tournament)


def _generate_bracket(db: Session, tournament_id: int, team_ids: list):
    import math
    n = len(team_ids)
    num_rounds = math.ceil(math.log2(n))
    first_round_matches = math.ceil(n / 2)

    byes = (2 ** num_rounds) - n

    match_order = 0
    for i in range(first_round_matches):
        team_a = team_ids[i * 2] if i * 2 < n else None
        team_b = team_ids[i * 2 + 1] if i * 2 + 1 < n else None
        match_order += 1

        match = models.Match(
            tournament_id=tournament_id,
            round_number=1,
            match_order=match_order,
            team_a_id=team_a,
            team_b_id=team_b,
            status=models.MatchStatusEnum.a_venir,
        )
        db.add(match)
        db.flush()

        if team_a and not team_b:
            match.winner_id = team_a
            match.status = models.MatchStatusEnum.termine
        elif team_b and not team_a:
            match.winner_id = team_b
            match.status = models.MatchStatusEnum.termine

    for r in range(2, num_rounds + 1):
        matches_in_round = 2 ** (num_rounds - r)
        for m_idx in range(matches_in_round):
            match_order += 1
            match = models.Match(
                tournament_id=tournament_id,
                round_number=r,
                match_order=match_order,
                status=models.MatchStatusEnum.a_venir,
            )
            db.add(match)


@router.get("/tournaments")
def list_tournaments(db: Session = Depends(get_db)):
    tournaments = db.query(models.Tournament).order_by(models.Tournament.created_at.desc()).all()
    return [_tournament_dict(t) for t in tournaments]


@router.get("/tournaments/{tournament_id}")
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    t = db.get(models.Tournament, tournament_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tournoi introuvable")
    return _tournament_dict(t)


@router.put("/matches/{match_id}")
def update_match(match_id: int, req: schemas.MatchUpdate, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    from datetime import datetime
    match = db.get(models.Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match introuvable")

    if req.team_a_id is not None:
        match.team_a_id = req.team_a_id
    if req.team_b_id is not None:
        match.team_b_id = req.team_b_id
    if req.score_a is not None:
        match.score_a = req.score_a
    if req.score_b is not None:
        match.score_b = req.score_b
    if req.winner_id is not None:
        match.winner_id = req.winner_id
        _advance_winner(db, match)
        _update_player_stats(db, match)
    if req.status is not None:
        match.status = req.status
    if req.match_date is not None:
        match.match_date = datetime.fromisoformat(req.match_date) if req.match_date else None
    if req.match_time is not None:
        match.match_time = req.match_time
    if req.location is not None:
        match.location = req.location

    db.commit()
    db.refresh(match)
    return _match_dict(match)


def _advance_winner(db: Session, match: models.Match):
    import math
    all_matches = db.query(models.Match).filter_by(tournament_id=match.tournament_id).order_by(models.Match.round_number, models.Match.match_order).all()

    current_round_matches = [m for m in all_matches if m.round_number == match.round_number]
    idx_in_round = current_round_matches.index(match)
    next_match_idx = idx_in_round // 2

    next_round_matches = [m for m in all_matches if m.round_number == match.round_number + 1]
    if next_match_idx < len(next_round_matches):
        next_match = next_round_matches[next_match_idx]
        if idx_in_round % 2 == 0:
            next_match.team_a_id = match.winner_id
        else:
            next_match.team_b_id = match.winner_id


def _update_player_stats(db: Session, match: models.Match):
    if not match.winner_id:
        return
    loser_id = match.team_b_id if match.winner_id == match.team_a_id else match.team_a_id

    winner_members = db.query(models.TeamMember).filter_by(team_id=match.winner_id).all()
    for m in winner_members:
        if m.user_id:
            user = db.get(models.User, m.user_id)
            if user:
                user.matches_played = (user.matches_played or 0) + 1
                user.matches_won = (user.matches_won or 0) + 1

    if loser_id:
        loser_members = db.query(models.TeamMember).filter_by(team_id=loser_id).all()
        for m in loser_members:
            if m.user_id:
                user = db.get(models.User, m.user_id)
                if user:
                    user.matches_played = (user.matches_played or 0) + 1
                    user.matches_lost = (user.matches_lost or 0) + 1


@router.delete("/tournaments/{tournament_id}")
def delete_tournament(tournament_id: int, admin: models.User = Depends(require_admin), db: Session = Depends(get_db)):
    t = db.get(models.Tournament, tournament_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tournoi introuvable")
    db.delete(t)
    db.commit()
    return {"message": "Tournoi supprimé"}


@router.put("/tournaments/{tournament_id}/schedule")
def schedule_tournament_matches(
    tournament_id: int,
    req: schemas.TournamentScheduleRequest,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from datetime import datetime
    tournament = db.get(models.Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournoi introuvable")

    updated = []
    for item in req.matches:
        match = db.get(models.Match, item.match_id)
        if not match or match.tournament_id != tournament_id:
            continue
        if item.match_date:
            try:
                match.match_date = datetime.fromisoformat(item.match_date)
            except ValueError:
                pass
        if item.match_time is not None:
            match.match_time = item.match_time or None
        if item.location is not None:
            match.location = item.location or None
        updated.append(item.match_id)

    db.commit()
    return {"message": f"{len(updated)} match(s) planifié(s)", "updated": updated}


def _tournament_dict(t: models.Tournament) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "sport": t.sport,
        "description": t.description,
        "location": t.location,
        "start_date": str(t.start_date) if t.start_date else None,
        "end_date": str(t.end_date) if t.end_date else None,
        "match_duration": t.match_duration,
        "status": t.status,
        "created_at": str(t.created_at),
        "teams": [
            {"id": tt.team.id, "name": tt.team.name, "seed": tt.seed, "sport": tt.team.sport}
            for tt in t.teams
        ],
        "matches": [_match_dict(m) for m in sorted(t.matches, key=lambda x: (x.round_number, x.match_order))],
    }


def _match_dict(m: models.Match) -> dict:
    return {
        "id": m.id,
        "tournament_id": m.tournament_id,
        "round_number": m.round_number,
        "match_order": m.match_order,
        "team_a": {"id": m.team_a.id, "name": m.team_a.name} if m.team_a else None,
        "team_b": {"id": m.team_b.id, "name": m.team_b.name} if m.team_b else None,
        "score_a": m.score_a,
        "score_b": m.score_b,
        "winner": {"id": m.winner.id, "name": m.winner.name} if m.winner else None,
        "match_date": str(m.match_date) if m.match_date else None,
        "match_time": m.match_time,
        "location": m.location,
        "status": str(m.status).replace("MatchStatusEnum.",""),
        "bookings_count": len(m.bookings) if m.bookings else 0,
    }


@router.get("/players")
def list_players(db: Session = Depends(get_db)):
    players = db.query(models.User).filter(models.User.role == "joueur").order_by(models.User.username).all()
    return [
        {
            "id": u.id, "nom": u.nom, "prenom": u.prenom, "username": u.username,
            "email": u.email, "profile_image": u.profile_image,
            "age": u.age, "height": u.height, "weight": u.weight,
            "ranking": u.ranking, "practice_sport": u.practice_sport,
            "matches_played": u.matches_played, "matches_won": u.matches_won, "matches_lost": u.matches_lost,
        }
        for u in players
    ]


@router.get("/players/search")
def search_players(q: str = "", db: Session = Depends(get_db)):
    from sqlalchemy import or_
    if not q or len(q) < 1:
        return []
    players = db.query(models.User).filter(
        models.User.role == "joueur",
        or_(
            models.User.nom.ilike(f"%{q}%"),
            models.User.prenom.ilike(f"%{q}%"),
            models.User.username.ilike(f"%{q}%"),
            models.User.email.ilike(f"%{q}%"),
        )
    ).limit(10).all()
    return [
        {
            "id": u.id, "nom": u.nom, "prenom": u.prenom,
            "username": u.username, "email": u.email,
            "profile_image": u.profile_image,
            "practice_sport": u.practice_sport,
        }
        for u in players
    ]


@router.get("/player/{user_id}")
def get_player_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    team_memberships = db.query(models.TeamMember).filter_by(user_id=user.id).all()
    teams = []
    for tm in team_memberships:
        team = db.get(models.Team, tm.team_id)
        if team:
            teams.append({"id": team.id, "name": team.name, "sport": team.sport, "position": tm.position})

    match_history = []
    all_member_team_ids = [tm.team_id for tm in team_memberships]
    if all_member_team_ids:
        matches = db.query(models.Match).filter(
            (models.Match.team_a_id.in_(all_member_team_ids)) | (models.Match.team_b_id.in_(all_member_team_ids))
        ).order_by(models.Match.match_date.desc()).all()
        for m in matches:
            match_history.append(_match_dict(m))

    return {
        "id": user.id, "nom": user.nom, "prenom": user.prenom, "username": user.username,
        "email": user.email, "profile_image": user.profile_image,
        "age": user.age, "height": user.height, "weight": user.weight,
        "ranking": user.ranking, "practice_sport": user.practice_sport,
        "matches_played": user.matches_played or 0, "matches_won": user.matches_won or 0,
        "matches_lost": user.matches_lost or 0,
        "teams": teams,
        "match_history": match_history,
    }


@router.post("/bookings", status_code=201)
def create_booking(req: schemas.BookingCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    import uuid
    from datetime import datetime, timedelta

    match = db.get(models.Match, req.match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match introuvable")

    # Block booking if match already started or finished
    status_str = str(match.status)
    if "en_cours" in status_str or "termine" in status_str:
        raise HTTPException(status_code=400, detail="Ce match est déjà commencé ou terminé")

    # Enforce 1-hour booking deadline
    if not match.match_date:
        raise HTTPException(status_code=400, detail="Ce match n'a pas encore de date planifiée. Réservation impossible.")

    match_start = match.match_date
    if match.match_time:
        try:
            t = match.match_time.strip().replace("H", "h")
            sep = "h" if "h" in t else ":"
            parts = t.split(sep)
            h = int(parts[0].strip())
            m = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0
            match_start = match_start.replace(hour=h, minute=m, second=0, microsecond=0)
        except Exception:
            pass

    now = datetime.utcnow()
    if match_start <= now:
        raise HTTPException(status_code=400, detail="Ce match est déjà passé")
    if match_start - now < timedelta(hours=1):
        raise HTTPException(status_code=400, detail="Les réservations sont fermées (moins d'1 heure avant le début du match)")

    existing = db.query(models.Booking).filter_by(user_id=current_user.id, match_id=req.match_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vous avez déjà réservé pour ce match")

    qr_code = f"SPORTEV-{uuid.uuid4().hex[:12].upper()}"
    booking = models.Booking(user_id=current_user.id, match_id=req.match_id, qr_code=qr_code)
    db.add(booking)
    db.commit()
    db.refresh(booking)

    team_a_name = match.team_a.name if match.team_a else "TBD"
    team_b_name = match.team_b.name if match.team_b else "TBD"
    match_date_str = match_start.strftime("%d/%m/%Y %H:%M")
    match_info = f"{team_a_name} vs {team_b_name} – {match_date_str}"
    display = f"{current_user.prenom or ''} {current_user.nom or ''}".strip() or current_user.username
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_code}"
    email_service.send_booking_confirmation_email(current_user.email, display, match_info, qr_url)

    return {"message": "Réservation confirmée", "qr_code": qr_code, "booking_id": booking.id}


@router.get("/bookings/my")
def my_bookings(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = db.query(models.Booking).filter_by(user_id=current_user.id).order_by(models.Booking.booked_at.desc()).all()
    result = []
    for b in bookings:
        match = db.get(models.Match, b.match_id)
        result.append({
            "id": b.id,
            "qr_code": b.qr_code,
            "booked_at": str(b.booked_at),
            "match": _match_dict(match) if match else None,
        })
    return result


@router.get("/calendar")
def player_calendar(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    team_memberships = db.query(models.TeamMember).filter_by(user_id=current_user.id).all()
    team_ids = [tm.team_id for tm in team_memberships]

    if not team_ids:
        return []

    matches = db.query(models.Match).filter(
        (models.Match.team_a_id.in_(team_ids)) | (models.Match.team_b_id.in_(team_ids))
    ).order_by(models.Match.match_date.asc()).all()

    return [_match_dict(m) for m in matches]


@router.post("/events/{event_id}/comments", status_code=201)
def add_comment(event_id: int, req: schemas.CommentCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    ev = db.get(models.Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    comment = models.Comment(event_id=event_id, user_id=current_user.id, content=req.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": str(comment.created_at),
        "user": {"id": current_user.id, "username": current_user.username, "profile_image": current_user.profile_image},
    }


@router.get("/events/{event_id}/comments")
def get_comments(event_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comment).filter_by(event_id=event_id).order_by(models.Comment.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "content": c.content,
            "created_at": str(c.created_at),
            "user": {"id": c.user.id, "username": c.user.username, "profile_image": c.user.profile_image},
        }
        for c in comments
    ]


# ── Match Comments ────────────────────────────────────────────────────────────

@router.post("/matches/{match_id}/comments", status_code=201)
def add_match_comment(
    match_id: int,
    req: schemas.MatchCommentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(models.Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match introuvable")

    content = req.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Le commentaire ne peut pas être vide")

    comment = models.MatchComment(
        match_id=match_id,
        user_id=current_user.id,
        content=content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": str(comment.created_at),
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "profile_image": current_user.profile_image,
        },
    }


@router.get("/matches/{match_id}/comments")
def get_match_comments(match_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(models.MatchComment)
        .filter_by(match_id=match_id)
        .order_by(models.MatchComment.created_at.asc())
        .all()
    )
    return [
        {
            "id": c.id,
            "content": c.content,
            "created_at": str(c.created_at),
            "user": {
                "id": c.user.id,
                "username": c.user.username,
                "profile_image": c.user.profile_image,
            },
        }
        for c in comments
    ]


@router.delete("/matches/comments/{comment_id}")
def delete_match_comment(
    comment_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.get(models.MatchComment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Commentaire introuvable")

    is_admin = str(current_user.role) in ("admin", "RoleEnum.admin")
    if comment.user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Non autorisé")

    db.delete(comment)
    db.commit()
    return {"message": "Commentaire supprimé"}
