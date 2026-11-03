const int kGlobalLimit = 100;

int clampValue(int value) {
    if (value > kGlobalLimit) {
        return kGlobalLimit;
    }
    return value;
}
