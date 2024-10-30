import pandas as pd
import random
import os


def preprocess_data(input_file, output_file):
    try:
        df = pd.read_csv(input_file)

        # 1. Handle Image Paths:  Create if not present or update if needed.
        image_dir = "product_images"  # Directory to store images
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        if "image_path" not in df.columns:
            df["image_path"] = (
                ""  # Add empty image_path column if it's missing.  Important for later error handling.
            )

        # If you want to rename images and update paths systematically (example):
        # for index, row in df.iterrows():
        #     new_image_name = f"{row['product_id']}.jpg"  # Or use a different format
        #     new_image_path = os.path.join(image_dir, new_image_name)
        #     df.loc[index, "image_path"] = new_image_path

        # 2. Create or Convert Price:
        if "Price (INR)" in df.columns:
            df["price"] = (
                df["Price (INR)"]
                .apply(
                    lambda x: float(str(x).replace(",", "")) * 0.012
                    if isinstance(x, str) and "," in x
                    else float(x) * 0.012
                    if x
                    else 0.00
                )
                .round(2)
            )  # Example INR to USD
        elif "price" not in df.columns:
            df["price"] = [
                round(random.uniform(10, 100), 2) for _ in range(len(df))
            ]  # Generate random if not provided

        # 3. Select required columns (in desired order)
        df = df[["product_id", "description", "title", "image_path", "price"]]

        # 4. Save to CSV
        df.to_csv(output_file, index=False)
        print(f"Preprocessed data saved to {output_file}")

    except FileNotFoundError:
        print
