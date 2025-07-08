http://127.0.0.1:8000/api/configuration/ get
{
    "question": {
        "id": 1,
        "name": "PROJE NEDİR?",
        "question_type": "text_input",
        "category_type": "master_question",
        "is_required": true,
        "order": 10,
        "variant_order": 10,
        "relations": [
            {
                "id": 1,
                "relation_type": "master",
                "relation_type_display": "Master İlişki",
                "options": []
            }
        ],
        "applicable_brands": [],
        "applicable_categories": []
    },
    "message": "İlk soru 'PROJE NEDİR?' ile başlar."
}

post

{
    "question_id": 1, 
    "answer": "İSTANBUL AFM"
}

{
    "question": {
        "id": 2,
        "name": "MARKA VE SATIŞ TİPİ NEDİR?",
        "question_type": "multiple_choice",
        "category_type": "master_question",
        "is_required": true,
        "order": 20,
        "variant_order": 20,
        "applicable_brands": [],
        "applicable_categories": []
    },
    "options": [
        {
            "id": 3,
            "name": "GIRSBERGER",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": "A034",
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                15,
                14,
                13,
                16,
                12
            ],
            "applicable_product_models": [
                83,
                84,
                82,
                81,
                86,
                87,
                90,
                88,
                91,
                97,
                95,
                94,
                89,
                93,
                92,
                96,
                66,
                67,
                68,
                78,
                69,
                77,
                70,
                80,
                71,
                72,
                79,
                73,
                74,
                75,
                76,
                85,
                98,
                99,
                100,
                101,
                104,
                103,
                106,
                105,
                102,
                107,
                108,
                109,
                110,
                111
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                3
            ]
        },
        {
            "id": 1,
            "name": "TUNA SİPARİŞ (RENKLİ KOD)",
            "price_modifier": "0.00",
            "color_status": "colored",
            "variant_code_part": "30",
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                6,
                7,
                8,
                10,
                9,
                11,
                1,
                5,
                3,
                2,
                4,
                17
            ],
            "applicable_product_models": [
                48,
                112,
                114,
                113,
                42,
                45,
                46,
                44,
                43,
                41,
                65,
                147,
                116,
                131,
                115,
                130,
                126,
                123,
                129,
                118,
                122,
                132,
                127,
                119,
                121,
                133,
                124,
                134,
                120,
                128,
                135,
                125,
                117,
                143,
                141,
                136,
                146,
                137,
                144,
                145,
                138,
                140,
                139,
                142,
                1,
                2,
                5,
                3,
                4,
                6,
                7,
                25,
                19,
                31,
                20,
                34,
                23,
                21,
                22,
                27,
                30,
                24,
                32,
                26,
                35,
                28,
                36,
                33,
                29,
                37,
                14,
                8,
                12,
                9,
                11,
                18,
                13,
                17,
                16,
                10,
                15,
                38,
                40,
                39,
                53,
                47,
                52,
                64,
                62,
                63,
                61,
                60,
                57,
                51,
                50,
                49,
                59,
                56,
                58,
                54,
                55
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 2,
            "name": "TUNA TEKLİF (RENKSİZ KOD)",
            "price_modifier": "0.00",
            "color_status": "colorless",
            "variant_code_part": "30",
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                6,
                7,
                8,
                10,
                9,
                11,
                1,
                5,
                3,
                2,
                4,
                17
            ],
            "applicable_product_models": [
                48,
                112,
                114,
                113,
                42,
                45,
                46,
                44,
                43,
                41,
                65,
                147,
                116,
                131,
                115,
                130,
                126,
                123,
                129,
                118,
                122,
                132,
                127,
                119,
                121,
                133,
                124,
                134,
                120,
                128,
                135,
                125,
                117,
                143,
                141,
                136,
                146,
                137,
                144,
                145,
                138,
                140,
                139,
                142,
                1,
                2,
                5,
                3,
                4,
                6,
                7,
                25,
                19,
                31,
                20,
                34,
                23,
                21,
                22,
                27,
                30,
                24,
                32,
                26,
                35,
                28,
                36,
                33,
                29,
                37,
                14,
                8,
                12,
                9,
                11,
                18,
                13,
                17,
                16,
                10,
                15,
                38,
                40,
                39,
                53,
                47,
                52,
                64,
                62,
                63,
                61,
                60,
                57,
                51,
                50,
                49,
                59,
                56,
                58,
                54,
                55
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        }
    ],
    "variant_info": {
        "variant_code": "",
        "variant_description": "",
        "total_price": 0.0
    },
    "variant_id": 52
}

