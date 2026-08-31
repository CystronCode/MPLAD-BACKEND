# backend/scripts/generate_karnataka_28_constituencies.py
# Generates rich, authentic UDISE+ schools and e-SAKSHI works across all 28 Karnataka Parliamentary Constituencies

import os
import json

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
MASTER_FILE = os.path.join(DATA_DIR, "karnataka_constituencies_master.json")
SCHOOLS_OUT_FILE = os.path.join(DATA_DIR, "karnataka_all_schools.json")
WORKS_OUT_FILE = os.path.join(DATA_DIR, "karnataka_all_works.json")

# Authentic constituency templates with realistic landmarks and school names
CONSTITUENCY_COHORTS = {
    "KA-01": {"city": "Chikkodi", "schools": ["Government High School Nipani", "Government PU College Chikkodi Main", "Government Model Primary School Hukkeri", "St. Jude English School Chikkodi"]},
    "KA-02": {"city": "Belgaum", "schools": ["Government Sardar High School Belagavi", "Government Model School Camp Belgaum", "Government PU College Tilakwadi", "GHS Shahapur Belgaum"]},
    "KA-03": {"city": "Bagalkot", "schools": ["Government High School Badami", "Government Model Primary School Jamkhandi", "Government PU College Bagalkot", "GHS Ilkal Main"]},
    "KA-04": {"city": "Bijapur", "schools": ["Government High School Gol Gumbaz Road Vijayapura", "Government Model Primary School Indi", "Government PU College Sindagi", "GHS Basavana Bagewadi"]},
    "KA-05": {"city": "Gulbarga", "schools": ["Government High School Super Market Kalaburagi", "Government PU College Sedam", "Government Model School Aland", "St. Mary English Academy Gulbarga"]},
    "KA-06": {"city": "Raichur", "schools": ["Government High School Station Road Raichur", "Government Model Primary School Sindhanur", "Government PU College Manvi", "GHS Lingasugur"]},
    "KA-07": {"city": "Bidar", "schools": ["Government High School Fort Road Bidar", "Government Model School Basavakalyan", "Government PU College Humnabad", "GHS Bhalki"]},
    "KA-08": {"city": "Koppal", "schools": ["Government High School Gangavathi", "Government Model Primary School Kushtagi", "Government PU College Koppal", "GHS Yelburga"]},
    "KA-09": {"city": "Bellary", "schools": ["Government High School Cantonment Ballari", "Government Model Primary School Hospet", "Government PU College Siruguppa", "GHS Sandur"]},
    "KA-10": {"city": "Haveri", "schools": ["Government High School Ranebennur", "Government Model Primary School Haveri", "Government PU College Byadgi", "GHS Hangal"]},
    "KA-11": {"city": "Dharwad", "schools": ["Government High School Station Road Hubballi", "Government Model Primary School Dharwad Old Town", "Government PU College Navalgund", "GHS Kalghatgi"]},
    "KA-12": {"city": "Uttara Kannada", "schools": ["Government High School Karwar Beach Road", "Government Model Primary School Sirsi", "Government PU College Kumta", "GHS Bhatkal"]},
    "KA-13": {"city": "Davanagere", "schools": ["Government High School PJ Extension Davanagere", "Government Model Primary School Harihar", "Government PU College Channagiri", "GHS Honnali"]},
    "KA-14": {"city": "Shimoga", "schools": ["Government High School BH Road Shivamogga", "Government Model Primary School Bhadravati", "Government PU College Sagar", "GHS Thirthahalli"]},
    "KA-15": {"city": "Udupi Chikmagalur", "schools": ["Government High School Malpe Udupi", "Government Model Primary School Chikmagalur Main", "Government PU College Karkala", "GHS Kundapura"]},
    "KA-16": {"city": "Hassan", "schools": ["Government High School BM Road Hassan", "Government Model Primary School Holenarasipura", "Government PU College Arsikere", "GHS Sakleshpur"]},
    "KA-17": {"city": "Dakshina Kannada", "schools": ["Government High School Hampankatta Mangaluru", "Government Model Primary School Bantwal", "Government PU College Puttur", "GHS Belthangady"]},
    "KA-18": {"city": "Chitradurga", "schools": ["Government High School Fort View Chitradurga", "Government Model Primary School Challakere", "Government PU College Hiriyur", "GHS Holalkere"]},
    "KA-19": {"city": "Tumkur", "schools": ["Government High School MG Road Tumakuru", "Government Model Primary School Sira", "Government PU College Tiptur", "GHS Madhugiri"]},
    "KA-20": {"city": "Mandya", "schools": ["Government High School Sugar Town Mandya", "Government Model Primary School Maddur", "Government PU College Pandavapura", "GHS Srirangapatna"]},
    "KA-21": {"city": "Mysore", "schools": ["Government High School Saraswathipuram Mysuru", "Government Model Primary School Nanjangud", "Government PU College Hunsur", "GHS Chamrajnagar Road Mysuru"]},
    "KA-22": {"city": "Chamarajanagar", "schools": ["Government High School Chamarajanagar Town", "Government Model Primary School Kollegal", "Government PU College Gundlupet", "GHS Hanur"]},
    "KA-23": {"city": "Bangalore Rural", "schools": ["Government High School Nelamangala", "Government Model Primary School Doddaballapur", "Government PU College Hoskote", "GHS Devanahalli"]},
    "KA-24": {"city": "Bangalore North", "schools": ["Government High School Yelahanka Old Town", "Government PU College & High School Hebbal", "Government Model Primary School Peenya Industrial Area", "Government High School 18th Cross Malleshwaram", "St. Anthony English Medium School RT Nagar", "Government High School Vidyaranyapura", "Government High School Jalahalli West", "Government Model High School Byatarayanapura"]},
    "KA-25": {"city": "Bangalore Central", "schools": ["Government High School Shivajinagar", "Government Model School Shantinagar", "Government PU College Gandhinagar", "GHS Domlur"]},
    "KA-26": {"city": "Bangalore South", "schools": ["Government High School 9th Block Jayanagar", "Government Model Primary School Basavanagudi", "Government PU College Padmanabhanagar", "GHS BTM Layout"]},
    "KA-27": {"city": "Chikkaballapur", "schools": ["Government High School Chikkaballapura Town", "Government Model Primary School Sidlaghatta", "Government PU College Gauribidanur", "GHS Bagepalli"]},
    "KA-28": {"city": "Yadgir", "schools": ["Government High School Station Area Yadgir", "Government Model Primary School Shahapur", "Government PU College Shorapur", "GHS Gurmitkal"]}
}

