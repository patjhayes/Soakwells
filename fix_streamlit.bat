@echo off
echo Fixing Streamlit configuration...
mkdir %USERPROFILE%\.streamlit 2>nul

echo [general] > %USERPROFILE%\.streamlit\credentials.toml
echo email = "" >> %USERPROFILE%\.streamlit\credentials.toml

echo [general] > %USERPROFILE%\.streamlit\config.toml
echo email = "" >> %USERPROFILE%\.streamlit\config.toml
echo. >> %USERPROFILE%\.streamlit\config.toml
echo [browser] >> %USERPROFILE%\.streamlit\config.toml
echo gatherUsageStats = false >> %USERPROFILE%\.streamlit\config.toml

echo Configuration files created.
echo Now try running: python -m streamlit run soakwell_dashboard.py --server.port 8505
pause
