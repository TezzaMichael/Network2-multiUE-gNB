import json


def generate_json(nUE):
    data = {
        "subscribers": []
    }

    for i in range(1, nUE+1):
        subscriber = {
            "imsi": f"0010112345678{i:02d}",
            "subscribed_rau_tau_timer": 12,
            "network_access_mode": 0,
            "subscriber_status": 0,
            "access_restriction_data": 32,
            "slice": [
                {
                    "sst": 1,
                    "default_indicator": True,
                    "sd": "000001",
                    "session": [
                        {
                            "name": "internet",
                            "type": 3,
                            "pcc_rule": [],
                            "ambr": {
                                "Comment": "unit=2 ==> Mbps",
                                "uplink":   {"value": 5*i, "unit": 2},
                                "downlink": {"value": 5*i, "unit": 2}
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
                                "uplink":   {"value": 40 + 10*i, "unit": 2},
                                "downlink": {"value": 40 + 10*i, "unit": 2}
                            },
                            "qos": {
                                "index": 8,
                                "arp": {"priority_level": 15, "pre_emption_capability": 1, "pre_emption_vulnerability": 1}
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

        # Aggiungi il subscriber alla lista
        data["subscribers"].append(subscriber)

    with open('./python_modules/subscribers.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data


if __name__ == "__main__":
    generate_json(10)
