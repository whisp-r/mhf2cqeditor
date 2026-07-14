import json
import struct
import sys

from collections import defaultdict

if len(sys.argv) != 3:
    print("Usage: python f2questparser.py input.json output.bin")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "rb") as f:
    data = bytearray(f.read())

offset = 0

def seek(pos: int):
    global offset
    offset = pos

def skip(n: int):
    global offset
    offset += n

def valid_ptr(ptr):
    return 0 < ptr <= len(data)

def read_u32() -> int:
    """Read 4-bytes (alter global offset)"""
    global offset
    (val,) = struct.unpack_from("<I", data, offset)
    offset += 4
    return val


# def u32_to_hex(val: int) -> str:
#     return f"{val:08X}"
def u32_to_hex(val: int) -> str:
    return struct.pack('<I', val).hex().upper()

def read_u16() -> int:
    """Read 2-bytes (alter global offset)"""
    global offset
    (val,) = struct.unpack_from("<H", data, offset)
    offset += 2
    return val


# def u16_to_hex(val: int) -> str:
#     return f"{val:04X}"
def u16_to_hex(val: int) -> str:
    return struct.pack('<H', val).hex().upper()


def read_u8() -> int:
    """Read 1-byte (alter global offset)"""
    global offset
    val = data[offset]
    offset += 1
    return val

# def u8_to_hex(val: int) -> str:
    # return f"{val:02X}"
def u8_to_hex(val: int) -> str:
    return struct.pack('<B', val).hex().upper()

def read_f32() -> float:
    """Read 4-bytes (alter global offset)"""
    global offset
    (v,) = struct.unpack_from("<f", data, offset)
    offset += 4
    return v


def f32_to_hex(val: float) -> str:
    return struct.pack("<f", val).hex().upper()

def read_raw(n: int) -> bytearray:
    """Read n bytes from global offset, advance offset, return raw bytes."""
    global offset
    chunk = data[offset:offset + n]
    offset += n
    return chunk

def read_raw_no_offset(n: int) -> bytearray:
    """Read n bytes from global offset, return raw bytes."""
    chunk = data[offset:offset + n]
    return chunk

def raw_to_hex(chunk: bytearray) -> str:
    """Convert bytes to uppercase hex string."""
    return chunk.hex().upper()

def read_str() -> str:
    global offset
    end = data.find(b"\x00", offset)
    if end == -1:
        end = len(data)
    val = data[offset:end].decode("utf-8")
    offset = end + 1  # skip the null terminator
    return val

def auto_dict():
    return defaultdict(auto_dict)

out_dict = auto_dict()

out_dict["headerSection"]["identifier"] = u32_to_hex(read_u32())
questInfoPtr = read_u32()
supplyItemsPtr = read_u32()
questRewardsPtr = read_u32()
fixedInformationPtr = read_u32()
smallMonInfoPtr = read_u32()
bossInformationPtr = read_u32()
gatherInfoPtr = read_u32()
unknownInformationPtr = read_u32()
gatherPointDataPtr = read_u32()
out_dict["headerSection"]["bossSize"] = u16_to_hex(read_u16())
out_dict["headerSection"]["largeMonsterSize%"] = u8_to_hex(read_u8())
out_dict["headerSection"]["fixedValue"] = u8_to_hex(read_u8())
out_dict["headerSection"]["guildPointsReward"] = u32_to_hex(read_u32())
out_dict["headerSection"]["unknown0"] = u32_to_hex(read_u32()) # is apparently 00000000 for gathering - X quests otherwise 0F000000
out_dict["headerSection"]["carvingDifficulty"] = u8_to_hex(read_u8())
out_dict["headerSection"]["arrivalPosition"] = u8_to_hex(read_u8())
out_dict["headerSection"]["supplyState"]["supplyMode"] = u8_to_hex(read_u8())
out_dict["headerSection"]["supplyState"]["supplyConditions"] = u8_to_hex(read_u8())
out_dict["headerSection"]["supplyState"]["conditionQuantity"] = u8_to_hex(read_u8())
out_dict["headerSection"]["difficulty"] = u8_to_hex(read_u8())
skip(2)
out_dict["headerSection"]["smallMonsterChange0"]["changeCondition"] = u32_to_hex(read_u32())
out_dict["headerSection"]["smallMonsterChange0"]["targetCode"] = u16_to_hex(read_u16())
out_dict["headerSection"]["smallMonsterChange0"]["quantity"] = u8_to_hex(read_u8())
out_dict["headerSection"]["smallMonsterChange0"]["sequenceNumber"] = u8_to_hex(read_u8())
out_dict["headerSection"]["smallMonsterChange1"]["changeCondition"] = u32_to_hex(read_u32())
out_dict["headerSection"]["smallMonsterChange1"]["targetCode"] = u16_to_hex(read_u16())
out_dict["headerSection"]["smallMonsterChange1"]["quantity"] = u8_to_hex(read_u8())
out_dict["headerSection"]["smallMonsterChange1"]["sequenceNumber"] = u8_to_hex(read_u8())


