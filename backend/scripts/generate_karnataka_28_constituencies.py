import os, json, calendar
from datetime import date, timedelta

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
MASTER_FILE = os.path.join(DATA_DIR, "karnataka_constituencies_master.json")
SCHOOLS_OUT_FILE = os.path.join(DATA_DIR, "karnataka_all_schools.json")
WORKS_OUT_FILE = os.path.join(DATA_DIR, "karnataka_all_works.json")

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
    "KA-24": {"city": "Bangalore North", "schools": ["Government High School Yelahanka Old Town", "Government PU College Hebbal", "Government Model Primary School Peenya", "Government High School Malleshwaram"]},
    "KA-25": {"city": "Bangalore Central", "schools": ["Government High School Shivajinagar", "Government Model School Shantinagar", "Government PU College Gandhinagar", "GHS Domlur"]},
    "KA-26": {"city": "Bangalore South", "schools": ["Government High School 9th Block Jayanagar", "Government Model Primary School Basavanagudi", "Government PU College Padmanabhanagar", "GHS BTM Layout"]},
    "KA-27": {"city": "Chikkaballapur", "schools": ["Government High School Chikkaballapura Town", "Government Model Primary School Sidlaghatta", "Government PU College Gauribidanur", "GHS Bagepalli"]},
    "KA-28": {"city": "Yadgir", "schools": ["Government High School Station Area Yadgir", "Government Model Primary School Shahapur", "Government PU College Shorapur", "GHS Gurmitkal"]}
}

# --- DETERMINISTIC LOOKUP TABLES (28 entries, indexed by constituency_idx 0-27) ---

COST_RED      = [1250000,1680000,1050000,2150000,980000,1450000,1120000,1580000,1320000,2280000,1750000,880000,1620000,1180000,2050000,950000,1480000,1260000,1840000,2320000,1020000,1560000,1090000,2180000,1640000,830000,1390000,1080000]
CLAIMED_RED   = [2,3,2,4,2,3,2,3,2,4,3,2,3,2,4,2,3,2,3,4,2,3,2,4,3,2,3,2]
PRE_ROOMS_RED = [8,6,10,5,12,7,9,11,8,6,10,14,8,12,5,9,7,11,8,6,13,7,9,5,10,15,8,11]
ENROLL_RED    = [142,95,210,78,315,124,186,248,167,91,228,342,153,279,82,195,118,261,144,88,305,127,173,76,219,384,138,256]
RY_RED        = [2022,2022,2021,2022,2021,2022,2021,2022,2022,2021,2022,2021,2022,2021,2022,2022,2021,2022,2021,2022,2021,2022,2022,2021,2022,2021,2022,2021]
RM_RED        = [11,10,9,12,10,8,11,9,10,12,11,7,9,10,11,12,9,10,11,8,10,9,12,11,10,9,8,11]
RD_RED        = [5,12,22,3,18,8,14,27,2,19,11,25,7,15,28,4,21,9,16,30,6,23,13,1,17,26,10,20]
SD_RED        = [45,52,38,61,55,48,67,41,58,44,57,50,63,47,56,39,68,53,46,71,42,59,65,37,54,70,43,60]
BD_RED        = [14,16,18,20,15,17,19,21,14,16,18,20,15,17,19,21,14,16,18,20,15,17,19,21,14,16,18,20]

COST_ORA     = [920000,780000,1150000,680000,1050000,850000,980000,1220000,870000,720000,1080000,760000,940000,810000,1190000,890000,1030000,740000,960000,1130000,820000,690000,1010000,900000,1070000,770000,1160000,830000]
SD_ORA_DELAY = [106,82,118,95,130,76,142,88,109,97,125,83,138,91,115,104,127,79,141,96,112,87,133,103,121,93,145,78]
ENROLL_ORA   = [68,145,52,198,41,172,59,223,75,132,48,187,63,156,44,209,71,141,55,194,38,168,66,215,80,127,45,183]
PRE_ORA      = [4,9,3,11,2,8,5,12,4,7,3,10,5,8,2,11,4,7,3,9,2,8,5,12,4,7,3,10]
RY_ORA       = [2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021,2022,2021]
RM_ORA       = [9,11,10,8,12,10,9,7,11,9,10,12,8,11,9,10,7,12,11,8,9,10,12,7,10,11,8,9]
RD_ORA       = [8,14,3,21,12,5,28,17,6,24,10,2,19,11,25,7,15,29,4,18,9,22,13,1,16,27,8,20]

