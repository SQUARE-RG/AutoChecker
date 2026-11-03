int main() {
    int sum = 0;
    {
        int i = 0;
        for (i = 0; i < 5; ++i) {
            sum += i;
        }
    }
    return sum;
}
