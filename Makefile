.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline:
	python pipeline/load_data.py
	python pipeline/InitialAnalysis.py
	python pipeline/StatistialAnalysis.py
	python pipeline/DataSubsetAnalysis.py

dashboard:
	streamlit run InteractiveDashboard.py