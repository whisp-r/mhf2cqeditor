import struct
import json
import sys

if len(sys.argv) != 3:
    print("Usage: python f2questparser.py input.json output.bin")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "r") as f:
    data = json.load(f)

buf = bytearray()

symbols = {}  # name -> offset
patches = []  # (target_name, placeholder_offset)


def mark(name: str):
    """Remember the current offset as 'name'."""
    symbols[name] = len(buf)


def w_ptr(target: str):
    """Write a 4-byte placeholder and record where to patch later."""
    patches.append((target, len(buf)))
    buf.extend(b"\xdd\xdd\xdd\xdd")  # placeholder


def align4():
    """Align to 4-bytes"""
    while len(buf) % 4 != 0:
        buf.extend(b"\x00")


def w_str(data: str):
    """Write 4-byte aligned null terminated utf-8 encoded string"""
    align4()
    raw = data.encode("utf-8") + b"\x00"
    buf.extend(raw)
    align4()


def w_hex(data: str):
    """Writes a string of hex characters as bytes"""
    buf.extend(bytes.fromhex(data))


def w_pad(n: int):
    """Writes 0's repeated n times"""
    buf.extend(b"\x00" * n)


w_hex(data["headerSection"]["identifier"])
w_ptr("questInfo")
w_ptr("supplyItems")
w_ptr("questRewards")
w_ptr("fixedInformation")
w_ptr("smallMonInfo")
w_ptr("bossInformation")
w_ptr("gatherInfo")
w_ptr("unknownInformation")
w_ptr("gatherPointData")
w_hex(data["headerSection"]["bossSize"])
w_hex(data["headerSection"]["largeMonsterSize%"])
w_hex(data["headerSection"]["fixedValue"])
w_hex(data["headerSection"]["guildPointsReward"])
w_hex("0F000000")
w_hex(data["headerSection"]["carvingDifficulty"])
w_hex(data["headerSection"]["arrivalPosition"])
w_hex(data["headerSection"]["supplyState"]["supplyMode"])
w_hex(data["headerSection"]["supplyState"]["supplyConditions"])
w_hex(data["headerSection"]["supplyState"]["conditionQuantity"])
w_hex(data["headerSection"]["difficulty"])
w_pad(2)
w_hex(data["headerSection"]["smallMonsterChange0"]["changeCondition"])
w_hex(data["headerSection"]["smallMonsterChange0"]["targetCode"])
w_hex(data["headerSection"]["smallMonsterChange0"]["quantity"])
w_hex(data["headerSection"]["smallMonsterChange0"]["sequenceNumber"])
w_hex(data["headerSection"]["smallMonsterChange1"]["changeCondition"])
w_hex(data["headerSection"]["smallMonsterChange1"]["targetCode"])
w_hex(data["headerSection"]["smallMonsterChange1"]["quantity"])
w_hex(data["headerSection"]["smallMonsterChange1"]["sequenceNumber"])


mark("questInfo")
w_hex(data["questInformation"]["questType"])
w_hex(data["questInformation"]["additional"])
w_hex(data["questInformation"]["unknown0"])
w_hex(data["questInformation"]["contractFee"])
w_hex(data["questInformation"]["rewardMoney"])
w_hex(data["questInformation"]["felyneCartLoss"])
w_hex(data["questInformation"]["questTime"])
w_ptr("questContent")
w_hex(data["questInformation"]["questNumber"])
w_hex(data["questInformation"]["questStarLevel"])
w_hex(data["questInformation"]["unknown1"])
w_hex(data["questInformation"]["questMap"])
w_hex(data["questInformation"]["specialConditions"])
w_hex(data["questInformation"]["targetCount"])
w_hex(data["questInformation"]["unknown2"])
w_hex(data["questInformation"]["questTarget0"]["questCondition"])
w_hex(data["questInformation"]["questTarget0"]["additionalCondition"])
w_pad(1)
w_hex(data["questInformation"]["questTarget0"]["targetCode"])
w_hex(data["questInformation"]["questTarget0"]["quantity"])
w_hex(data["questInformation"]["questTarget1"]["questCondition"])
w_hex(data["questInformation"]["questTarget1"]["additionalCondition"])
w_pad(1)
w_hex(data["questInformation"]["questTarget1"]["targetCode"])
w_hex(data["questInformation"]["questTarget1"]["quantity"])
# w_ptr("trainingData")
w_hex("00000000") # TODO: implement training data