{
    "variant_id": 1,
    "question_id": 2,
    "answer": 1
}

{
    "question": {
        "id": 3,
        "name": "GRUP NEDİR?",
        "question_type": "multiple_choice",
        "category_type": "master_question",
        "is_required": true,
        "order": 30,
        "variant_order": 30,
        "applicable_brands": [],
        "applicable_categories": []
    },
    "options": [
        {
            "id": 5,
            "name": "DEPOLAMA",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                6,
                7,
                8
            ],
            "applicable_product_models": [
                112,
                114,
                113,
                42,
                45,
                46,
                44,
                43,
                41,
                65
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 7,
            "name": "DÖŞEMELİ",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                10,
                9,
                11
            ],
            "applicable_product_models": [
                147,
                116,
                131,
                115,
                130,
                126,
                123,
                129,
                118,
                122,
                132,
                127,
                119,
                121,
                133,
                124,
                134,
                120,
                128,
                135,
                125,
                117,
                143,
                141,
                136,
                146,
                137,
                144,
                145,
                138,
                140,
                139,
                142
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 4,
            "name": "MASA",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                1,
                5,
                3,
                2,
                4
            ],
            "applicable_product_models": [
                1,
                2,
                5,
                3,
                4,
                6,
                7,
                25,
                19,
                31,
                20,
                34,
                23,
                21,
                22,
                27,
                30,
                24,
                32,
                26,
                35,
                28,
                36,
                33,
                29,
                37,
                14,
                8,
                12,
                9,
                11,
                18,
                13,
                17,
                16,
                10,
                15,
                38,
                40,
                39
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 6,
            "name": "SANDALYE",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                15,
                14,
                13,
                16,
                12
            ],
            "applicable_product_models": [
                83,
                84,
                82,
                81,
                86,
                87,
                90,
                88,
                91,
                97,
                95,
                94,
                89,
                93,
                92,
                96,
                66,
                67,
                68,
                78,
                69,
                77,
                70,
                80,
                71,
                72,
                79,
                73,
                74,
                75,
                76,
                85,
                98,
                99,
                100,
                101,
                104,
                103,
                106,
                105,
                102,
                107,
                108,
                109,
                110,
                111
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                3
            ]
        },
        {
            "id": 8,
            "name": "SEHPA",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                17
            ],
            "applicable_product_models": [
                48,
                53,
                47,
                52,
                64,
                62,
                63,
                61,
                60,
                57,
                51,
                50,
                49,
                59,
                56,
                58,
                54,
                55
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        }
    ],
    "variant_info": {
        "variant_code": "30",
        "variant_description": "",
        "total_price": 0.0
    },
    "variant_id": 52
}

{
    "variant_id": 53,
    "question_id": 3,
    "answer_data": {
        "option_id": 4
    }
}

{
    "question": {
        "id": 4,
        "name": "KATEGORİ NEDİR?",
        "question_type": "multiple_choice",
        "category_type": "master_question",
        "is_required": true,
        "order": 40,
        "variant_order": 40,
        "applicable_brands": [],
        "applicable_categories": []
    },
    "options": [
        {
            "id": 9,
            "name": "OPERASYONEL",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                1
            ],
            "applicable_product_models": [
                1,
                2,
                5,
                3,
                4,
                6
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 13,
            "name": "SEMİNER",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                5
            ],
            "applicable_product_models": [
                7
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 11,
            "name": "TOPLANTI",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                3
            ],
            "applicable_product_models": [
                66,
                67,
                68,
                78,
                69,
                77,
                70,
                80,
                71,
                72,
                79,
                73,
                74,
                75,
                76,
                25,
                19,
                31,
                20,
                34,
                23,
                21,
                22,
                27,
                30,
                24,
                32,
                26,
                35,
                28,
                36,
                33,
                29,
                37
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 10,
            "name": "YÖNETİCİ",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                2
            ],
            "applicable_product_models": [
                14,
                8,
                12,
                9,
                11,
                18,
                13,
                17,
                16,
                10,
                15
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 12,
            "name": "YÜKSEKLİK AYARLI",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": null,
            "variant_description_part": null,
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                4
            ],
            "applicable_product_models": [
                38,
                40,
                39
            ],
            "applicable_conditions": [],
            "applicable_brands": [
                1
            ]
        }
    ],
    "variant_info": {
        "variant_code": "30",
        "variant_description": "",
        "total_price": 0.0
    },
    "variant_id": 52
}

{
    "variant_id": 53,
    "question_id": 4,
    "answer_data": {
        "option_id": 9
    }
}

