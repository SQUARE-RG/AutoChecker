int main() {
    int iNumbers[3] = {1, 2, 3};
    long lTotal = 0;
    for (int iValue : iNumbers) {
        lTotal += iValue;
    }
    double dWeights[2] = {1.0, 2.0};
    for (double dWeight : dWeights) {
        lTotal += static_cast<long>(dWeight);
    }
    return static_cast<int>(lTotal);
}
