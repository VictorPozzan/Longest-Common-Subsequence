from Data import Data
from dynamic import DynamicLCS
from bruteforce import BruteForceLCS

data = Data()
file = "DataBase/Strings25.txt"
sub_String_A, sub_String_B = data.cleanData(file)
print(sub_String_A)
print(sub_String_B)

dynamicLCS = DynamicLCS()
size, sub_string = dynamicLCS.lcs(sub_String_A, sub_String_B)
print("dynamic size:"+ str(size))
print("string is:"+ sub_string)

bruteforceLCS = BruteForceLCS()

size, sub_string = bruteforceLCS.lcs(sub_String_A, sub_String_B)
print("brute force size:"+ str(size))
print("string is:"+ sub_string)
