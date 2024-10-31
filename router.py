from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session, load_only

from function import save_in_db, get_in_db
from db import database
from models.answer import Answers
from models.question import Questions
from models.science import Sciences

tests_router = APIRouter(
    prefix="/test",
    tags=["Test operatsiyalari"]
)


@tests_router.post('/add_science')
def create(science_name: str, db: Session = Depends(database)):
    new_item = Sciences(
        name=science_name
    )
    save_in_db(db, new_item)
    raise HTTPException(200, 'success')


@tests_router.get('/get_science')
def get(db: Session = Depends(database)):
    return db.query(Sciences).all()


@tests_router.get('/get_question')
def get(db: Session = Depends(database)):
    return db.query(Questions).all()


@tests_router.get('/get_answer')
def get(db: Session = Depends(database)):
    return db.query(Answers).all()


@tests_router.get('/get_tests')
async def get_test_f(science_id: int, db: Session = Depends(database)):
    await get_in_db(db, Sciences, science_id)
    questions = (db.query(Questions).options(load_only(Questions.text))
                       .filter(Questions.science_id == science_id).all())
    result = []
    for question in questions:
        answers = db.query(Answers).filter(Answers.question_id == question.id).all()
        result.append({
            "question": question,
            "answers": [{
                "text": answer.text,
                'status': answer.status} for answer in answers]
        })

    return {"data": result}


@tests_router.post('/upload_test/{science_id}')
async def upload_txt(science_id: int, file: UploadFile = File(...), db: Session = Depends(database)):
    await get_in_db(db, Sciences, science_id)
    content = await file.read()
    content_str = content.decode("utf-8-sig")

    questions_data = content_str.strip().split("+++++")
    created_questions = []

    for question_data in questions_data:
        lines = question_data.strip().split("====")
        if len(lines) < 2:
            continue

        question_text = lines[0].strip()
        options = []
        correct_option_index = None

        for idx, line in enumerate(lines[1:], start=0):
            line = line.strip()
            if line.startswith("#"):
                option_text = line[1:].strip()
                correct_option_index = idx
            else:
                option_text = line
            options.append(option_text)

        if correct_option_index is None:
            raise HTTPException(status_code=400, detail=f"No correct option found for question: "
                                                        f"{question_text}")

        db_question = Questions(text=question_text, science_id=science_id)
        save_in_db(db, db_question)

        db_options = []
        for idx, option_text in enumerate(options):
            is_correct = (idx == correct_option_index)
            db_option = Answers(text=option_text, status=is_correct, question_id=db_question.id)
            save_in_db(db, db_option)
            db_options.append(db_option)

        created_questions.append({
            "id": db_question.id,
            "question_text": db_question.text,
            "options": [{"id": opt.id, "text": opt.text, "is_correct": opt.status} for opt in db_options]
        })

    return created_questions

#
# @tests_router.post('/upload_test_excel/{science_id}')
# async def upload_tests_from_excel(science_id: int, file: UploadFile = File(...), db: Session = Depends(database)):
#     if not file.filename.endswith(('.xlsx', '.xls')):
#         raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")
#
#     content = await file.read()
#     file_path = "/mnt/data/uploaded_test.xlsx"
#     with open(file_path, "wb") as f:
#         f.write(content)
#
#     # Excel faylini o'qish
#     workbook = xlrd.open_workbook(file_path)
#     sheet = workbook.sheet_by_index(0)  # Birinchi varaqni olish
#
#     created_questions = []
#
#     for row_idx in range(1, sheet.nrows):  # 1-qator sarlavhalarni o'tkazish
#         row = sheet.row(row_idx)
#         question_text = row[0].value  # 1-ustun (savollar)
#         correct_answer = row[1].value  # 2-ustun (to'g'ri javob)
#
#         options = [cell.value for cell in row[2:] if cell.value is not None]  # 3-ustundan boshlanadi
#
#         if question_text is None or correct_answer is None:
#             continue
#
#         try:
#             correct_option_index = options.index(correct_answer)
#         except ValueError:
#             raise HTTPException(status_code=400, detail=f"No correct answer found for question: {question_text}")
#
#         db_question = Questions(text=question_text, science_id=science_id)
#         save_in_db(db, db_question)
#
#         db_options = []
#         for idx, option_text in enumerate(options):
#             is_correct = (idx == correct_option_index)
#             db_option = Answers(text=option_text, status=is_correct, question_id=db_question.id)
#             save_in_db(db, db_option)
#             db_options.append(db_option)
#
#         created_questions.append({
#             "id": db_question.id,
#             "question_text": db_question.text,
#             "options": [{"id": opt.id, "text": opt.text, "is_correct": opt.status} for opt in db_options]
#         })
#
#     if not created_questions:
#         raise HTTPException(status_code=400, detail="No valid questions uploaded.")
#
#     return {"status": "All questions and answers uploaded successfully", "questions": created_questions}
