DROP TABLE IF EXISTS gold.coco_train;
CREATE TABLE gold.coco_train AS
WITH per_image AS (
    SELECT image_id,
           any_value(image_uri) AS image_uri,
           mode(category_id) AS label,
           count(*) AS n_objects
    FROM silver.coco
    GROUP BY image_id
)
SELECT image_id, image_uri, label, n_objects,
       CASE WHEN image_id % 5 = 0 THEN 'val' ELSE 'train' END AS split
FROM per_image;

DROP TABLE IF EXISTS gold.visdrone_train;
CREATE TABLE gold.visdrone_train AS
SELECT fragment_uri, clip_id, start_frame, end_frame, n_objects, classes,
       CASE WHEN n_objects > 20 THEN 1 ELSE 0 END AS is_busy,
       CASE WHEN fragment_id % 5 = 0 THEN 'val' ELSE 'train' END AS split
FROM silver.visdrone;
