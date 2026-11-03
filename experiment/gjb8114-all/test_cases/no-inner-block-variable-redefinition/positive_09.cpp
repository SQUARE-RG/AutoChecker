int main() {
    int total = 0;
    int values[] = {1, 2, 3};
    for (int value : values) {
        int doubled = value * 2;
        total += doubled;
    }
    return total;
}
