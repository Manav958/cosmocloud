
if ($IsWindows) {
    Write-Host "Running on Windows"
    
    Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "main:app", "--host", "localhost", "--port", "8000"
} else {
    Write-Host "Running on Linux"
    
    uvicorn main:app --host localhost --port 8000
}
