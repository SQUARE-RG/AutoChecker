int sumRange() {
    int sum = 0;
    for (int i = 6; i > 0; --i) {
        sum += i;
    }
    return sum;
}

int main() {
    return sumRange();
}
