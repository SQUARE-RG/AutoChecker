int main() {
    unsigned int flags = 0x10u;
    const unsigned int mask = 0x10u;
    if (0x10u == (flags & mask)) {
        return 1;
    }
    return 0;
}
