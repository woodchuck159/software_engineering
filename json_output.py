
import json
import sys

def build_model_output(
    name,
    category,
    scores,
    latency
):
    output = {
    "name":name,
    "category":category.upper(),
    "net_score":scores.get("net_score", 0.00),
    "net_score_latency":latency.get("net_score_latency", 0),
    "ramp_up_time":scores.get("rampup_time_metric", 0.00),
    "ramp_up_time_latency":latency.get("rampup_time_metric", 0),
    "bus_factor":scores.get("bus_factor_metric", 0.00),
    "bus_factor_latency":latency.get("bus_factor_metric", 0),
    "performance_claims":scores.get("performance_claims_metric", 0.00),
    "performance_claims_latency":latency.get("performance_claims_metric", 0),
    "license":scores.get("calculate_license_score", 0.00),
    "license_latency":latency.get("calculate_license_score", 0),
    "size_score":scores.get("calculate_size_score", 0.00),  
    "size_score_latency":latency.get("calculate_size_score", 0),
    "dataset_and_code_score":scores.get("dataset_and_code_present", 0.00),
    "dataset_and_code_score_latency":latency.get("dataset_and_code_present", 0),
    "dataset_quality":scores.get("dataset_quality", 0.00),
    "dataset_quality_latency":latency.get("dataset_quality", 0),
    "code_quality":scores.get("code_quality", 0.00),
    "code_quality_latency":latency.get("code_quality", 0),
}
    #return output

    #print to stdout
    sys.stdout.write(json.dumps(output) + "\n")

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
