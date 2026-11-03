int main() {
    double values[] = {3.14159, 2.71828};
    int ints[2];
    for (int i = 0; i < 2; ++i) {
        ints[i] = values[i]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    }
    return ints[0];
}
