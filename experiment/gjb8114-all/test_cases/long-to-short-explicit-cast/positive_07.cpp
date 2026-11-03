int main() {
    long sourceValue = 123456L;
    short targetValue = 0;
    targetValue = static_cast<short>(sourceValue);
    return static_cast<int>(targetValue);
}
