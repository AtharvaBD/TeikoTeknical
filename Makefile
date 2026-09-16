.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python pipeline/InitialAnalysis.py
	python pipeline/StatistialAnalysis.py
	python pipeline/DataSubsetAnalysis.py
	python avgb_cell.py

dashboard:
	streamlit run InteractiveDashboard.py