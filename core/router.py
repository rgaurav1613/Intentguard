import os

def deliver_output(df, output_path):
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "intentguard_output.csv")
    df.to_csv(output_file, index=False)
    return output_file
