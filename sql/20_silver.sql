DROP TABLE IF EXISTS silver.coco;
CREATE TABLE silver.coco AS
SELECT DISTINCT
    image_id,
    image_uri,
    CAST(width AS INTEGER) AS width,
    CAST(height AS INTEGER) AS height,
    bbox_id,
    CAST(category AS INTEGER) AS category_id,
    bbox
FROM raw.coco_annotations
WHERE bbox IS NOT NULL;

ALTER TABLE silver.coco ADD COLUMN bbox_area DOUBLE;
UPDATE silver.coco SET bbox_area = bbox[3] * bbox[4];

DROP TABLE IF EXISTS silver.visdrone;
CREATE TABLE silver.visdrone AS
SELECT DISTINCT
    clip_id,
    clip_uri,
    fragment_id,
    fragment_uri,
    CAST(start_frame AS INTEGER) AS start_frame,
    CAST(end_frame AS INTEGER) AS end_frame,
    start_time,
    end_time,
    CAST(n_objects AS INTEGER) AS n_objects,
    classes
FROM raw.visdrone_fragments;