mark("questName")
w_str(data["textCommissionContent"]["questName"])
mark("successDesc")
w_str(data["textCommissionContent"]["successDesc"])
mark("failureDesc")
w_str(data["textCommissionContent"]["failureDesc"])
mark("questDesc")
w_str(data["textCommissionContent"]["questDesc"])
mark("mainMonster")
w_str(data["textCommissionContent"]["mainMonster"])
mark("client")
w_str(data["textCommissionContent"]["client"])


mark("commissionContent")
w_ptr("questName")
w_ptr("successDesc")
w_ptr("failureDesc")
w_ptr("questDesc")
w_ptr("mainMonster")
w_ptr("client")


mark("questContent")
w_ptr("commissionContent")
w_ptr("commissionContent")
w_ptr("commissionContent")
w_ptr("commissionContent")
w_ptr("commissionContent")
w_ptr("commissionContent")
w_ptr("commissionContent")

mark("fixedInformation")
w_hex(data["fixedInformation"]["initialInfoState"])
w_hex(data["fixedInformation"]["unknown0"])
w_hex(data["fixedInformation"]["unknownValue"])
w_hex(data["fixedInformation"]["unknown1"])
w_hex(data["fixedInformation"]["endMarker"])
w_hex(data["fixedInformation"]["unknown2"])


mark("supplyItems")
for item in data["supplyItems"]:
    w_hex(item["itemCode"])
    w_hex(item["quantity"])
w_hex("0000")

w_hex(data["questInformation"]["questNumber"])  # postSupplyQuestNumber


for i, code in enumerate(data["gatheringPointData"]):
    mark(f"gatherCode{i}")
    for material in code:
        w_hex(material["probability"])
        w_hex(material["itemCode"])
    w_hex("FFFF")  # end marker
    align4()

mark("gatherPointData")
for i, code in enumerate(data["gatheringPointData"]):
    w_ptr(f"gatherCode{i}")
# w_hex("FFFFFFFF")  # custom end marker


for i, area in enumerate(data["gatherInfo"]):
    if area:
        mark(f"areaInfo{i}")
        for point in area:
            w_hex(point["X"])
            w_hex(point["Z"])
            w_hex(point["Y"])
            w_hex(point["effectiveRange"])
            w_hex(point["gatherCode"])
            w_hex(point["gatherFreqUpperLimit"])
            w_hex(point["gatherType"])
            w_hex(point["gatherFreqLowerLimit"])
        w_hex("000080BF")
        w_pad(20)

mark("gatherInfo")
for i, area in enumerate(data["gatherInfo"]):
    if area:
        w_ptr(f"areaInfo{i}")
    else:
        w_hex("00000000")  # null ptr
# w_hex("FFFFFFFF")  # custom end marker


for i, rewardType in enumerate(data["questRewards"]):
    mark(f"rewardBlock{i}")
    for reward in rewardType["rewards"]:
        w_hex(reward["probability"])
        w_hex(reward["rewardCode"])
        w_hex(reward["quantity"])
    w_hex("FFFF")
    align4()

mark("questRewards")
for i, rewardType in enumerate(data["questRewards"]):
    w_hex(rewardType["rewardAcquisitionConditionCode"])
    w_ptr(f"rewardBlock{i}")
w_hex("FFFF")
align4()
w_pad(4)


mark("unknownInformation")
w_hex("FFFF")
w_hex(data["unknownPostUnknownInformationBlock"])


# ------------------------- ugh small monster bs


def w_template_small_mon_detail_and_spawn_block(
    jsonMonDataArr: str,
    markSpawnBlock: str,
    markSpawnDetail: str,
):
    """Write details (if any) and then spawn block after it for small monsters"""
    for i, area in enumerate(data[jsonMonDataArr]):
        mark(f"{markSpawnDetail}{i}")
        for detail in area["spawnDetails"]:
            w_hex(detail["code"])
            w_hex(detail["state"])
            w_hex(detail["quantity"])
            w_hex(detail["unknownValue"])
            w_hex(detail["unknown0"])
            w_hex(detail["orientation"])
            w_hex(detail["X"])
            w_hex(detail["Z"])
            w_hex(detail["Y"])
            w_hex(detail["inQuestSequenceNumber"])
            w_pad(2)
            w_hex(detail["inQuestSize"])
            w_hex(detail["inQuestHP"])
            w_pad(8)
        w_hex("FFFF")
        align4()
        w_pad(56)

        # idk if this shouldve been another loop, but i think fixed is fine for now
        mark(f"{markSpawnBlock}{i}")
        w_hex(area["smallMonSpawn0"])
        w_hex(area["smallMonSpawn1"])
        w_hex(area["smallMonSpawn2"])
        w_hex(area["smallMonSpawn3"])


