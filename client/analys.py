a = [76438296, 132102489, 132408905, 129863493, 133565471, 130502215, 129415454, 129129352, 126915974, 75891253, 140419879, 131061866, 131003800, 131199014, 141633099, 133576684, 117940121, 79445430, 128142724, 127816182, 120928995, 124598727, 120943223, 132098012, 125043677, 73031827, 123879864, 125458120, 128010047, 118285369, 121015035, 132900351, 131468348, 72567104, 131074562, 117149721, 121300266, 136564462, 115929706, 122093116, 124219178, 72745850, 130208487, 87321354, 117166266, 117797958, 124533723, 133237488, 114223388, 119584697, 73841782, 72676793, 115342343, 130585713, 135551384, 125081858, 119443590, 124096311, 129482864, 128637626, 73553994, 134361504, 134172618, 132692475, 130254399, 153435313, 124233703, 110342589, 73955435, 130748059, 129343727, 119137687, 130719983, 125392006, 124360304, 114898862, 73328548, 129321018, 124966030, 122185621, 137426150, 134330388, 105102630, 127692005, 73071484, 122099374, 121767927, 136223822, 116933721, 126318378, 136299735, 101264430, 72777205, 129396117, 126279327, 121062938, 140044954, 116604468, 114973846, 127033203, 72893708, 130922237, 129630470, 130051943, 131067328, 130886949, 130145483, 142692973, 118156026, 75071843, 134689721, 137595247, 129687965, 130401626, 129853796, 130182153, 129208678, 74377538, 118821968, 125262694, 100050990, 129266533, 129690873, 129842770, 133630063, 72649030, 120010635, 126800900, 123870788, 116802503, 127921738, 128884677, 134113486, 73174873, 117000326, 128274097, 122478803, 122164520, 134715987, 118248802, 129957379, 73473464, 117037005, 122944361, 125801838, 128853303, 120599819, 132629382, 116143110, 74047234, 106429848, 113952343, 124798235, 125487649, 123777395, 126177058, 133150258, 73625822, 129852894, 142926692, 138635777, 129797425, 106737475, 130362547, 130151144, 129777243, 73951085, 74578842, 133379705, 141032268, 119673801, 122302796, 130957998, 128398624, 121590943, 142787615, 74168853, 130906184, 130056520, 132238246, 143490225, 131215557, 118085921, 131537645, 73774064, 127523698, 115131869, 131318149, 122104853, 123095507, 123592311, 124470121, 73221501, 124512924, 119325500, 120375425, 128362663, 145290572, 107041088, 121432859, 73369544, 131690246, 131465531, 129536497, 130248450, 130091122, 130648850, 141895054, 124308228, 72797255, 88501046, 114940481, 133730521, 122881966, 124523832, 118173359, 129936464, 73857644, 130108160, 131185596, 130785023, 132948530, 142661620, 130177509, 114426281, 73234246, 133031632, 118948412, 142675177, 109295420, 129452127, 127806501, 116593811, 73442973, 129706073, 138241922, 110445351, 117461489, 130019034, 120849557, 129671068, 72924378, 120031747, 122010913, 118990922, 128167880, 123068600, 129553185, 120663329, 72875515, 117173426, 121562455, 119118635, 130547512, 123731182, 122959271, 124975377, 74029518, 131842695, 131456015, 130560099, 132339220, 129587025, 130864727, 131900086, 118065003, 73250458, 139228217, 130413912, 131302486, 130944197, 130131644, 129115732, 129216860, 74053060, 139275333, 115470776, 122299144, 125065797, 124388391, 122947124, 123973290, 73920699, 133719400, 129810283, 129656627, 130246183, 130839038, 130201186, 129630806, 73451381, 121702872, 137423377, 112966132, 127239780, 123930157, 133224201, 124987737, 73405838, 131042880, 130642456, 130139891, 132076103, 128423332, 141212418, 124356476, 124076866, 73291288, 72786405, 115635988, 130303147, 133480445, 116942333, 128528490, 126835338, 113500768, 116699910, 73406628, 127121578, 127513098, 129907164, 122087892, 125601335, 118976964, 125173037, 72045223, 129942541, 129060860, 130284636, 130352622, 130117971, 131226086, 130673754, 71424315, 121672130, 135119014, 113397019]

b = {}
for i in range(int(min(a)/1000000), int(max(a)/1000000) + 1):
    b[i] = 0

for x in a:
    b[int(x/1000000)] += 1

print(min(a))
for x in b:
    print(b[x])