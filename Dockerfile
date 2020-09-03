FROM python:3.7
EXPOSE 8501
WORKDIR /or_finder
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD streamlit run orienteering_race_finder_CH.py