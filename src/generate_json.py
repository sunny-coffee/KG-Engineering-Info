import re
import json

sss = '1) as a result of,  2) at the expense of,  3) by means of,  4) by virtue of,  5) by way of,  6) for the sake of,  7) in accordance with / to,  8) in addition to,  9) in back of,  10) in case of,  11) in charge of,  12) in comparison with / to,  13) in common with,  14) in connection with / to,  15) in contact with,  16) in contrast with / to,  17) in exchange for,  18) in favor of,  19) in front of,  20) in lieu of,  21) in (the) light of,  22) in line with,  23) in need of,  24) in place of,  25) in the process of,  26) in reference to,  27) in regard to,  28) in relation to,  29) in respect to,  30) in return for,  31) in search of,  32) in spite of,  33) in terms of,  34) in view of,  35) on account of,  36) on behalf of,  37) on the matter of,  38) on top of,  39) to the left of,  40) to the right of,  41) to the side of,  42) with reference to,  43) with regard to,  44) with respect to,  45) with the exception of'
ss = re.sub(r'\,  \d\d\) ', ',', sss)
s = re.sub(r'\,  \d\) ', ',', ss)
print(s.split(","))
with open('phrasal_preposition.json', 'w') as f:
     json.dump(s.split(","), f)