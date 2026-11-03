int main() {
    int iValues[3] = {1, 2, 3};
    double dSamples[2] = {1.0, 2.0};
    char cFlags[2] = {'a', 'b'};
    return iValues[0] + static_cast<int>(dSamples[0]) + cFlags[0];
}