def generate_full_state_cohort():
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        constituencies = json.load(f)

    all_schools = []
    all_works = []

    for idx, c in enumerate(constituencies):
        c_code = c["code"]
        c_name = c["name"]
        mp_id = c["mp_id"]
        dist_lgd = c["district_lgd_code"]
        cohort = CONSTITUENCY_COHORTS.get(c_code, {"city": c_name, "schools": [f"Government High School {c_name} Main", f"Government Model School {c_name} East", f"Government PU College {c_name}"]})
        
        school_names = cohort["schools"]
        
        # Base coordinates for the district
        base_lat = 12.0 + (idx * 0.22) % 4.5
        base_lon = 74.8 + (idx * 0.15) % 3.2

        c_schools = []
        for s_idx, s_name in enumerate(school_names):
            udise_code = f"29{dist_lgd:03d}{s_idx+1:02d}01"
            is_private = "St." in s_name or "Academy" in s_name or "English School" in s_name
            mgmt = "PRIVATE_UNAIDED" if is_private else "GOVERNMENT"
            
            s_lat = round(base_lat + (s_idx * 0.02), 4)
            s_lon = round(base_lon + (s_idx * 0.02), 4)

            # Generate longitudinal states
            pre_classrooms = 8 + (s_idx * 2)
            # For reflection gap test (e.g. s_idx == 0 for certain seats), classrooms remain unchanged
            is_reflection_gap = (s_idx == 0 and idx % 2 == 0)
            post_classrooms = pre_classrooms if is_reflection_gap else (pre_classrooms + 2)

            states = [
                {
                    "academic_year": "2022-23",
                    "total_enrollment": 180 + s_idx * 30,
                    "girls_enrollment": 90 + s_idx * 15,
                    "boys_enrollment": 90 + s_idx * 15,
                    "total_classrooms": pre_classrooms,
                    "good_condition_classrooms": pre_classrooms - 2,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 3,
                    "functional_boys_toilets": 3,
                    "has_computer_lab": s_idx % 2 == 0,
                    "total_computers": 15 if s_idx % 2 == 0 else 0,
                    "data_freeze_date": "2022-09-30",
                    "data_published_date": "2023-01-15"
                },
                {
                    "academic_year": "2023-24",
                    "total_enrollment": 195 + s_idx * 30,
                    "girls_enrollment": 100 + s_idx * 15,
                    "boys_enrollment": 95 + s_idx * 15,
                    "total_classrooms": post_classrooms,
                    "good_condition_classrooms": post_classrooms - 2,
                    "classrooms_dilapidated": 0,
                    "has_electricity": True,
                    "has_drinking_water": True,
                    "functional_girls_toilets": 4,
                    "functional_boys_toilets": 4,
                    "has_computer_lab": True,
                    "total_computers": 25,
                    "data_freeze_date": "2023-09-30",
                    "data_published_date": "2024-02-10"
                }
            ]

            school_obj = {
                "udise_code": udise_code,
                "name_canonical": s_name,
                "state_lgd_code": 29,
                "district_lgd_code": dist_lgd,
                "block_lgd_code": dist_lgd * 10 + 1,
                "village_name": cohort["city"],
                "latitude": s_lat,
                "longitude": s_lon,
                "management_category": mgmt,
                "operational_status": "OPERATIONAL",
                "states": states
            }
            all_schools.append(school_obj)
            c_schools.append(school_obj)

        # Generate Works for this constituency
        for w_idx, s_obj in enumerate(c_schools):
            work_id = f"PRJ-{c_code}-{2023}-{w_idx+1:04d}"
            s_name = s_obj["name_canonical"]
            
            # Anomaly distribution:
            if w_idx == 0 and idx % 2 == 0:
                # Priority 1: Field Warrant (Ghost Room - Reflection Gap)
                desc = f"Construction of 2 Additional Class rooms at {s_name}"
                cost = 1450000.0
                recom = "2023-03-15"
                sanc = "2023-04-10"
                comp = "2023-05-02"
            elif s_obj["management_category"] == "PRIVATE_UNAIDED":
                # Priority 1: Private Beneficiary Violation
                desc = f"Setup of Smart Computer Lab at {s_name}"
                cost = 1150000.0
                recom = "2023-01-20"
                sanc = "2023-04-18"
                comp = "2023-10-10"
            elif w_idx == 2 and idx % 3 == 0:
                # Priority 2: 19-day speed violation
                desc = f"Construction of 2 Additional Classrooms at {s_name}"
                cost = 1420000.0
                recom = "2023-03-01"
                sanc = "2023-03-25"
                comp = "2023-04-13"
            else:
                # Verified Clean Project
                work_types = [
                    (f"Construction of 2 Additional Classrooms at {s_name}", 1500000.0),
                    (f"Construction of Girls Sanitation Toilet Block at {s_name}", 480000.0),
                    (f"Supply of computers and setup of smart ICT lab at {s_name}", 920000.0),
                    (f"Construction of Compound Boundary Wall at {s_name}", 620000.0)
                ]
                desc, cost = work_types[w_idx % len(work_types)]
                recom = "2023-01-10"
                sanc = "2023-02-15"
                comp = "2023-08-20"

            work_obj = {
                "work_id": work_id,
                "mp_id": mp_id,
                "district_lgd_code": dist_lgd,
                "work_description": desc,
                "sanction_cost": cost,
                "recommendation_date": recom,
                "sanction_date": sanc,
                "completion_date": comp,
                "latitude": s_obj["latitude"],
                "longitude": s_obj["longitude"]
            }
            all_works.append(work_obj)

    # Save to JSON files
    with open(SCHOOLS_OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_schools, f, indent=2)

    with open(WORKS_OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_works, f, indent=2)

    print(f"[SUCCESS] Generated {len(all_schools)} schools and {len(all_works)} works across all 28 Karnataka Parliamentary Constituencies!")

if __name__ == "__main__":
    generate_full_state_cohort()
