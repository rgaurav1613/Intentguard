import os
from datetime import datetime

def deliver_output(df, output_path):

    os.makedirs(output_path, exist_ok=True)

    filename = f"intentguard_output_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    full_path = os.path.join(output_path, filename)

    df.to_csv(full_path, index=False)

    return full_path
