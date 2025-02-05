import json

def generate_json(nUE):
    """
    Generates a JSON file with subscriber data for a given number of User Equipments (UEs).

    The function generates a JSON structure with subscriber information such as IMSI, network access mode, 
    session data, AMBR (Allocation and Mobility Resource), QoS settings, and security information for each 
    UE. The resulting JSON is saved to a file and also returned as a Python dictionary.

    Args:
        nUE (int): The number of subscribers (User Equipments) to generate.

    Returns:
        dict: The generated JSON data as a Python dictionary.
    """
    
    # Initialize the data structure with an empty subscribers list
    data = {
        "subscribers": []
    }

    # Loop through the number of UEs (nUE) and create subscriber data
    for i in range(1, nUE + 1):
        # Define each subscriber's data
        subscriber = {
            "imsi": f"0010112345678{i:02d}",  # Unique IMSI for each subscriber
            "subscribed_rau_tau_timer": 12,
            "network_access_mode": 0,
            "subscriber_status": 0,
            "access_restriction_data": 32,
            "slice": [
                {
                    "sst": 1,  # Slice Selection Type
                    "default_indicator": True,
                    "sd": "000001",
                    "session": [
                        {
                            "name": "internet",
                            "type": 3,
                            "pcc_rule": [],
                            "ambr": {
                                "Comment": "unit=2 ==> Mbps",
                                "uplink": {"value": 5 * i, "unit": 2},
                                "downlink": {"value": 5 * i, "unit": 2}
                            },
                            "qos": {
                                "index": 8,
                                "arp": {
                                    "priority_level": 15,
                                    "pre_emption_capability": 1,
                                    "pre_emption_vulnerability": 1
                                }
                            }
                        }
                    ]
                },
                {
                    "sst": 2,
                    "default_indicator": None,
                    "sd": "000001",
                    "session": [
                        {
                            "name": "mec",
                            "type": 3,
                            "pcc_rule": [],
                            "ambr": {
                                "Comment": "unit=2 ==> Mbps",
                                "uplink": {"value": 40 + 10 * i, "unit": 2},
                                "downlink": {"value": 40 + 10 * i, "unit": 2}
                            },
                            "qos": {
                                "index": 8,
                                "arp": {
                                    "priority_level": 15,
                                    "pre_emption_capability": 1,
                                    "pre_emption_vulnerability": 1
                                }
                            }
                        }
                    ]
                }
            ],
            "ambr": {
                "Comment": "unit=2 ==> Mbps",
                "uplink": {"value": 1, "unit": 2},
                "downlink": {"value": 1, "unit": 2}
            },
            "security": {
                "k": "8baf473f2f8fd09487cccbd7097c6862",
                "amf": "8000",
                "op": "11111111111111111111111111111111",
                "opc": None
            },
            "msisdn": [],
            "schema_version": 1,
            "__v": 0
        }

        # Add the subscriber to the list
        data["subscribers"].append(subscriber)

    # Write the generated data to a JSON file
    with open('./python_modules/subscribers.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # Return the generated data as a dictionary
    return data


if __name__ == "__main__":
    generate_json(10)  # Generate 10 subscribers (UEs)
