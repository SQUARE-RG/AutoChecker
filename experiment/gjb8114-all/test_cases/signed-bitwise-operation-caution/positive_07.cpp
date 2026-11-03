int main() {
    unsigned int value = 0x80000000u;
    value >>= 2;
    return static_cast<int>(value);
}
