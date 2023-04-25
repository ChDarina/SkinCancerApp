import logging
from typing import List

from db.base import Base, engine, get_db
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from schemas.patient import PatientCreate, PatientUpdate, PatientModel
from services.patient import create_patient, read_patient, update_patient, delete_patient, read_patients, upload
from sqlalchemy.orm import Session

from errors.badrequest import BadRequestError
from errors.forbidden import ForbiddenError

from db.user import User
from services.token import is_correct_user, get_current_user
from starlette.responses import JSONResponse

Base.metadata.create_all(engine)

router = APIRouter(prefix="/patient",
                   tags=["patients"],
                   responses={404: {"description": "Patients router not found"}})

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s:  %(asctime)s  %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")


@router.post("/")
def create_patient_route(patient: PatientCreate, db: Session = Depends(get_db)):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=create_patient(db, patient))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{patient_id}", response_model=PatientModel)
def read_patient_route(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    is_correct_user(patient_id, current_user.id)
    try:
        return read_patient(db, patient_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[PatientModel])
def read_patients_route(db: Session = Depends(get_db)):
    try:
        return read_patients(db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{patient_id}", response_model=PatientModel)
def update_patient_route(patient_id: int, patient: PatientUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    is_correct_user(patient_id, current_user.id)
    try:
        return update_patient(db, patient_id, patient)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{patient_id}")
def delete_patient_route(patient_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    is_correct_user(patient_id, current_user.id)
    try:
        delete_patient(db, patient_id)
        return {"detail": f"Patient with id {patient_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{patient_id}/upload")
def upload_photo_route(patient_id: int, file: UploadFile, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    is_correct_user(patient_id, current_user.id)
    try:
        return upload(db, patient_id, file)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))