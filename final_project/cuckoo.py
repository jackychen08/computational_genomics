import hashlib
import math

# Source: https://medium.com/@meeusdylan/implementing-a-cuckoo-filter-in-go-147a5f1f7a9


class Cuckoo:

    def __init__(self, n, fp, max_tries=500, b=4):
        """
        Initializes Cuckoo hash table

        Args:
            n (int): number of elements to store
            fp (float): false positive rate

        Returns:
            Cuckoo hash table
        """
        self.b = b  # number of entries per bucket
        self.f = self.fingerprintLength(4, fp)  # fingerprint length in bits
        self.m = self.nextPower(n / fp * 8)  # number of buckets
        self.fp = fp
        self.table = [[None] * self.b for _ in range(self.m)]
        self.max_tries = max_tries

    def fingerprintLength(self, k, fp):
        """
        Returns fingerprint length in bits
        """
        return max(1, int(math.ceil(math.log(fp, 2) / k)))

    def nextPower(self, i):
        """
        Returns next power of 2 greater than i
        """
        return 1 << int(i - 1).bit_length()

    def fingerprint(self, data):
        """
        Returns fingerprint of data

        Args:
            data (str): data to fingerprint

        Returns:
            int: fingerprint
        """
        hash = hashlib.sha256(data).hexdigest()
        return hash[:self.f]

    def hash(self, data):
        """
        Hashes data using SHA-256

        Args:
            data (str): data to hash

        Returns:
            int: hash value
        """
        h = data.encode('utf-8')
        f = self.fingerprint(h)
        i1 = int(hashlib.sha256(h).hexdigest(), 16) % self.m
        i2 = i1 ^ int(hashlib.sha256(
            f.encode('utf-8')).hexdigest(), 16) % self.m
        return i1, i2, f

    def insert(self, data):
        """
        Inserts key into hash table

        Args:
            key (str): key to insert

        Returns:
            True if key is inserted, False otherwise
        """
        i1, i2, f = self.hash(data)
        for i in range(self.max_tries):
            for i in range(self.b):  # find empty bucket in i1
                if self.table[i1][i] is None:
                    self.table[i1][i] = f
                    return True
            for i in range(self.b):  # find empty bucket in i2
                if self.table[i2][i] is None:
                    self.table[i2][i] = f
                    return True
            else:
                if i % 2 == 0:
                    f, self.table[i1][i] = self.table[i1][i], f
                    i1 = i1 ^ int(hashlib.sha256(
                        f.encode('utf-8')).hexdigest(), 16) % self.m
                else:
                    f, self.table[i2][i] = self.table[i2][i], f
                    i2 = i2 ^ int(hashlib.sha256(
                        f.encode('utf-8')).hexdigest(), 16) % self.m
        # cuckoo data structure is full, TODO: handle resizing
        raise Exception('Reached max size')

    def search(self, key):
        """
        Looks for key in hash table

        Args:
            key (str): key to search for

        Returns:
            True if key is found, False otherwise
        """
        i1, i2, f = self.hash(key)
        b1 = self.table[i1]
        b2 = self.table[i2]
        for i in range(len(self.table[i1])):
            if b1[i] == f:
                return True
        for i in range(len(self.table[i2])):
            if b2[i] == f:
                return True
        return False

    def delete(self, key):
        """
        Deletes key from hash table

        Args:
            key (str): key to delete

        Returns:
            True if key is deleted, False otherwise
        """
        i1, i2, f = self.hash(key)
        b1 = self.table[i1]
        b2 = self.table[i2]
        for i in range(len(self.table[i1])):
            if b1[i] == f:
                b1[i] = None
                return True
        for i in range(len(self.table[i2])):
            if b2[i] == f:
                b2[i] = None
                return True
        return False
