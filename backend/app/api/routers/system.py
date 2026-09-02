from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.schemas import UserSettingsSchema, GeneralMessageResponse
from app.models.db import DBUserSettings
from app.services.transaction_service import delete_all_user_data

router = APIRouter(prefix="/api", tags=["system"])

@router.delete("/data", response_model=GeneralMessageResponse)
def wipe_all_data(db: Session = Depends(get_db)):
    success = delete_all_user_data(db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to wipe user data.")
    return GeneralMessageResponse(
        message="All user transaction data and category overrides have been permanently deleted.",
        success=True
    )

@router.get("/settings", response_model=UserSettingsSchema)
def get_settings(db: Session = Depends(get_db)):
    st = db.query(DBUserSettings).filter(DBUserSettings.id == 1).first()
    if not st:
        return UserSettingsSchema()
    # Mask API Key for privacy
    masked_key = ""
    if st.llm_api_key:
        masked_key = st.llm_api_key[:4] + "..." + st.llm_api_key[-4:] if len(st.llm_api_key) > 8 else "***"

    return UserSettingsSchema(
        currency=st.currency or "₹",
        llm_provider=st.llm_provider or "auto",
        llm_api_key=masked_key
    )

@router.put("/settings", response_model=UserSettingsSchema)
def update_settings(payload: UserSettingsSchema, db: Session = Depends(get_db)):
    st = db.query(DBUserSettings).filter(DBUserSettings.id == 1).first()
    if not st:
        st = DBUserSettings(id=1)
        db.add(st)

    st.currency = payload.currency
    st.llm_provider = payload.llm_provider
    if payload.llm_api_key and not payload.llm_api_key.startswith("***"):
        st.llm_api_key = payload.llm_api_key

    db.commit()
    db.refresh(st)

    masked_key = ""
    if st.llm_api_key:
        masked_key = st.llm_api_key[:4] + "..." + st.llm_api_key[-4:] if len(st.llm_api_key) > 8 else "***"

    return UserSettingsSchema(
        currency=st.currency,
        llm_provider=st.llm_provider,
        llm_api_key=masked_key
    )
