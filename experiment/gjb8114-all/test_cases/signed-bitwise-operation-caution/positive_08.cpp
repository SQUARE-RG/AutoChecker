int main() {
    unsigned int flags = 0x55u;
    flags ^= 0x0Fu;
    return static_cast<int>(flags);
}
