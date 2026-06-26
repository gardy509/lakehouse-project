from datasets import load_dataset
print("loading a few COCO rows (streaming, no full download)...")
ds = load_dataset("detection-datasets/coco", split="val", streaming=True)
ex = next(iter(ds))
print("\nCOLUMNS:", list(ex.keys()))
print("\nONE EXAMPLE (truncated):")
for k, v in ex.items():
    print(f"  {k}: {type(v).__name__} = {str(v)[:160]}")
