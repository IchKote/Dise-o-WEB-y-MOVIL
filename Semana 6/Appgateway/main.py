from fastapi import FastAPI

app = FastAPI(
    title="API Gateway", 
    description="API ubicada en localhost enrutada por APway"
)

@app.get("/health")
def health():
    return {"status": "Service 2.0"}


@app.get("/products")
def get_products():
    return [
        {"id": 1, "name": "Notebook", "price": 900000},
        {"id": 2, "name": "Monitor", "price": 250000}
    ]

@app.get("/orders")
def get_orders():
    return [
        {"id": 6001, "status": "pagado"},
        {"id": 6002, "status": "pending"}
    ]