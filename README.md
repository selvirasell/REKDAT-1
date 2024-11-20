Tugas Akhir Rekayasa Data 
========

Kelompok
================
1. Fahrin Ulya Nisrina (22/497708/TK/54557)
2. Aisa Selvira Quraata Ayunni (22/498561/TK/54690)


LINK PENTING 
===========================
1. LINK COLAB MODELLING DATA : https://colab.research.google.com/drive/15Shr4EIDd1E_84AP1CtwRveR4JD_dmgc?authuser=2#scrollTo=JNZyRWCOSjbb
2. LINK GITHUB MODELLING DATA : https://github.com/fahrinulyanisrina/TugasAkhirRekayasaData.git
3. LINK BLOG NOTION : https://pleasant-shear-ca4.notion.site/Tugas-Akhir-Rekayasa-Data-End-to-End-Data-Engineering-Project-144b13ad76d180219136c73d17155c3f?pvs=4 
4. LINK VIDEO PRESENTASI : https://drive.google.com/file/d/1kq0Sahd3dYy8E87GWSepNaEbQvOhBgT5/view?usp=sharing
   

Overview
========

This project was generated after you ran 'astro dev init' using the Astronomer CLI. 

Deploy Project Locally
===========================

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 4 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks

2. Verify that all 4 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start the project with the Airflow Webserver exposed at port 8080 and Postgres exposed at port 5432. 

3. Access the Airflow UI for local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.