{
    "question": {
        "id": 5,
        "name": "TİP NEDİR?",
        "question_type": "multiple_choice",
        "category_type": "conditional_question",
        "is_required": true,
        "order": 50,
        "variant_order": 50,
        "relations": [
            {
                "id": 5,
                "relation_type": "conditional",
                "relation_type_display": "Koşullu İlişki",
                "options": [
                    {
                        "id": 41,
                        "name": "2 Lİ",
                        "price_modifier": "0.00",
                        "color_status": "both",
                        "variant_code_part": "2WS",
                        "variant_description_part": "2Lİ WORKSTATION",
                        "image": null,
                        "is_popular": true,
                        "applicable_categories": [
                            1
                        ],
                        "applicable_product_models": [
                            1,
                            2,
                            5,
                            3,
                            4,
                            6
                        ],
                        "applicable_conditions": [
                            5
                        ],
                        "applicable_brands": [
                            1
                        ]
                    },
                    {
                        "id": 42,
                        "name": "4 LU",
                        "price_modifier": "0.00",
                        "color_status": "both",
                        "variant_code_part": "4WS",
                        "variant_description_part": "4LU WORKSTATION",
                        "image": null,
                        "is_popular": true,
                        "applicable_categories": [
                            1
                        ],
                        "applicable_product_models": [
                            1,
                            2,
                            5,
                            3,
                            4,
                            6
                        ],
                        "applicable_conditions": [
                            5
                        ],
                        "applicable_brands": [
                            1
                        ]
                    },
                    {
                        "id": 43,
                        "name": "6 LI",
                        "price_modifier": "0.00",
                        "color_status": "both",
                        "variant_code_part": "6WS",
                        "variant_description_part": "6LI WORKSTATION",
                        "image": null,
                        "is_popular": true,
                        "applicable_categories": [
                            1
                        ],
                        "applicable_product_models": [
                            1,
                            2,
                            5,
                            3,
                            4,
                            6
                        ],
                        "applicable_conditions": [
                            5
                        ],
                        "applicable_brands": [
                            1
                        ]
                    },
                    {
                        "id": 40,
                        "name": "TEKİL",
                        "price_modifier": "0.00",
                        "color_status": "both",
                        "variant_code_part": "A",
                        "variant_description_part": "TEKİL",
                        "image": null,
                        "is_popular": true,
                        "applicable_categories": [
                            1
                        ],
                        "applicable_product_models": [
                            1,
                            2,
                            5,
                            3,
                            4,
                            6
                        ],
                        "applicable_conditions": [
                            5
                        ],
                        "applicable_brands": [
                            1
                        ]
                    }
                ]
            }
        ],
        "applicable_brands": [
            {
                "id": 1,
                "name": "TUNA"
            }
        ],
        "applicable_categories": [
            {
                "id": 1,
                "name": "OPERASYONEL MASALAR",
                "brand": 1,
                "product_group": 1
            }
        ]
    },
    "options": [
        {
            "id": 41,
            "name": "2 Lİ",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": "2WS",
            "variant_description_part": "2Lİ WORKSTATION",
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                1
            ],
            "applicable_product_models": [
                1,
                2,
                5,
                3,
                4,
                6
            ],
            "applicable_conditions": [
                5
            ],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 42,
            "name": "4 LU",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": "4WS",
            "variant_description_part": "4LU WORKSTATION",
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                1
            ],
            "applicable_product_models": [
                1,
                2,
                5,
                3,
                4,
                6
            ],
            "applicable_conditions": [
                5
            ],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 43,
            "name": "6 LI",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": "6WS",
            "variant_description_part": "6LI WORKSTATION",
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                1
            ],
            "applicable_product_models": [
                1,
                2,
                5,
                3,
                4,
                6
            ],
            "applicable_conditions": [
                5
            ],
            "applicable_brands": [
                1
            ]
        },
        {
            "id": 40,
            "name": "TEKİL",
            "price_modifier": "0.00",
            "color_status": "both",
            "variant_code_part": "A",
            "variant_description_part": "TEKİL",
            "image": null,
            "is_popular": true,
            "applicable_categories": [
                1
            ],
            "applicable_product_models": [
                1,
                2,
                5,
                3,
                4,
                6
            ],
            "applicable_conditions": [
                5
            ],
            "applicable_brands": [
                1
            ]
        }
    ],
    "variant_info": {
        "variant_code": "30",
        "variant_description": "",
        "total_price": 0.0
    },
    "variant_id": 53
}