import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# 1. Catch-all route for any path and any method
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path: str = ""):
    html_content = """
    <html>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: #27ae60;">🚀 Startup Dashboard (Real Server)</h1>
            <p>Welcome, Admin. System Status: <b>ONLINE</b></p>
            <div style="border: 1px solid #ddd; padding: 20px; display: inline-block;">
                <p>💰 Revenue: <b>$1,200,000</b></p>
                <p>🔑 API Key: <b>sk_live_84758374</b></p>
            </div>
            <br><br>
            <small style="color: gray;">(Served by FastAPI Port 3000)</small>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    print("[-] 🚀 Dummy Server Running on http://0.0.0.0:3000")
    uvicorn.run(app, host="0.0.0.0", port=3000)