int main() {
    unsigned int total = 0;
    for (unsigned int value = 1; value < 1024; value = value * 2) {
        total += value;
    }
    return static_cast<int>(total);
}
