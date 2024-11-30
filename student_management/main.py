from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from dotenv import load_dotenv
import os
load_dotenv() 
app = FastAPI()


MONGO_URL = os.getenv("MONGO_URL")
print(MONGO_URL)
client = AsyncIOMotorClient(MONGO_URL)
db = client["student_management"]

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class UpdateStudent(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[Address] = None

@app.post("/students", status_code=201)
async def create_student(student: Student):
    student = jsonable_encoder(student)
    result = await db["students"].insert_one(student)
    return {"id": str(result.inserted_id)}

@app.get("/students", status_code=200)
async def list_students(country: Optional[str] = None, age: Optional[int] = None):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = await db["students"].find(query).to_list(100)
    return {"data": [{"name": s["name"], "age": s["age"]} for s in students]}

@app.get("/students/{id}", status_code=200)
async def get_student(id: str):
    try:
        student_id = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    student = await db["students"].find_one({"_id": student_id})

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "name": student["name"],
        "age": student["age"],
        "address": student["address"],
    }

@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student: UpdateStudent):
    update_data = {k: v for k, v in student.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        student_id = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = await db["students"].update_one({"_id": student_id}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student updated successfully"}

@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str):
    try:
        student_id = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = await db["students"].delete_one({"_id": student_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"}