seek(questInfoPtr)
out_dict["questInformation"]["questType"] = u8_to_hex(read_u8())
out_dict["questInformation"]["additional"] = u8_to_hex(read_u8())
out_dict["questInformation"]["unknown0"] = u16_to_hex(read_u16()) # 0000 or 0800 afaiik
out_dict["questInformation"]["contractFee"] = u32_to_hex(read_u32())
out_dict["questInformation"]["rewardMoney"] = u32_to_hex(read_u32())
out_dict["questInformation"]["felyneCartLoss"] = u32_to_hex(read_u32())
out_dict["questInformation"]["questTime"] = u32_to_hex(read_u32())
questContentPtr = read_u32()
out_dict["questInformation"]["questNumber"] = u16_to_hex(read_u16())
out_dict["questInformation"]["questStarLevel"] = u8_to_hex(read_u8())
out_dict["questInformation"]["unknown1"] = u8_to_hex(read_u8())
out_dict["questInformation"]["questMap"] = u8_to_hex(read_u8())
out_dict["questInformation"]["specialConditions"] = u8_to_hex(read_u8())
out_dict["questInformation"]["targetCount"] = u8_to_hex(read_u8())
out_dict["questInformation"]["unknown2"] = u8_to_hex(read_u8())
out_dict["questInformation"]["questTarget0"]["questCondition"] = u8_to_hex(read_u8())
out_dict["questInformation"]["questTarget0"]["additionalCondition"] = u16_to_hex(read_u16())
skip(1)
out_dict["questInformation"]["questTarget0"]["targetCode"] = u16_to_hex(read_u16())
out_dict["questInformation"]["questTarget0"]["quantity"] = u16_to_hex(read_u16())
out_dict["questInformation"]["questTarget1"]["questCondition"] = u8_to_hex(read_u8())
out_dict["questInformation"]["questTarget1"]["additionalCondition"] = u16_to_hex(read_u16())
skip(1)
out_dict["questInformation"]["questTarget1"]["targetCode"] = u16_to_hex(read_u16())
out_dict["questInformation"]["questTarget1"]["quantity"] = u16_to_hex(read_u16())
trainingDataPtr = read_u32()

seek(questContentPtr)
commisionContentPtr = read_u32()

seek(commisionContentPtr)
questNamePtr = read_u32()
successDescPtr = read_u32()
failureDescPtr = read_u32()
questDescPtr = read_u32()
mainMonsterPtr = read_u32()
clientPtr = read_u32()

seek(questNamePtr)
out_dict["textCommissionContent"]["questName"] = read_str()
seek(successDescPtr)
out_dict["textCommissionContent"]["successDesc"] = read_str()
seek(failureDescPtr)
out_dict["textCommissionContent"]["failureDesc"] = read_str()
seek(questDescPtr)
out_dict["textCommissionContent"]["questDesc"] = read_str()
seek(mainMonsterPtr)
out_dict["textCommissionContent"]["mainMonster"] = read_str()
seek(clientPtr)
out_dict["textCommissionContent"]["client"] = read_str()


# TODO: training data extraction

seek(supplyItemsPtr)
supplyItemsArr = []
while True:
    item = read_u16()
    if item == 0x0000:
        break
    qty = read_u16()
    supplyItemsArr.append({
        "itemCode": u16_to_hex(item),
        "quantity": u16_to_hex(qty)
    })

out_dict["supplyItems"] = supplyItemsArr


seek(questRewardsPtr)
questRewardsArr = []
saved = offset
while True:
    seek(saved)
    rewardAcquisitionCode = read_u32()
    rewardBlockPtr = read_u32()

    saved = offset
    seek(rewardBlockPtr) # WARN: this is dangerous and can fail
    items = []
    while True:
        temp = read_u16()
        if temp == 0xFFFF: # or temp == 0x0000: seems like probability being 0x0000 does not break it?
            break
        probability = temp
        rewardCode = read_u16()
        quantity = read_u16()
        items.append({
                "probability": u16_to_hex(probability),
                "rewardCode": u16_to_hex(rewardCode),
                "quantity": u16_to_hex(quantity)
        })

    questRewardsArr.append({
        "rewardAcquisitionConditionCode": u32_to_hex(rewardAcquisitionCode),
        "rewards": items
    })
    seek(saved)
    saved2 = offset
    temp = read_u16()
    if temp == 0xFFFF or temp == 0x0000:
        break
    saved = saved2

