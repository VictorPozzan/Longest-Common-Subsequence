
# Dynamic Programming implementation of LCS problem

import time

class BFRecursiveLCS:

    def lcs(self, X, Y):
        start = time.time()
        m = len(X)
        n = len(Y)
        
        size = self.lcs_recursive(X, Y, m, n)
        end = time.time()
        executionTime = end - start

        strig = self.slcs(X,Y)

        return strig, size, executionTime

    def lcs_recursive(self ,X, Y, m, n):
        if m == 0 or n == 0:
            return 0;
        elif X[m-1] == Y[n-1]:
            return 1 + self.lcs_recursive(X, Y, m-1, n-1)
        else:
            return max(self.lcs_recursive(X, Y, m, n-1), self.lcs_recursive(X, Y, m-1, n))
    

    def slcs(self, str1, str2):
        # If either string is empty, stop
        if len(str1) == 0 or len(str2) == 0:
            return ""
        
        # First property
        if str1[-1] == str2[-1]:
            return self.slcs(str1[:-1], str2[:-1]) + str1[-1]
            
        # Second proprerty
        # Last of str1 not needed:
        t1 = self.slcs(str1[:-1], str2)
        # Last of str2 is not needed
        t2 = self.slcs(str1, str2[:-1])
        if len(t1) > len(t2):
            return t1
        else:
            return t2
    