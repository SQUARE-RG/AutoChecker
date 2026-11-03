int sum(int a, int b) {
    return a + b;
}

int main() {
    int total = 0;
    for (int i = 0; i < 4; i += 1) {
        total = sum(total, i);
    }
    return total;
}