out_dict["questRewards"] = questRewardsArr

seek(fixedInformationPtr)
out_dict["fixedInformation"]["initialInfoState"] = u32_to_hex(read_u32())
out_dict["fixedInformation"]["unknown0"] = u32_to_hex(read_u32())
out_dict["fixedInformation"]["unknownValue"] = u16_to_hex(read_u16())
out_dict["fixedInformation"]["unknown1"] = raw_to_hex(read_raw(6))
out_dict["fixedInformation"]["endMarker"] = raw_to_hex(read_raw(8))
gap_size = supplyItemsPtr - offset
out_dict["fixedInformation"]["unknown2"] = raw_to_hex(read_raw(gap_size))


def parse_monster_setting(ptr: int) -> tuple:
    seek(ptr)
    areas = []
    saved = offset
    while True:
        seek(saved)
        temp = read_u32()
        if temp == 0x00000000:
            break

        areaCode = temp
        skip(4)
        spawnPtr = read_u32()
        detailsPtr = read_u32()
        saved = offset

        seek(spawnPtr)
        smallMonSpawn0 = read_u32()
        smallMonSpawn1 = read_u32()
        smallMonSpawn2 = read_u32()
        smallMonSpawn3 = read_u32()

        seek(detailsPtr)
        detailsArr = []
        while True:
            temp = read_u16()
            if temp == 0xFFFF:
                break

            code = temp
            state = read_u16()
            quantity = read_u16()
            unknownValue = read_u16()
            unknown0 = read_raw(20)
            orientation = read_u32()
            x = read_f32()
            z = read_f32()
            y = read_f32()
            inQuestSequenceNumber = read_u16()
            skip(2)
            inQuestSize = read_u16()
            inQuestHP = read_u16()
            skip(8)

            detailsArr.append({
                "code" : u16_to_hex(code),
                "state" : u16_to_hex(state),
                "quantity" : u16_to_hex(quantity),
                "unknownValue" : u16_to_hex(unknownValue),
                "unknown0" : raw_to_hex(unknown0),
                "orientation" : u32_to_hex(orientation),
                "X" : f32_to_hex(x),
                "Z" : f32_to_hex(z),
                "Y" : f32_to_hex(y),
                "inQuestSequenceNumber" : u16_to_hex(inQuestSequenceNumber),
                "inQuestSize" : u16_to_hex(inQuestSize),
                "inQuestHP" : u16_to_hex(inQuestHP),
            })

        areas.append({
        "areaCode": u32_to_hex(areaCode),
        "smallMonSpawn0": u32_to_hex(smallMonSpawn0),
        "smallMonSpawn1": u32_to_hex(smallMonSpawn1),
        "smallMonSpawn2": u32_to_hex(smallMonSpawn2),
        "smallMonSpawn3": u32_to_hex(smallMonSpawn3),
        "spawnDetails": detailsArr
        })

    seek(saved)
    skip(4)
    unknownPostAreas = read_raw(12)
    return areas, raw_to_hex(unknownPostAreas)




seek(smallMonInfoPtr)
initSmallMonPtr = read_u32()
smallMonChange1Ptr = read_u32()
smallMonChange2Ptr = read_u32()
if valid_ptr(initSmallMonPtr):
    out_dict["initSmallMon"], out_dict["unknownPostinitSmallMon"] = parse_monster_setting(initSmallMonPtr)
else:
    out_dict["initSmallMon"] = []
    out_dict["unknownPostinitSmallMon"] = "DDDDDDDDDDDDDDD"
if smallMonChange1Ptr != initSmallMonPtr:
    out_dict["changeSmallMon1"], out_dict["unknownPostChangeSmallMon1"] = parse_monster_setting(smallMonChange1Ptr)
else:
    out_dict["changeSmallMon1"] = []
    out_dict["unknownPostChangeSmallMon1"] = "DDDDDDDDDDDDDDD"
if smallMonChange2Ptr != initSmallMonPtr:
    out_dict["changeSmallMon2"], out_dict["unknownPostChangeSmallMon2"] = parse_monster_setting(smallMonChange2Ptr)
