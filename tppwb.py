import requests
import datetime

# Get player results from TPPWB API and convert them to replace the JSON of this app
def tppwb_matches(affiliation_number):
    tppwb_data = tppwb_raw_data(affiliation_number)

    # Sort by ascending order of "Date"
    tppwb_data = sorted(tppwb_data, key=lambda x: x.get("Date", ""))

    matches = []
    for item in tppwb_data:
        if not isinstance(item, dict):
            match = {"genre": "Erreur dict"}
            matches.append(match)
            continue  # skip non-dict items
        match = {
            # Guess the gender from the category
            "genre": "Dames" if item.get("Category").startswith("WD") else "Messieurs",

            "resultat": "Victoire" if item.get("VictoryOrDefeat") == ("V") else "D\u00e9faite",
            
            # Guess the type from the category
            "type_competition": (
                "Tour" if item.get("Category").startswith("MD") or item.get("Category").startswith("WD")
                else "Mixte" if item.get("Category").startswith("MX")
                else "Interclubs"
            ),

            # Guess the phase
            "phase": "Tableau" if item.get("DrawType") == "S" or item.get("TypeTab") == "Tour Final" else "Poule",
            #"phase": item.get("TypeTab"),
            
            # Compute the category of the player
            "classement_joueur": int(item.get("DoublePairValue")) - int(item.get("PartnerDoubleValue")),
            
             "classement_partenaire": item.get("PartnerDoubleValue"),
             "classement_adversaire_1": item.get("OpponentDoubleValue1"),
             "classement_adversaire_2": item.get("OpponentDoubleValue2"),
             "categorie": item.get("Category", "MD100").replace("MD", "P"),
        }
        matches.append(match)

        # Search if there was a change of level in the past
        # TODO
    return matches

# Get player results from TPPWB API based on affiliation number
# https://padel-webapi.tppwb.be/Help/Api/GET-api-Players-GetResultsByPlayer_affiliationNumber_singleOrDouble_dateFrom_dateTo_top_splitVictoriesAndDefeats_splitSinglesAndDoubles
def tppwb_raw_data(affiliation_number):
    # Use the begining of the previous semester as start date for the matches results
    # (Category change will be computed at the end of the semester, based on the last 12 months at most)
    today = datetime.date.today()
    if today.month <= 6:
        # January to June: use July 1st of the previous year
        date_from = datetime.date(today.year - 1, 7, 1)
    else:
        # July to December: use January 1st of the current year
        date_from = datetime.date(today.year, 1, 1)
    

    url = (
        "https://padel-webapi.tppwb.be/api/Players/GetResultsByPlayer"
        f"?affiliationNumber={affiliation_number}"
        f"&singleOrDouble=D"
        f"&splitVictoriesAndDefeats=False"
        f"&splitSinglesAndDoubles=False"
        f"&dateFrom={date_from.strftime('%d%m%Y')}"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Get player info from TPPWB API (Name, FirstName, Rank)
# https://padel-webapi.tppwb.be/Help/Api/GET-api-Players-SearchPlayerForAutoComplete_searchText_isNumFed
def tppwb_player_info(affiliation_number):
    url = (
        "https://padel-webapi.tppwb.be/api/Players/SearchPlayerForAutoComplete"
        f"?searchText={affiliation_number}&isNumFed=true"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
