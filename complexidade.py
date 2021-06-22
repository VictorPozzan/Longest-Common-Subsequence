#COMPLEXIDADE ASSINTÓTICA

    #DYNAMICO
    def lcs(self, X, Y):  # 16n²+68n+9 --> O(n²)
        m = len(X) # +1
        n = len(Y) # +1
        
        L = [[0]*(n+1) for i in range(m+1)] #2n + 4 

        for i in range(m+1): #2n + 3
            for j in range(n+1): # n² + 4n
                if i == 0 or j == 0: # 2*(n²+4n) --> 2n² + 8n
                    L[i][j] = 0  
                elif X[i-1] == Y[j-1]: # 5*(n²+4n) -->5n² + 20n
                    L[i][j] = L[i-1][j-1]+1
                else:
                    L[i][j] = max(L[i-1][j], L[i][j-1]) # 8(n²+4n) --> 8n²+32n

    #FORÇA BRUTA
    def lcs(self, str1, str2): # 22n^2+8n+11
        size = len(str1) - 1 #3
        m = (1 << size) - 1 #3
        maxLen = 0 #1
        longest = "" #1
        step = -1 #1

        for i in range(m, 0, step):  # 2n + 2
            sub = self.getSubString(i, str1) #13n² + 8n
            isSeq = self.isSubSeq(sub, str2)#9n²+6n
            if isSeq: # n
                if len(sub) > maxLen: #2n
                    longest = sub #n
                    maxLen = len(sub) #2n



    def getSubString(self, m, str1): #13n² + 8n
        s = "" # n
        size = len(str1)-1 # 3n
        for i in range(1, size+1): #2n²+3n
            if self.isOne(m, i): #7n² 
                s = str1[size - i] + s #4n²

        return s # n

    def isSubSeq(self, sub, str2): #9n²+6n
        si = 0 #n
        size = len(str2) #2n

        for i in range(size): #2n²+2n
            if sub[si] == str2[i]: #3n² 
                si = si + 1 #2n²
                if si == len(sub): #2n²
                    return True

        return False #n

    def isOne(self, m, i): #7n²
        i = i - 1 # 2n²
        k = m & (1 << i) #3n²
        return k > 0 #2n²
