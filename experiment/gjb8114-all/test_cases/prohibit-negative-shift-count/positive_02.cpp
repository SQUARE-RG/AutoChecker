int main() {
    int value = 5;
    constexpr int zeroShift = 0;
    int a = value << zeroShift;
    unsigned int shift = 3U;
    int b = value >> shift;
    return a + b;
}
