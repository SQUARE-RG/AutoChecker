double average(int total, int count) {
    double numerator = total;
    double denominator = count;
    return numerator / denominator;
}

int main() {
    return static_cast<int>(average(10, 4));
}
