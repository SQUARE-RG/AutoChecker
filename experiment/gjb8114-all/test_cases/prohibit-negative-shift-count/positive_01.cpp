int main() {
    unsigned int x = 1U;
    unsigned int y = x << 2;
    int z = 8;
    z = z >> 1;
    return static_cast<int>(y + static_cast<unsigned int>(z));
}
