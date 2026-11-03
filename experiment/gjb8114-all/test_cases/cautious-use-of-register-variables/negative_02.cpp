int sum(int n) {
    int total = 0;
    for (register int i = 0; i < n; ++i) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
        total += i;
    }
    return total;
}

int main() {
    return sum(4);
}
