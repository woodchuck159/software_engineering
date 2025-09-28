
import json
import sys

def build_model_output(
    name,
    category,
    scores,
    latency
):
    output = {
        "name": name,
        "category": category,
        "net_score": scores["net_score"],
        "net_score_latency": latency["net_score_latency"],
        "ramp_up_time": scores["rampup_time_metric"],
        "ramp_up_time_latency": latency["rampup_time_metric"],
        "bus_factor": scores["bus_factor_metric"],
        "bus_factor_latency": latency["bus_factor_metric"],
        "performance_claims": scores["performance_claims_metric"],
        "performance_claims_latency": latency["performance_claims_metric"],
        "license": scores["calculate_license_score"],
        "license_latency": latency["calculate_license_score"],
        "size_score": scores["calculate_size_score"],  
        "size_score_latency": latency["calculate_size_score"],
        "dataset_and_code_score": scores["dataset_metric"],
        "dataset_and_code_score_latency": latency["dataset_metric"],
        "dataset_quality": scores["dataset_quality"],
        "dataset_quality_latency": latency["dataset_quality"],
        "code_quality": scores["code_quality"],
        "code_quality_latency": latency["code_quality"]
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
