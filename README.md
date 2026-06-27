# AI Lakehouse

This is my CS375 project. It is a small data lakehouse that keeps track of every version of the data. I used DuckLake for the catalog, RustFS for storage (it works like an S3 bucket), and DuckDB to run the SQL. The data is two datasets: COCO, which is images, and VisDrone, which is drone video. One of the final tables gets pushed up to Hugging Face.

## How the layers work

The data goes through three stages.

* raw is the data exactly how it came in. The big stuff like images and video is saved as files in RustFS, and the tables only keep the links and some info like labels and boxes.
* silver is the cleaned up version. I remove duplicates, fix the column types, and drop bad rows. I also add one new column here (bbox_area) to show schema evolution.
* gold is the final version that is ready for machine learning. It has labels and a train and val split.

## What you need

* Docker Desktop running
* A Hugging Face account with a Write token

## Getting started

1. Make a file called .env in this folder and put your token in it:

       HF_TOKEN=your_token_here

2. Start everything:

       docker compose up -d

3. Go into the lab container:

       docker compose exec lab bash

4. Install the python packages (the container starts fresh, so you do this each time it is rebuilt):

       pip install duckdb datasets pillow boto3 pandas

## Building the lakehouse

Run these inside the lab container:

       python scripts/10_land_coco.py
       python scripts/11_land_visdrone.py
       python scripts/20_build_layers.py

## Rebuilding from scratch

If you want to wipe the bucket and build the whole thing again with one command, run this inside the lab container:

       ./rebuild.sh

## Hugging Face round trip

       python scripts/30_hf_roundtrip.py

This grabs some new COCO rows into raw and then pushes the gold table back up to Hugging Face.

My dataset is here: https://huggingface.co/datasets/jeangardy810/lakehouse-coco-gold

## What is in the repo

* docker-compose.yml runs RustFS and the lab container
* rebuild.sh wipes the bucket and rebuilds everything
* sql/ has the attach, silver, and gold SQL
* scripts/ has the landing, building, time travel, and Hugging Face scripts
* .env has my token and is ignored by git