def w_template_small_mon_area_block(
    markMonDataArr: str,
    jsonMonDataArr: str,
    ptrSpawnBlock: str,
    ptrSpawnDetail: str,
    jsonUnknownPostData: str,
):
    """Write the area array for small monster pointer"""
    mark(markMonDataArr)
    for i, area in enumerate(data[jsonMonDataArr]):  # print array of area infos
        w_hex(area["areaCode"])
        w_pad(4)
        w_ptr(f"{ptrSpawnBlock}{i}")
        w_ptr(f"{ptrSpawnDetail}{i}")
    w_hex("00000000")  # custom end marker
    w_hex(data[jsonUnknownPostData])


if data["initSmallMon"]:
    w_template_small_mon_detail_and_spawn_block(
        "initSmallMon", "initSmallMonSpawnBlock", "initSmallMonSpawnDetail"
    )

if data["changeSmallMon1"]:
    w_template_small_mon_detail_and_spawn_block(
        "changeSmallMon1", "changeSmallMon1SpawnBlock", "changeSmallMon1SpawnDetail"
    )

if data["changeSmallMon2"]:
    w_template_small_mon_detail_and_spawn_block(
        "changeSmallMon2", "changeSmallMon2SpawnBlock", "changeSmallMon2SpawnDetail"
    )

# -----------------------------------------------------

if data["initSmallMon"]:
    w_template_small_mon_area_block(
        "initSmallMon",
        "initSmallMon",
        "initSmallMonSpawnBlock",
        "initSmallMonSpawnDetail",
        "unknownPostinitSmallMon",
    )
if data["changeSmallMon1"]:
    w_template_small_mon_area_block(
        "changeSmallMon1",
        "changeSmallMon1",
        "changeSmallMon1SpawnBlock",
        "changeSmallMon1SpawnDetail",
        "unknownPostChangeSmallMon1",
    )
if data["changeSmallMon2"]:
    w_template_small_mon_area_block(
        "changeSmallMon2",
        "changeSmallMon2",
        "changeSmallMon2SpawnBlock",
        "changeSmallMon2SpawnDetail",
        "unknownPostChangeSmallMon2",
    )

# ---------------------------------------------------

# mark("smallMonNULL") 
# w_hex("00000000") # placing it here crashes the game, its placed at the bottom now

mark("smallMonInfo")
if data["initSmallMon"]:
    w_ptr("initSmallMon")
else:
    w_ptr("smallMonNULL")

if data["changeSmallMon1"]:
    w_ptr("changeSmallMon1")
else:
    if data["initSmallMon"]:
        w_ptr("initSmallMon")
    else:
        w_ptr("smallMonNULL")

if data["changeSmallMon2"]:
    w_ptr("changeSmallMon2")
else:
    if data["initSmallMon"]:
        w_ptr("initSmallMon")
    else:
        w_ptr("smallMonNULL")
w_pad(4)


# boss monster

mark("bossDetails")
for detail in data["bossInfo"]["spawnDetails"]:
    w_hex(detail["code"])
    w_hex(detail["state"])
    w_hex(detail["quantity"])
    w_pad(2)
    w_hex(detail["spawnArea"])
    w_pad(20)
    w_hex(detail["orientation"])
    w_hex(detail["X"])
    w_hex(detail["Z"])
    w_hex(detail["Y"])
    w_hex(detail["inQuestSequenceNumber"])
    w_pad(2)
    w_hex(detail["inQuestSize"])
    w_hex(detail["inQuestHP"])
    w_pad(8)
w_hex("FFFF")
align4()
w_pad(56)

mark("bossSpawn")
w_hex(data["bossInfo"]["bossSpawn0"])
w_hex(data["bossInfo"]["bossSpawn1"])
w_hex(data["bossInfo"]["bossSpawn2"])
w_hex(data["bossInfo"]["bossSpawn3"])

mark("bossInformation")
w_hex("0100000000000000")
w_ptr("bossSpawn")
w_ptr("bossDetails")
w_hex("00000000")
w_pad(4)

mark("smallMonNULL")
w_pad(10)

# PATCHING POINTERS
for target, pos in patches:
    if target not in symbols:
        raise KeyError(f"Pointer target '{target}' not found")
    struct.pack_into('<I', buf, pos, symbols[target])

print(f"Writing to {output_file}")
with open(output_file, "wb") as f:
    f.write(buf)
