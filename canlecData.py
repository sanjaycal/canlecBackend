candidateResults = [x.split("\t") for x in open("./candidateResults.tsv","r").read().split("\n")]

LIBERAL = "Liberal/Libéral"
CONSERVATIVE = "Conservative/Conservateur"
NDP = "NDP-New Democratic Party/NPD-Nouveau Parti démocratique"
BLOC = "Bloc Québécois/Bloc Québécois"
GREEN = "Green Party/Parti Vert"

PARTIES = [LIBERAL, CONSERVATIVE, NDP, BLOC, GREEN]

PROVINCES = [
    'Alberta',
    'British Columbia/Colombie-Britannique',
    'Manitoba',
    'New Brunswick/Nouveau-Brunswick',
    'Newfoundland and Labrador/Terre-Neuve-et-Labrador',
    'Northwest Territories/Territoires du Nord-Ouest',
    'Nova Scotia/Nouvelle-Écosse',
    'Nunavut',
    'Ontario',
    'Prince Edward Island/Île-du-Prince-Édouard',
    'Quebec/Québec',
    'Saskatchewan',
    'Yukon'
]

PROVINCE = 0
RIDINGNAME = 1
RIDINGNUMBER = 2
CANDIDATENAMEANDPARTY = 3
CANDIDATEVOTES = 6
CANDIDATEPERCENTAGE = 7


def splitNameAndParty(candidatenameandparty: str) -> (str, str):
    try:
        party = PARTIES[[(x in candidatenameandparty) for x in PARTIES].index(True)]
    except:
        party = ""
    name = candidatenameandparty.replace(party, "").strip()
    return party, name

ridingTable = {}
def compute():
    for result in candidateResults[1:-1]:
        if result[RIDINGNUMBER] not in ridingTable.keys():
            ridingTable[result[RIDINGNUMBER]] = {
                "name": result[RIDINGNAME],
                "province": result[PROVINCE],
                "number": int(result[RIDINGNUMBER]),
                "partyResults": {
                    LIBERAL: 0,
                    CONSERVATIVE: 0,
                    NDP: 0,
                    BLOC: 0,
                    GREEN: 0
                }
            }
        party, name = splitNameAndParty(result[CANDIDATENAMEANDPARTY])
        if party in PARTIES:
            try:
                ridingTable[result[RIDINGNUMBER]]["partyResults"][party] = int(result[CANDIDATEVOTES])
            except ValueError as e:
                print(result)
                raise e

compute()

def main():
    for i in list(ridingTable.keys())[:5]:
        print(ridingTable[i])

if __name__ == "__main__":
    main()
