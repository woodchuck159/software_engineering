import time

def calculate_size_score(model_size_bytes, verbose):

    if verbose == 1:
        print(f"[INFO] Starting size score calculation for model of {model_size_bytes} bytes...")

    #for latency 
    start = time.time()
    
    size_mb = model_size_bytes / (1024 * 1024)
    size_gb = model_size_bytes / (1024 * 1024 * 1024)

    if verbose == 1:
        print(f"[INFO] Model size: {size_mb:.2f} MB ({size_gb:.2f} GB)")

    
    scores = {}
    
    #Raspberry Pi
    if size_mb <= 100:
        scores["raspberry_pi"] = 1.0
    elif size_mb <= 500:
        scores["raspberry_pi"] = 0.5
    else:
        scores["raspberry_pi"] = 0.0

    if verbose == 1:
        print(f"[INFO] Raspberry Pi score: {scores['raspberry_pi']}")


    #Jetson Nano
    if size_mb <= 500:
        scores["jetson_nano"] = 1.0
    elif size_gb <= 2:
        scores["jetson_nano"] = 0.5
    else:
        scores["jetson_nano"] = 0.0

    if verbose == 1:
        print(f"[INFO] Jetson Nano score: {scores['jetson_nano']}")


    #Desktop PC
    if size_gb <= 5:
        scores["desktop_pc"] = 1.0
    elif size_gb <= 10:
        scores["desktop_pc"] = 0.5
    else:
        scores["desktop_pc"] = 0.0

    if verbose == 1:
        print(f"[INFO] Desktop PC score: {scores['desktop_pc']}")


    #AWS Server
    scores["aws_server"] = 1.0

    if verbose == 1:
        print(f"[INFO] AWS Server score: {scores['aws_server']}")


    latency_ms = int((time.time() - start) * 1000)

    if verbose == 1:
        print(f"[INFO] Finished calculation. Latency={latency_ms}ms")


    return scores, latency_ms

'''
# ---------------- Example Usage ----------------
if __name__ == "__main__":
    # Example model sizes in bytes
    model_sizes = [
        ("small_model", 50*1024*1024),      # 50MB
        ("medium_model", 600*1024*1024),    # 600MB
        ("large_model", 8*1024*1024*1024),  # 8GB
        ("huge_model", 12*1024*1024*1024),  # 12GB
    ]

    for name, size in model_sizes:
        scores, latency = calculate_size_score(size)
        print(f"{name} -> Scores: {scores}, Latency: {latency} ms")
'''
