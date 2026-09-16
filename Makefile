.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python InitialAnalysis.py
	python StatistialAnalysis.py
	python SubsetAnalysis.py

dashboard:
	streamlit run dashboard.py