from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
try:
    from server.schemas.user import RegisterIn, LoginIn, UserOut
    from server.infrastructure.db import User
    from server.infrastructure.security import hash_password, verify_password, create_token
    from server.dependencies import get_db, get_current_user
except ModuleNotFoundError:
    from schemas.user import RegisterIn, LoginIn, UserOut
    from infrastructure.db import User
    from infrastructure.security import hash_password, verify_password, create_token
    from dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/register", status_code=201)
def register(req: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=req.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=req.email, name=req.name, password_hash=hash_password(req.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"userId": user.id}

@router.post("/login")
def login(req: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")
    token = create_token(user.email)
    return {"accessToken": token, "user": {"id": user.id, "email": user.email, "name": user.name}}

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(id=user.id, email=user.email, name=user.name)
