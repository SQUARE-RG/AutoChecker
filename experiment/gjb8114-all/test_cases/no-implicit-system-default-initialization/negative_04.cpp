int accumulate() {
    static int cache[4]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-2]
    int sum = 0;
    for (int i = 0; i < 4; ++i) {
        sum += cache[i];
    }
    return sum;
}

int main() {
    return accumulate();
}
