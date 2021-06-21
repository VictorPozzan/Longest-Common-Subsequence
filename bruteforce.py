
import time


class BruteForceLCS:
    cont = 0

    def lcs(self, str1, str2):
        start = time.time()
        size = len(str1) - 1
        m = (1 << size) - 1
        maxLen = 0
        longest = ""
        step = -1

        for i in range(m, 0, step):  # for decremental
            sub = self.getSubString(i, str1)
            isSeq = self.isSubSeq(sub, str2)

            if isSeq:
                if len(sub) > maxLen:
                    longest = sub
                    maxLen = len(sub)

        end = time.time()
        executionTime = end - start

        return len(longest), longest, executionTime

    def getSubString(self, m, str1):
        s = ""
        size = len(str1)-1
        for i in range(1, size+1):
            if self.isOne(m, i):
                s = str1[size - i] + s

        return s

    def isSubSeq(self, sub, str2):
        si = 0
        size = len(str2)
        #print("sub: ",sub)

        for i in range(size):
            if sub[si] == str2[i]:
                si = si + 1
                if si == len(sub):
                    return True

        return False

    def isOne(self, m, i):
        i = i - 1
        k = m & (1 << i)

        return k > 0
