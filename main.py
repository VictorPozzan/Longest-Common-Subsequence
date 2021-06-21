from Data import Data
from dynamic import DynamicLCS
from bruteforce import BruteForceLCS
from bfrecursive import BFRecursiveLCS

################################################
################################################
vet2 = ["DataBase2/Strings02.txt",
        "DataBase2/Strings03.txt",
        "DataBase2/Strings04.txt",
        "DataBase2/Strings05.txt",
        "DataBase2/Strings06.txt",
        "DataBase2/Strings07.txt",
        "DataBase2/Strings08.txt",
        "DataBase2/Strings09.txt",
        "DataBase2/Strings10.txt",
        "DataBase2/Strings11.txt",
        "DataBase2/Strings12.txt",
        "DataBase2/Strings13.txt",
        "DataBase2/Strings14.txt",
        "DataBase2/Strings15.txt",
        "DataBase2/Strings16.txt",
        "DataBase2/Strings17.txt",
        "DataBase2/Strings18.txt",
        "DataBase2/Strings19.txt",
        "DataBase2/Strings20.txt",
        "DataBase2/Strings21.txt",
        "DataBase2/Strings22.txt",
        "DataBase2/Strings23.txt",
        "DataBase2/Strings24.txt",
        "DataBase2/Strings25.txt",
        "DataBase2/Strings26.txt",
        "DataBase2/Strings27.txt",
        "DataBase2/Strings28.txt",
        "DataBase2/Strings29.txt",
        "DataBase2/Strings30.txt",
        ]
# file_result = open("Results-DataBase2/dynamic_results.txt", "a")

# file_result.write("\n")


# for i in range(len(vet2)):
#     data = Data()
#     file = vet2[i]
#     sub_String_A, sub_String_B = data.cleanData(file)

#     #bruteforceLCS = BruteForceLCS()
#     #size, sub_string, time = bruteforceLCS.lcs(sub_String_A, sub_String_B)
#     dynamicLCS = DynamicLCS()
#     size, sub_string, time = dynamicLCS.lcs(sub_String_A, sub_String_B)

#     file_result.write(str(vet2[i]))
#     file_result.write("\n")
#     file_result.write("size: ")
#     file_result.write(str(size))
#     file_result.write("\n")
#     file_result.write("string found: ")
#     file_result.write(str(sub_string))
#     file_result.write("\n")
#     file_result.write("time: ")
#     file_result.write(str(time))
#     file_result.write("\n")
#     file_result.write("\n")


# file_result.close()

#############################################################
#############################################################



# dynamicLCS = DynamicLCS()
# size, sub_string = dynamicLCS.lcs(sub_String_A, sub_String_B)
# print("dynamic size:"+ str(size))
# print("string is:"+ sub_string)

#bruteforceLCS = BruteForceLCS()
#size, sub_string, time = bruteforceLCS.lcs(sub_String_A, sub_String_B)
#print("brute force size:"+ str(size))
#print("string is:"+ sub_string)


data = Data()
file = "DataBase1/Strings10.txt"
sub_String_A, sub_String_B = data.cleanData(file)
bfrec = BFRecursiveLCS()
sub_string, size, time =  bfrec.lcs(sub_String_A,sub_String_B)

bfrec = BFRecursiveLCS()
sub_string, size, time =  bfrec.lcs(sub_String_A,sub_String_B)


file_result = open("testes.txt", "a")
file_result.write(str(file))
file_result.write("\n")
file_result.write("size: ")
file_result.write(str(size))
file_result.write("\n")
file_result.write("string found: ")
file_result.write(str(sub_string))
file_result.write("\n")
file_result.write("time: ")
file_result.write(str(time))
file_result.write("\n")
file_result.write("\n")
file_result.close()
