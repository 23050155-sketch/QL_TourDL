
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User


# Khóa bản ghi tài khoản trong transaction
def lock_user(
    db: Session,
    user_id: int
) -> User | None:

    return (
        db.query(User)
        .filter(User.id == user_id)
        .populate_existing()
        .with_for_update()
        .first()
    )


# Tăng phiên bản Token để thu hồi JWT cũ
def revoke_user_tokens(user: User) -> None:

    if user.token_version >= 2**32 - 1:

        raise HTTPException(
            status_code=409,
            detail="Phiên bản Token đã đạt giới hạn"
        )

    user.token_version += 1
