typedef unsigned int Count;
int main() {
    unsigned int total = 0;
    for (unsigned int count = 0; count < 3; ++count) {
        total += count;
    }
    return static_cast<int>(total);
}
