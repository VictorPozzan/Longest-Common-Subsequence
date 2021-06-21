
# Dynamic Programming implementation of LCS problem

import time

class DynamicLCS:
    comp = 0

    def lcs(self, X, Y):
        m = len(X)
        n = len(Y)
        #start = time.time()
        L = [[0]*(n+1) for i in range(m+1)]

        for i in range(m+1):
            for j in range(n+1):
                self.comp = self.comp + 2 # comparasion "i == 0 or j == 0"
                if i == 0 or j == 0:
                    L[i][j] = 0 
                elif X[i-1] == Y[j-1]:
                    self.comp = self.comp + 1 # comparasion "elif X[i-1] == Y[j-1]:"
                    L[i][j] = L[i-1][j-1]+1
                else:
                    self.comp = self.comp + 1 # max(L[i-1][j], L[i][j-1])
                    L[i][j] = max(L[i-1][j], L[i][j-1])

        #end = time.time()
        #executionTime = end - start

        #sub_string = self.findSubString(L, m, n, X, Y)

        return L[m][n], self.comp#sub_string, executionTime

    def findSubString(self, L,  m, n, X, Y):
        index = L[m][n]
        lsc = [""] * (index+1)
        lsc[index] = ""
        i = m
        j = n
        while i > 0 and j > 0:
            if X[i-1] == Y[j-1]:
                lsc[index-1] = X[i-1]
                i -= 1
                j -= 1
                index -= 1
            elif L[i-1][j] > L[i][j-1]:
                i -= 1
            else:
                j -= 1

        return "".join(lsc)
