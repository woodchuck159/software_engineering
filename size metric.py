import time

def calculate_size_score(model_size_bytes):

    #for latency 
    start = time.time()
    
    size_mb = model_size_bytes / (1024 * 1024)
    size_gb = model_size_bytes / (1024 * 1024 * 1024)
    
    scores = {}
    
    #Raspberry Pi
    if size_mb <= 100:
        scores["raspberry_pi"] = 1.0
    elif size_mb <= 500:
        scores["raspberry_pi"] = 0.5
    else:
        scores["raspberry_pi"] = 0.0

    #Jetson Nano
    if size_mb <= 500:
        scores["jetson_nano"] = 1.0
    elif size_gb <= 2:
        scores["jetson_nano"] = 0.5
    else:
        scores["jetson_nano"] = 0.0

    #Desktop PC
    if size_gb <= 5:
        scores["desktop_pc"] = 1.0
    elif size_gb <= 10:
        scores["desktop_pc"] = 0.5
    else:
        scores["desktop_pc"] = 0.0

    #AWS Server
    scores["aws_server"] = 1.0

    latency_ms = int((time.time() - start) * 1000)
    return scores, latency_ms

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
