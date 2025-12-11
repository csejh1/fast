from fastapi import FastAPI


from domain.question import question_router
#
from domain.answer import answer_router
#
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/hello")
# def hello():
#     return {"message": "hello world"}


app.include_router(question_router.router)
# include_router는 함수고, question_router.py의 router는 /api/question으로 잡아놓음.
# 결국 누군가 main.app의 /api/question으로 오면 domain\question\question_router.py로 전달


#
app.include_router(answer_router.router)
#

@app.get("/hello")
def hello():
    return {"message": "안녕하세요 파이보"}

@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}
#####################
