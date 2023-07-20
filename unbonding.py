from substrateinterface import SubstrateInterface
from pprint import pprint



ws_provider = SubstrateInterface(
    url="wss://public-01.mainnet.thebifrost.io/wss"
)

execute_round = ws_provider.query(
    module='BfcStaking',
    storage_function='CandidateInfo',
    params=['0x03FCBa6842bc2e0538Cc5360328ff3cb72038d43']
)

current_round = ws_provider.query(
    module='BfcStaking',
    storage_function='Round'
)

request = execute_round['request']

## Current Round
cround = current_round['current_round_index']
## Execute Round or None
eround = execute_round['request']['whenExecutable'] if request.value is not None else None
    

# 남은 라운드 확인
rround = eround.value - cround.value if request.value is not None else None


# pprint(eround)
# pprint(rround)


