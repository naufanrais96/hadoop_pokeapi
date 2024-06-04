# Tutorial ETL from pokeapi.co to HDFS by docker-compose
Notes: In this project, we get the data from https://pokeapi.co/api/v2/ability/ability_id using python and generate CSV files per 100 ability_id. Then, we store all CSV files into HDFS

#1. Create a folder to store the project called ‘hadoop_pokeapi’

#2. Create a file in that folder called ‘docker-compose.yml’ and store the yaml format. 

This docker-compose contains namenode image, datanode image, and python image. We created these 3 image as python will run a script to generate csv pokeapi and store it in the same environment to our hadoop (namenode)

Script:

version: '3.8'


services:
 namenode:
   image: bde2020/hadoop-namenode:2.0.0-hadoop2.7.4-java8
   container_name: namenode
   platform: linux/amd64
   environment:
     - CLUSTER_NAME=test
     - CORE_CONF_fs_defaultFS=hdfs://namenode:8020
     - HDFS_CONF_dfs_replication=1
   ports:
     - "9870:9870"
     - "9000:9000"
   volumes:
     - namenode_data:/hadoop/dfs/name
     - shared_data:/shared
   networks:
     - hadoop


 datanode:
   image: bde2020/hadoop-datanode:2.0.0-hadoop2.7.4-java8
   container_name: datanode
   platform: linux/amd64
   environment:
     - CORE_CONF_fs_defaultFS=hdfs://namenode:8020
   volumes:
     - datanode_data:/hadoop/dfs/data
   networks:
     - hadoop
   depends_on:
     - namenode


 python:
   build:
     context: .
     dockerfile: Dockerfile.python
   container_name: python_container
   volumes:
     - shared_data:/app/output
   networks:
     - hadoop
   depends_on:
     - namenode


volumes:
 namenode_data:
 datanode_data:
 shared_data:


networks:
 hadoop:

#3. Create an python image that run a script to store the pokebase api and generate the csv file

Script:

import requests
import csv


--this function connects to pokeapi ability
def fetch_ability_details(ability_id):
   url = f"https://pokeapi.co/api/v2/ability/{ability_id}"
   response = requests.get(url)
   if response.status_code == 200:
       return response.json()
   else:
       return None


--this function save the result to csv
def save_to_csv(abilities, filename):
   with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
       fieldnames = ['id', 'pokemon_ability_id', 'effect', 'language', 'short_effect']
       writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
       writer.writeheader()
       for ability in abilities:
           writer.writerow(ability)


--main function to connects to pokeapi ability, save it to csv based on the format
def main():
   abilities = []
   for i in range(1, 1000):
       ability_data = fetch_ability_details(i)
       if ability_data:
           effect_entries = ability_data.get('effect_entries', [])
           if effect_entries:
               abilities.append({
                   'id': i,
                   'pokemon_ability_id': ability_data['id'],
                   'effect': effect_entries[0].get('effect', ''),
                   'language': effect_entries[0].get('language', {}).get('name', ''),
                   'short_effect': effect_entries[0].get('short_effect', '')
               })
       if i % 100 == 0:
           save_to_csv(abilities, f'result_{i-99}_{i}.csv')
           abilities = []


--execute the main function
if __name__ == "__main__":
   main()

#4. Create requirements.txt and store a word ‘requests’ as this will be a module that will be installed in our python docker environment.

#5. Create a Dockerfile.python that runs a python container in docker

Script:
FROM python:3.9


-- Create a directory to store the script and CSV files
WORKDIR /app/output/


COPY requirements.txt /app/output/
RUN pip install --no-cache-dir -r requirements.txt


-- Copy the Python script into the container
COPY hit_pokeapi.py /app/output/


-- Run the Python script to generate CSV files
CMD ["python3", "hit_pokeapi.py"] 

#6. Create a file called ‘config’ and store the config from https://hub.docker.com/r/apache/hadoop 

#7. Open the terminal and go to that folder. Run:

docker-compose up id to create a hadoop environment --> It will run the Dockerfile.python, generate all csv files and store it in the docker directory. 
docker exec -it python_container /bin/bash --> run python container --> Type ls too see csv files are generated or not.
docker exec -it namenode /bin/bash --> run a namenode container.
ls /shared --> see if the csv files are generated or not. We will see that csv files are ready in shared volume (the shared folder which can be copied to another container which is hadoop). Next type exit to exit the python container.
docker-compose exec namenode hadoop fs -mkdir -p /path/in/hdfs/ --> create a folder in hadoop environment in namenode container.
docker exec namenode bash -c 'for file in /shared/*.csv; do hadoop fs -put "$file" /path/in/hdfs/; done' --> copy all csv files from namenode container to our hadoop environment.
docker-compose exec namenode hadoop fs -ls /path/in/hdfs/ --> check if the files are uploaded or not.


