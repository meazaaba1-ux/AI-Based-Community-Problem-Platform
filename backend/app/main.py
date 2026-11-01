
from pathlib import Path
import pickle
import shutil
import uuid

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import User, Problem
from .schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    ProblemResponse,
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="AI-Based Community Problem Detection and Reporting Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Community Problem Platform API is running"
    }


# --------------------------------------------------
# IMAGE UPLOAD CONFIGURATION
# --------------------------------------------------

UPLOAD_DIR = (
    Path(__file__).resolve().parent.parent / "uploads"
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOAD_DIR)),
    name="uploads",
)


# --------------------------------------------------
# AI MODEL LOADING
# --------------------------------------------------

AI_MODEL_PATH = (
    Path(__file__).resolve().parent
    / "ai_model"
    / "problem_classifier.pkl"
)

try:
    with AI_MODEL_PATH.open("rb") as model_file:
        ai_model = pickle.load(model_file)

    print("AI classification model loaded successfully.")

except FileNotFoundError:
    ai_model = None
    print("AI model file not found. Train the model first.")

except Exception as error:
    ai_model = None
    print(f"Could not load AI model: {error}")


# --------------------------------------------------
# REGISTER USER
# --------------------------------------------------

@app.post("/register", response_model=UserResponse)


# --------------------------------------------------
# CREATE OFFICER ACCOUNT
# --------------------------------------------------

class OfficerCreate(BaseModel):
    name: str
    email: str
    password: str
    category: str


@app.post("/create-officer")
def create_officer(
    officer: OfficerCreate,
    db: Session = Depends(get_db),
):
    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == officer.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email is already registered.",
        )

    # Create officer account
    new_officer = User(
        name=officer.name,
        email=officer.email,
        password=officer.password,
        role="officer",
        category=officer.category,
    )

    db.add(new_officer)
    db.commit()
    db.refresh(new_officer)

    return {
        "message": "Officer account created successfully.",
        "officer_id": new_officer.id,
        "name": new_officer.name,
        "email": new_officer.email,
        "category": new_officer.category,
        "role": new_officer.role,
    }

def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email is already registered.",
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password,
        role="citizen",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# --------------------------------------------------
# LOGIN USER
# --------------------------------------------------

