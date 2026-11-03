int main() {
    int total = 0;
    for (int i = 0; i < 3; ++i) {
        total += i;
    }
    if (total > 0) {
        total -= 1;
    }
    return total;
}
