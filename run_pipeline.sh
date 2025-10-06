lternative: Use a shell command

Instead of modifying your script, you can run two commands in sequence:

# Step 1: run your data pipeline
python src/main.py --query "Antimicrobial resistance AND novel antibiotics" --data_collection True

# Step 2: launch Streamlit
streamlit run src/api/app.py