else:
    out_dict["changeSmallMon2"] = []
    out_dict["unknownPostChangeSmallMon2"] = "DDDDDDDDDDDDDDD"

seek(bossInformationPtr)
skip(8)
bossSpawnPtr = read_u32()
bossDetailPtr = read_u32()


seek(bossSpawnPtr)
out_dict["bossInfo"]["bossSpawn0"] = u32_to_hex(read_u32())
out_dict["bossInfo"]["bossSpawn1"] = u32_to_hex(read_u32())
out_dict["bossInfo"]["bossSpawn2"] = u32_to_hex(read_u32())
out_dict["bossInfo"]["bossSpawn3"] = u32_to_hex(read_u32())

seek(bossDetailPtr)
bossDetailArr = []
while True:
    temp = read_u16()
    if temp == 0xFFFF:
        break
    code = temp
    state = read_u16()
    quantity = read_u8()
    skip(2)
    spawnArea = read_u8()
    unknown0 = read_raw(20)
    orientation = read_u32()
    x = read_f32()
    z = read_f32()
    y = read_f32()
    inQuestSequenceNumber = read_u16()
    skip(2)
    inQuestSize = read_u16()
    inQuestHP = read_u16()
    skip(8)
    bossDetailArr.append({
        "code": u16_to_hex(code),
        "state": u16_to_hex(state),
        "quantity": u8_to_hex(quantity),
        "spawnArea": u8_to_hex(spawnArea),
        "unknown0": raw_to_hex(unknown0),
        "orientation": u32_to_hex(orientation),
        "X": f32_to_hex(x),
        "Z": f32_to_hex(z),
        "Y": f32_to_hex(y),
        "inQuestSequenceNumber": u16_to_hex(inQuestSequenceNumber),
        "inQuestSize": u16_to_hex(inQuestSize),
        "inQuestHP": u16_to_hex(inQuestHP)
    })

out_dict["bossInfo"]["spawnDetails"] = bossDetailArr


seek(gatherInfoPtr)
gatherInfoArr = []
saved = offset
while True:
    seek(saved)
    temp = read_u32()
    if temp == 0x00000000:
        saved = offset
        continue
    elif not valid_ptr(temp):
        break
    areaSettingPtr = temp
    saved = offset

    seek(areaSettingPtr)
    areaSettingArr = []
    while True:
        temp = read_f32()
        if temp == -1.0: # 0xBF800000 (BE)
            break
        x = temp
        z = read_f32()
        y = read_f32()
        effectiveRange = read_f32()
        gatherCode = read_u16()
        gatherFreqUpperLimit = read_u16()
        gatherType = read_u16()
        gatherFreqLowerLimit = read_u16()

        areaSettingArr.append({
            "X": f32_to_hex(x),
            "Z": f32_to_hex(z),
            "Y": f32_to_hex(y),
            "effectiveRange": f32_to_hex(effectiveRange),
            "gatherCode": u16_to_hex(gatherCode),
            "gatherFreqUpperLimit": u16_to_hex(gatherFreqUpperLimit),
            "gatherType": u16_to_hex(gatherType),
            "gatherFreqLowerLimit": u16_to_hex(gatherFreqLowerLimit)
        })

    gatherInfoArr.append(areaSettingArr)

out_dict["gatherInfo"] = gatherInfoArr

seek(unknownInformationPtr)
skip(4) # FFFF "end marker"
# NOTE: i really dont know what to do with this, its variable, unknown information block, with unknown end
#       what a pain in the ass...
#       the quest dosent seem to care, so ill place the 6 zeros that are usually in most quests, some have a long one:
#       (this one: "000000000000FFFF00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000999900000000000000000000" )
out_dict["unknownPostUnknownInformationBlock"] = "00000000"

seek(gatherPointDataPtr)
gatherPointDataArr = []
saved = offset
while True:
    seek(saved)
    temp = read_u32()
    if not valid_ptr(temp):
        break

    gatherMaterialPtr = temp

    saved = offset
    seek(gatherMaterialPtr)
    codes = []
    while True:
        temp = read_u16()
        if temp == 0xFFFF:
            break
        probability = temp
        itemCode = read_u16()

        codes.append({
            "probability": u16_to_hex(probability),
            "itemCode": u16_to_hex(itemCode)
        })
    gatherPointDataArr.append(codes)

out_dict["gatherPointData"] = gatherPointDataArr


with open(output_file, "w", encoding="utf-8") as f:
    json.dump(out_dict, f, indent=2)
print(f"Saved to {output_file}")
