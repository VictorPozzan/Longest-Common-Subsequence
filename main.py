from Data import Data
from dynamic import DynamicLCS
from bruteforce import BruteForceLCS
from bfrecursive import BFRecursiveLCS

file = "DataBase2/Strings02.txt"
data = Data()
sub_String_A, sub_String_B = data.cleanData(file)

bfrec = BFRecursiveLCS()
size, time, comp, string =  bfrec.lcs(sub_String_A,sub_String_B)

bruteforceLCS = BruteForceLCS()
size, time, comp, string= bruteforceLCS.lcs(sub_String_A, sub_String_B)
    
dynamicLCS = DynamicLCS()
size, time, comp, string = dynamicLCS.lcs(sub_String_A, sub_String_B)