@app.post("/login")
def login_user(
    login: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == login.email)
        .first()
    )

    if user is None or user.password != login.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    return {
        "message": "Login successful",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


# --------------------------------------------------
# AI CATEGORY PREDICTION
# --------------------------------------------------

class ProblemPredictionRequest(BaseModel):
    description: str


@app.post("/predict-category")
def predict_category(
    request: ProblemPredictionRequest,
):
    if ai_model is None:
        raise HTTPException(
            status_code=503,
            detail="AI model is not loaded. Train the model first.",
        )

    description = request.description.strip()

    if not description:
        raise HTTPException(
            status_code=400,
            detail="Please provide a problem description.",
        )

    predicted_category = ai_model.predict([description])[0]

    return {
        "description": description,
        "predicted_category": str(predicted_category),
    }


# --------------------------------------------------
# SUBMIT A COMMUNITY PROBLEM
# --------------------------------------------------

@app.post("/problems", response_model=ProblemResponse)
async def create_problem(
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    user_id: int = Form(...),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    # Clean form values
    title = title.strip()
    description = description.strip()
    location = location.strip()

    # Validate required fields
    if not title or not description or not location:
        raise HTTPException(
            status_code=400,
            detail="Title, description, and location are required.",
        )

    # Check that the user exists
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please login again.",
        )

    # --------------------------------------------------
    # AI CATEGORY PREDICTION
    # --------------------------------------------------

    if ai_model is not None:
        try:
            predicted_category = str(
                ai_model.predict([description])[0]
            )
        except Exception:
            predicted_category = "Unclassified"
    else:
        predicted_category = "Unclassified"




        
    # --------------------------------------------------
    # AUTOMATIC OFFICER ASSIGNMENT
    # --------------------------------------------------

    assigned_officer = (
        db.query(User)
        .filter(
            User.role == "officer",
            User.category == predicted_category,
        )
        .first()
    )

    assigned_officer_id = (
        assigned_officer.id
        if assigned_officer is not None
        else None
    )


    # --------------------------------------------------
    # IMAGE UPLOAD
    # --------------------------------------------------

    image_url = None

    if image is not None and image.filename:

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if image.content_type not in allowed_types:
            await image.close()

            raise HTTPException(
                status_code=400,
                detail="Upload a JPG, PNG, or WEBP image.",
            )

        extension = Path(image.filename).suffix.lower()

        if extension not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            await image.close()

            raise HTTPException(
                status_code=400,
                detail="Unsupported image file extension.",
            )

        saved_filename = f"{uuid.uuid4().hex}{extension}"

        destination = UPLOAD_DIR / saved_filename

        try:
            with destination.open("wb") as buffer:
                shutil.copyfileobj(
                    image.file,
                    buffer,
                )

            image_url = f"/uploads/{saved_filename}"

        finally:
            await image.close()

    # --------------------------------------------------
    # SAVE REPORT TO MYSQL
    # --------------------------------------------------

    new_problem = Problem(
        title=title,
        description=description,
        location=location,
        category=predicted_category,
        image_url=image_url,
        latitude=latitude,
        longitude=longitude,
        status="pending",
        user_id=user_id,
     assigned_officer_id=assigned_officer_id,
    )

    try:
        db.add(new_problem)

        db.commit()

        db.refresh(new_problem)

        return new_problem

    except Exception:
        db.rollback()

        # Remove uploaded image if database save fails
        if image_url:
            saved_path = UPLOAD_DIR / Path(image_url).name

            saved_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Could not save the report. Check the database configuration.",
        )

# --------------------------------------------------
# GET OFFICER ASSIGNED REPORTS
# --------------------------------------------------

@app.get(
    "/officer/problems",
    response_model=list[ProblemResponse],
)
def get_officer_problems(
    officer_id: int,
    db: Session = Depends(get_db),
):
    # Check officer account
    officer = (
        db.query(User)
        .filter(
            User.id == officer_id,
            User.role == "officer",
        )
        .first()
    )

    if officer is None:
        raise HTTPException(
            status_code=404,
            detail="Officer account not found.",
        )

    # Get reports assigned to this officer
    reports = (
        db.query(Problem)
        .filter(
            Problem.assigned_officer_id == officer_id
        )
        .order_by(Problem.id.desc())
        .all()
    )

    return reports


# --------------------------------------------------
# GET COMMUNITY PROBLEMS
# --------------------------------------------------

@app.get(
    "/problems",
    response_model=list[ProblemResponse],
)
def get_problems(
    user_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Problem)

    # Citizen: show only reports belonging to that user
    if user_id is not None:

        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found.",
            )

        query = query.filter(
            Problem.user_id == user_id
        )

    # Admin: when user_id is not provided,
    # return all community reports
    reports = (
        query
        .order_by(Problem.id.desc())
        .all()
    )

    return reports


# --------------------------------------------------
# UPDATE REPORT STATUS
# --------------------------------------------------

@app.patch("/problems/{problem_id}/status")
def update_problem_status(
    problem_id: int,
    status: str,
    db: Session = Depends(get_db),
):

    allowed_statuses = {
        "pending",
        "in_progress",
        "resolved",
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Choose pending, "
                "in_progress, or resolved."
            ),
        )

    problem = (
        db.query(Problem)
        .filter(Problem.id == problem_id)
        .first()
    )

    if problem is None:
        raise HTTPException(
            status_code=404,
            detail="Problem report not found.",
        )

    problem.status = status

    try:
        db.commit()

        db.refresh(problem)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not update report status.",
        )

    return {
        "message": "Problem status updated successfully",
        "id": problem.id,
        "status": problem.status,
    }
