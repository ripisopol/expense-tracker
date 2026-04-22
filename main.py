from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import Base, engine, get_db
from models import Expense

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")

'''@app.on_event("startup")
def startup():
    from database import Base, engine
    Base.metadata.create_all(bind=engine)'''

@app.get("/health")
def health():
    return {"status": "ok"}

class ExpenseSchema(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    date: date

@app.get("/expenses")
def get_expenses(category: Optional[str] = None, month: Optional[str] = None):
    db = get_db()
    query = db.query(Expense)
    
    if category:
        query = query.filter(Expense.category == category)
    
    if month:
        # month format: "2026-04"
        query = query.filter(Expense.date.like(f"{month}%"))
    
    return query.all()

@app.post("/expenses", status_code=201)
def create_expense(expense: ExpenseSchema):
    db = get_db()
    new_expense = Expense(
    amount=expense.amount,
    category=expense.category,
    description=expense.description,
    date=expense.date
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

class ExpenseUpdateSchema(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None

@app.patch("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseUpdateSchema):
    db = get_db()
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if expense.amount is not None:
        db_expense.amount = expense.amount
    if expense.category is not None:
        db_expense.category = expense.category
    if expense.description is not None:
        db_expense.description = expense.description
    if expense.date is not None:
        db_expense.date = expense.date
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    db = get_db()
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="expense not found")
    db.delete(db_expense)
    db.commit()
    return None

