
import json

def build_model_output(
    name,
    category,
    net_score,
    net_score_latency,
    ramp_up_time,
    ramp_up_time_latency,
    bus_factor,
    bus_factor_latency,
    performance_claims,
    performance_claims_latency,
    license,
    license_latency,
    size_score,
    size_score_latency,
    dataset_and_code_score,
    dataset_and_code_score_latency,
    dataset_quality,
    dataset_quality_latency,
    code_quality,
    code_quality_latency
):
    
    output = {
        "name": name,
        "category": category,
        "net_score": net_score,
        "net_score_latency": net_score_latency,
        "ramp_up_time": ramp_up_time,
        "ramp_up_time_latency": ramp_up_time_latency,
        "bus_factor": bus_factor,
        "bus_factor_latency": bus_factor_latency,
        "performance_claims": performance_claims,
        "performance_claims_latency": performance_claims_latency,
        "license": license,
        "license_latency": license_latency,
        "size_score": size_score,  
        "size_score_latency": size_score_latency,
        "dataset_and_code_score": dataset_and_code_score,
        "dataset_and_code_score_latency": dataset_and_code_score_latency,
        "dataset_quality": dataset_quality,
        "dataset_quality_latency": dataset_quality_latency,
        "code_quality": code_quality,
        "code_quality_latency": code_quality_latency
    }

    #print to stdout
    print(json.dumps(output))

#testing
if __name__ == "__main__":
    build_model_output(
        name="google/gemma-3-270m",
        category="MODEL",
        net_score=0.82,
        net_score_latency=1001,
        ramp_up_time=0.75,
        ramp_up_time_latency=123,
        bus_factor=0.6,
        bus_factor_latency=88,
        performance_claims=0.8,
        performance_claims_latency=110,
        license=1.0,
        license_latency=95,
        size_score={
            "raspberry_pi": 0.2,
            "jetson_nano": 0.4,
            "desktop_pc": 0.9,
            "aws_server": 1.0,
        },
        size_score_latency=200,
        dataset_and_code_score=0.9,
        dataset_and_code_score_latency=130,
        dataset_quality=0.85,
        dataset_quality_latency=115,
        code_quality=0.7,
        code_quality_latency=140,
    )