COST_GNA     = [1820000,1650000,2100000,1480000,1950000,1720000,1560000,2250000,1890000,1630000,2050000,1510000,1780000,1670000,2180000,1540000,1920000,1690000,1840000,2130000,1600000,1760000,1470000,2080000,1730000,1590000,2020000,1680000]
COST_GNB     = [650000,820000,580000,920000,740000,860000,690000,780000,610000,890000,720000,550000,810000,670000,950000,630000,880000,750000,840000,590000,770000,640000,910000,700000,560000,830000,760000,620000]
BD_GN        = [65,72,88,54,95,78,110,62,83,70,125,57,98,75,140,60,105,85,68,150,92,67,115,73,80,130,58,100]
SD_GN        = [22,35,18,42,28,15,38,25,31,20,45,12,36,27,19,40,24,33,16,48,30,21,44,17,29,43,14,37]
PRE_GNA      = [10,8,14,7,16,9,12,15,11,8,13,18,10,14,6,11,9,15,10,7,17,9,12,6,13,20,10,14]
PRE_GNB      = [6,9,5,12,4,8,7,10,6,9,5,11,7,8,4,10,6,9,5,11,4,8,7,10,5,9,6,8]
ENROLL_GNA   = [245,178,312,154,408,267,192,356,223,169,289,421,198,334,138,271,162,318,207,145,385,173,228,132,276,462,184,315]
ENROLL_GNB   = [128,196,105,248,89,167,142,215,113,184,98,232,135,175,95,219,120,188,109,237,85,162,147,203,101,178,115,193]

def make_date(year, month, day):
    max_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, max_day))

