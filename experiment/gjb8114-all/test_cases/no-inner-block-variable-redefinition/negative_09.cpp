int main() {
    int total = 0;
    int values[] = {1, 2, 3};
    for (int value : values) {
        int total = value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        total += value;
    }
    return total;
}
