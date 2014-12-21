import abc
import hkdfv2
import hkdfv3
import hmac
import hashlib
import math
class HKDF(object):
    __metaclass__ = abc.ABCMeta
    HASH_OUTPUT_SIZE  = 32

    @staticmethod
    def createFor(messageVersion):
        if messageVersion == 2:
            return hkdfv2.HKDFv2()
        elif messageVersion == 3:
            return hkdfv3.HKDFv3()
        else:
            raise Exception("Unknown version: %s " % messageVersion)

    def deriveSecrets(self, inputKeyMaterial, info, outputLength, salt = None):
        salt = salt or [0] * self.__class__.HASH_OUTPUT_SIZE
        prk = self.extract(salt, inputKeyMaterial)
        return self.expand(prk, info, outputLength)

    def extract(self, salt, inputKeyMaterial):
        mac = hmac.new(salt, digestmod=hashlib.sha256)
        mac.update(inputKeyMaterial)
        return mac.digest()

    def expand(self, prk, info, outputSize):

        iterations = int(math.ceil(float(outputSize)/ float(self.__class__.HASH_OUTPUT_SIZE)))
        mixin = bytearray()
        results = bytearray()
        remainingBytes = outputSize

        for i in range(self.getIterationStartOffset(), iterations + self.getIterationStartOffset()):
            mac = hmac.new(prk, digestmod=hashlib.sha256)
            mac.update(mixin)
            if info is not None:
                mac.update(info)
            mac.update(i % 256)

            stepResult = mac.digest()
            stepSize = min(remainingBytes, len(stepResult))
            results.extend(stepResult[:stepSize])
            mixin = stepResult
            remainingBytes -= stepSize

        return str(results)

    @abc.abstractmethod
    def getIterationStartOffset(self):
        return 0