def make_school_states(pre_rooms, post_rooms, enrollment, idx):
    enroll_post = enrollment + 15 + idx * 3
    girls_pre = int(enrollment * 0.48)
    boys_pre = enrollment - girls_pre
    girls_post = int(enroll_post * 0.48)
    boys_post = enroll_post - girls_post
    has_lab = pre_rooms > 10 or enrollment > 200
    return [
        {
            "academic_year": "2022-23",
            "total_enrollment": enrollment,
            "girls_enrollment": girls_pre,
            "boys_enrollment": boys_pre,
            "total_classrooms": pre_rooms,
            "good_condition_classrooms": max(1, pre_rooms - 2),
            "classrooms_dilapidated": 0,
            "has_electricity": True,
            "has_drinking_water": True,
            "functional_girls_toilets": 2 + (idx % 4),
            "functional_boys_toilets": 2 + ((idx + 1) % 4),
            "has_computer_lab": has_lab,
            "total_computers": 10 + (idx % 20) if has_lab else 0,
            "data_freeze_date": "2022-09-30",
            "data_published_date": "2023-01-15"
        },
        {
            "academic_year": "2023-24",
            "total_enrollment": enroll_post,
            "girls_enrollment": girls_post,
            "boys_enrollment": boys_post,
            "total_classrooms": post_rooms,
            "good_condition_classrooms": max(1, post_rooms - 1),
            "classrooms_dilapidated": 0,
            "has_electricity": True,
            "has_drinking_water": True,
            "functional_girls_toilets": 3 + (idx % 3),
            "functional_boys_toilets": 3 + ((idx + 2) % 3),
            "has_computer_lab": True,
            "total_computers": 20 + (idx % 15),
            "data_freeze_date": "2023-09-30",
            "data_published_date": "2024-02-10"
        }
    ]

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
        cohort = CONSTITUENCY_COHORTS.get(c_code, {"city": c_name, "schools": [f"Government High School {c_name} Main", f"Government Model School {c_name} East", f"Government PU College {c_name}", f"GHS {c_name} West"]})
        school_names = cohort["schools"]
        base_lat = 12.0 + (idx * 0.22) % 4.5
        base_lon = 74.8 + (idx * 0.15) % 3.2
        c_schools = []

        for s_idx, s_name in enumerate(school_names):
            udise_code = f"29{dist_lgd:03d}{s_idx+1:02d}01"
            is_private = ("St." in s_name or "Academy" in s_name or "English School" in s_name or "English Medium" in s_name)
            # Orange PRIVATE: even constituency, s_idx==1
            if s_idx == 1 and idx % 2 == 0 and not is_private:
                is_private = True  # Force private for orange anomaly generation on even constituencies
            mgmt = "PRIVATE_UNAIDED" if is_private else "GOVERNMENT"
            s_lat = round(base_lat + (s_idx * 0.018) + (idx * 0.003), 4)
            s_lon = round(base_lon + (s_idx * 0.015) + (idx * 0.002), 4)

            # Determine pre/post rooms per tier
            if s_idx == 0:  # RED
                pre_r = PRE_ROOMS_RED[idx]
                post_r = pre_r  # 0 delta — ghost work
                enroll = ENROLL_RED[idx]
            elif s_idx == 1:  # ORANGE
                pre_r = PRE_ORA[idx]
                post_r = pre_r  # private won't reflect; delay case: partial
                if idx % 2 == 1:  # DELAY type: sanction delay, work eventually done
                    post_r = pre_r + 1
                enroll = ENROLL_ORA[idx]
            elif s_idx == 2:  # GREEN A
                pre_r = PRE_GNA[idx]
                post_r = pre_r + (2 if idx % 2 == 0 else 3)
                enroll = ENROLL_GNA[idx]
            else:  # GREEN B
                pre_r = PRE_GNB[idx]
                post_r = pre_r + 1
                enroll = ENROLL_GNB[idx]

            states = make_school_states(pre_r, post_r, enroll, idx)
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

        for w_idx, s_obj in enumerate(c_schools):
            work_id = f"PRJ-{c_code}-2023-{w_idx+1:04d}"
            s_name = s_obj["name_canonical"]

            if w_idx == 0:  # RED: reflection gap + velocity violation
                n_rooms = CLAIMED_RED[idx]
                desc = f"Construction of {n_rooms} Additional Class Rooms at {s_name}"
                cost = COST_RED[idx]
                recom = make_date(RY_RED[idx], RM_RED[idx], RD_RED[idx])
                sanction = recom + timedelta(days=SD_RED[idx])
                completion = sanction + timedelta(days=BD_RED[idx])

            elif w_idx == 1:  # ORANGE
                if idx % 2 == 0:  # PRIVATE anomaly
                    desc = f"Setup of Smart Computer Lab at {s_name}"
                    cost = COST_ORA[idx]
                    recom = make_date(RY_ORA[idx], RM_ORA[idx], RD_ORA[idx])
                    sanction = recom + timedelta(days=30 + idx * 2)
                    completion = sanction + timedelta(days=75 + idx * 4)
                else:  # DELAY anomaly
                    n_rooms = 2 + (idx % 2)
                    desc = f"Construction of {n_rooms} Additional Classrooms at {s_name}"
                    cost = COST_ORA[idx]
                    recom = make_date(RY_ORA[idx], RM_ORA[idx], RD_ORA[idx])
                    sanction = recom + timedelta(days=SD_ORA_DELAY[idx])  # >75 days
                    completion = sanction + timedelta(days=90 + idx * 3)

            elif w_idx == 2:  # GREEN A
                if idx % 2 == 0:
                    desc = f"Construction of Girls Toilet Block at {s_name}"
                else:
                    desc = f"Provision of RO Plant and Drinking Water Facility at {s_name}"
                cost = COST_GNA[idx]
                recom = make_date(2021 + (idx % 2), (3 + idx * 2) % 12 + 1, 10 + (idx % 15))
                sanction = recom + timedelta(days=SD_GN[idx])
                completion = sanction + timedelta(days=BD_GN[idx])

            else:  # GREEN B (w_idx==3)
                if idx % 2 == 0:
                    desc = f"Construction of Compound Boundary Wall at {s_name}"
                else:
                    desc = f"Establishment of Smart ICT Computer Lab at {s_name}"
                cost = COST_GNB[idx]
                recom = make_date(2021 + (idx % 2), (5 + idx * 3) % 12 + 1, 12 + (idx % 12))
                sanction = recom + timedelta(days=SD_GN[idx] + 5)
                completion = sanction + timedelta(days=BD_GN[idx] + 10)

            work_obj = {
                "work_id": work_id,
                "mp_id": mp_id,
                "district_lgd_code": dist_lgd,
                "work_description": desc,
                "sanction_cost": float(cost),
                "recommendation_date": str(recom),
                "sanction_date": str(sanction),
                "completion_date": str(completion),
                "latitude": s_obj["latitude"],
                "longitude": s_obj["longitude"]
            }
            all_works.append(work_obj)

    with open(SCHOOLS_OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_schools, f, indent=2)
    with open(WORKS_OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_works, f, indent=2)

    print(f"[SUCCESS] Generated {len(all_schools)} schools and {len(all_works)} works across 28 Karnataka Constituencies")

if __name__ == "__main__":
    generate_full_state_cohort()
